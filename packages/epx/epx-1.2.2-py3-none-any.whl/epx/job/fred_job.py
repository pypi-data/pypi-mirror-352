import json
import logging
import os
import io
import shutil
import tempfile
import time
import zipfile
from datetime import date
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import (
    Any,
    Iterable,
    List,
    Literal,
    Optional,
    Union,
)

import pandas as pd
import requests
from pandas._libs.tslibs.nattype import NaTType
from pydantic import BaseModel

from epx.core.cloud.auth import platform_api_headers
from epx.core.errors.api_errors import UnauthorizedUserError, NotFoundError
from epx.core.types.common import RunParameters, UserRequests
from epx.core.types.error_type import ForbiddenResponse, NotFoundResponse
from epx.core.utils.s3_helpers import (
    get_signed_upload_url,
    upload_file_to_s3_with_presigned_url,
)
from epx.job.config.fred_model_config import FREDModelConfig, FREDModelParams
from epx.core.models.synthpop import SynthPopModel
from epx.core.utils.config import (
    get_auth_config_dir,
    get_job_storage_dir,
    get_max_retry_value,
    read_auth_config,
)
from epx.job.job import Job
from epx.job.result.fred_job_results import FREDJobResults
from epx.job.status.fred_job_status import FREDJobStatus
from epx.run.exec.cloud.strategy import RunExecuteMultipleCloudStrategy
from epx.run.fred_run import FREDRun

logger = logging.getLogger(__name__)


class _ModelConfigModel(BaseModel):
    synth_pop: Optional[SynthPopModel] = None
    start_date: Optional[Union[date, str]] = None
    end_date: Optional[Union[date, str]] = None
    params: Optional[FREDModelParams] = None
    seed: Optional[Union[int, tuple[int, ...]]] = None
    n_reps: int = 1

    @staticmethod
    def from_model_config(model_config: "FREDModelConfig") -> "_ModelConfigModel":
        return _ModelConfigModel(
            synth_pop=(
                SynthPopModel.from_synth_pop(model_config.synth_pop)
                if model_config.synth_pop
                else None
            ),
            start_date=model_config.start_date,
            end_date=model_config.end_date,
            params=model_config.model_params,
            seed=model_config.seed,
            n_reps=model_config.n_reps,
        )

    def as_model_config(self) -> "FREDModelConfig":
        return FREDModelConfig(
            synth_pop=self.synth_pop.as_synth_pop() if self.synth_pop else None,
            start_date=self.start_date,
            end_date=self.end_date,
            model_params=self.params,
            seed=self.seed,
            n_reps=self.n_reps,
        )


class _JobModel(BaseModel):
    config: list[_ModelConfigModel]
    tags: list[str]
    job_id: int
    size: str = "hot"
    fred_version: str = "latest"
    n: int = 1
    fred_files: Iterable[Union[Path, str]]
    ref_files: Optional[dict[str, Union[Path, str]]] = None
    run_ids: list[int]

    @staticmethod
    def from_job(job: "FREDJob") -> "_JobModel":
        return _JobModel(
            fred_files=job.fred_files,
            config=[_ModelConfigModel.from_model_config(x) for x in job.config],
            tags=job.tags,
            job_id=job.job_id,
            size=job.size,
            fred_version=job.fred_version,
            ref_files=job.ref_files,
            run_ids=job.run_ids,
        )

    def as_job(self) -> "FREDJob":
        job = FREDJob(
            fred_files=self.fred_files,
            config=[x.as_model_config() for x in self.config],
            tags=self.tags,
            size=self.size,
            fred_version=self.fred_version,
            ref_files=self.ref_files,
            run_ids=self.run_ids,
        )
        if self.job_id is not None:
            job._set_job_id(self.job_id)
        return job


class _DeleteOutcome(BaseModel):
    runId: int
    reason: Literal["Success", "NotFound", "Forbidden", "InternalError"]


class _StopResponse(BaseModel):
    """Response object from the /runs endpoint for deleted SRS runs .

    Attributes
    ----------
    description : str
        The description of the status of the stop
    deletedIds: list[_DeleteOutcome], optional
        List of runIds deleted successfully
    failedIds: list[_DeleteOutcome], optional
        List of runIds deleted unsuccessfully
    """

    description: str
    deletedIds: Optional[list[_DeleteOutcome]] = None
    failedIds: Optional[list[_DeleteOutcome]] = None


class _JobDetails(BaseModel):
    """Details of a single job.

    Attributes
    ----------
    userId : int
        The id of the user
    id: int
        The id of the job
    tags: list[str]
        A list of tags associated with the job
    created: Date
        The date created job
    """

    id: int
    userId: int
    tags: list[str]
    created: datetime


class _GetListJobResponse(BaseModel):
    """Response object from the /jobs endpoint for get list my jobs .

    Attributes
    ----------
    jobs : list[_JobDetails]
        List of job details returned from the API.
    """

    jobs: List[_JobDetails]  # List of jobs


class _GetSignedUploadUrl(BaseModel):
    """Response object of presigned url.

    Attributes
     ----------
    url: str
        The presigned url from s3 for uploading models.
    """

    url: str


class _SignedDownloadUrlInfo(BaseModel):
    """Response object of signed url.

    Attributes
     ----------
    run_id : str
        ID for the run.
    url: str
        The signed url from s3 for downloading job outputs.
    """

    run_id: int
    url: str


class _GetSignedDownloadUrlResponse(BaseModel):
    """Response collection of signed urls from the /job?job_name= endpoint."""

    urls: list[_SignedDownloadUrlInfo]


class _ErrorRun(BaseModel):
    """Represent a failed execution attempt of a run.

    Attributes
     ----------
    runId: int
        A identifier for the retry attempt.
    retry_times: int
        Total number of retry attempts.
    """

    runId: int
    retry_times: int


class _RetryResponse(BaseModel):
    """Response object from the /runs/retry endpoint for retry SRS error runs .

    Attributes
    ----------
    status : str
         A string indicating the status of the request
    runRequestIds: list[int]
        List of submitted runRequestIds
    """

    status: str
    runRequestIds: List[int]


class _RegisterJobResponse(BaseModel):
    """Response object from the /jobs/register endpoint for registering a job execution.

    Attributes
    ----------
    id : int
        Unique ID for the job
    userId: int
        Unique ID for the user
    tags : list[str]
        A list of tags associated with the job
    """

    id: int
    userId: int
    tags: list[str]


class FREDJob(Job):
    def __init__(
        self,
        fred_files: Iterable[Union[Path, str]],
        config: Iterable[FREDModelConfig],
        tags: list[str],
        size: str = "hot",
        fred_version="latest",
        api_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
        run_ids=[],
        ref_files: Optional[dict[str, Union[Path, str]]] = None,
        visualize: Optional[bool] = None,
    ):
        """Client interface for configuring and running collections of
        simulation runs.

        Parameters
        ----------
        fred_files : list[str]
            list of all additional .fred files to be appended to the main.fred. Files are appended in the order they are listed # noqa: E501
        config : Iterable[FREDModelConfig]
            Set of model run configurations to execute.
        tags : list[str]
            A list of tags associated with the job for filtering, searching, or categorization.
        size : str, optional
            Instance size to use for each run in the job, by default "hot".
        fred_version : str, optional
            FRED Simulation Engine version to use for each run in the job,
            by default "latest".
        api_url: endpoint to use for call api - str, optional
        bearer_token: token to add request header when call api - str, optional
        ref_files : dict[str, Path]
            dict with key equal to the local path to a reference file and the value as the destination path # noqa: E501
        """
        self.fred_files = self._validate_fred_files(fred_files)
        self.config = list(config)
        self.tags = self._validate_tags(tags)
        self.size = size
        self.fred_version = fred_version
        self.api_url = api_url
        self.bearer_token = bearer_token
        self.run_ids = run_ids
        self._job_id: int | None = None
        self.visualize = visualize
        self._error_runs: List[_ErrorRun] = []
        self.ref_files = ref_files
        if self.api_url and self.bearer_token:
            self._create_auth_config_file(
                self.api_url,
                self.bearer_token,
            )
        self._runs: tuple[FREDRun, ...] = ()

    def _set_job_id(self, job_id: int):
        self._job_id = job_id

    @property
    def job_id(self) -> int:
        """
        Returns the unique ID of the job.

        Raises:
            AttributeError: If the job hasn't been executed
            and the job ID is unassigned.
        """
        if self._job_id is None:
            raise AttributeError("Job ID is missing, ensure the job has been executed.")
        return self._job_id

    @property
    def run_meta(self) -> pd.DataFrame:
        """Return metadata about each run in the job.

        Returns
        -------
        pd.DataFrame
            A DataFrame with columns:
                * ``run_id``: The ID of the run in the job.
                * ``synth_pop``: The name of the synthetic population used.
                * ``locations``: The locations in the synthetic population.
                * ``start_date``: The start date of the simulation.
                * ``end_date``: The end date of the simulation.
                * ``params``: The model parameters.
                * ``seed``: The random seed used for the run.
                * ``size``: The instance size used for the run.
        """

        def proc_date(date: Optional[date]) -> Union[pd.Timestamp, NaTType]:
            return pd.Timestamp(date) if date is not None else pd.NaT

        if not self._runs and self.run_ids:
            self._runs = tuple(
                FREDRun.from_job_and_run_id(self.job_id, run_id)
                for run_id in self.run_ids
            )
        return pd.DataFrame(
            {
                "run_id": run.run_id,
                "synth_pop": (
                    run.params.synth_pop.name if run.params.synth_pop else None
                ),
                "locations": (
                    run.params.synth_pop.locations if run.params.synth_pop else None
                ),
                "start_date": proc_date(run.params.start_date),
                "end_date": proc_date(run.params.end_date),
                "params": run.params.model_params,
                "seed": run.params.seed,
                "size": run.size,
            }
            for run in self._runs
        )

    @property
    def status(self) -> FREDJobStatus:
        """Current status of the job."""
        if not self._runs and self.run_ids:
            self._runs = tuple(
                FREDRun.from_job_and_run_id(self.job_id, run_id)
                for run_id in self.run_ids
            )
        return FREDJobStatus(self.job_id, ((run.run_id, run) for run in self._runs))

    @property
    def results(self) -> FREDJobResults:
        """Object providing access to simulation results."""

        # Retrieve the path to the results directory
        path = self._get_results_dir(self.job_id)

        # Proceed update storage
        self._update_results_storage(path)

        if not self._runs and self.run_ids:
            self._runs = tuple(
                FREDRun.from_job_and_run_id(self.job_id, run_id)
                for run_id in self.run_ids
            )

        completed_run_results_with_ids = (
            (run.run_id, run.results)
            for run in self._runs
            if run.status.name == "DONE" and run.results is not None
        )

        return FREDJobResults(completed_run_results_with_ids)

    def _update_results_storage(self, path: Path):
        """Update the storage if missing run results is detected

        This function performs the following steps:
        1. Checks if the user's local result storage exists.
           If not, it creates the results directory.
        2. Filter run results that are not stored in the storage from the Job for runs.
        3. Fetches results from S3 and updates the storage.

        Attributes
        ----------
        path : Path
            The directory that stores run results for a specific job.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
            If the results do not exist in S3.
        """

        if not path.exists():
            path.mkdir(parents=True)

        # Retrieve the current run_ids from the results storage.
        current_run_ids_in_storage = self._get_run_id_from_results_storage()
        # Retrieve signed URLs for downloading results
        # where the run status is either 'ERROR' or 'DONE'."
        signed_urls = self._get_signed_download_url(self.job_id).urls
        # Exclude runs from signed_urls that contain the current_run_ids_in_storage
        # for downloading results not found in the storage.
        runs_for_download = [
            obj for obj in signed_urls if obj.run_id not in current_run_ids_in_storage
        ]
        if runs_for_download:
            # To download output files from signed url and extract them
            for run_id, url in runs_for_download:
                response = requests.get(url[1])
                # Check HTTP response status code and raise exceptions as appropriate
                if not response.ok:
                    logger.error(
                        f"Error occured while retrieving results "
                        f"for jobId '{self.job_id}', "
                        f"runId '{str(run_id[1])}'."
                    )
                    raise RuntimeError(
                        "Error occurred while retrieving simulation results."
                    )
                # Get file content and extract all on the fly
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    path = self._get_results_dir(self.job_id) / str(run_id[1])
                    zip_ref.extractall(str(path))

    def execute(
        self,
        time_out: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[int] = None,
    ) -> None:
        """Execute the runs comprising the job.

        Parameters
        ----------
        time_out : int, optional
            The timeout of the job execution (in seconds).
        max_retries : int, optional
            Maximum number of retry attempts.
        backoff_factor : int, optional
            Factor by which the sleep time is increased.
        force_overwrite : bool, optional
            Whether to remove existing files if the output directory contains any.

        Raises
        ------
        RuntimeError:
            If the execution time exceeds timeout or
            If the execution occurs error.
        """

        if time_out and (not isinstance(time_out, int) or time_out < 0):
            logger.error("Invalid timeout value")
            raise ValueError("Invalid timeout value")

        # Register a job execution
        job_id = self._register_job_execution()
        self._set_job_id(job_id)
        self._init_job_storage()

        # Save and upload models
        self._save_and_upload_models_to_s3()

        # Proceed build FREDRun instances
        self._runs = self._build_runs(
            self.config,
            self.job_id,
            self.size,
            self.fred_version,
            self.fred_files,
        )
        logger.info(f"Created {len(self._runs)} runs for jobId {self.job_id}")
        # Start time of the job execution
        start_time = time.time()
        # Create a combined execution strategy
        exec_strategy_all = RunExecuteMultipleCloudStrategy(self._runs)
        results = exec_strategy_all.execute_all(
            max_retries=max_retries, backoff_factor=backoff_factor
        )

        for run, result in zip(self._runs, results):
            run._set_run_id(result.run_id)
            if result.run_id:
                self.run_ids.append(result.run_id)
            run._init_run_input_storage()
            run._write_run_config()

        self._write_job_config()

        max_retries = get_max_retry_value("max_retries_for_run")
        if time_out:
            # Time to wait (in seconds) before checking status again
            idle_time = 3
            update_count = 0
            try:
                update_interval = int(read_auth_config("update_interval"))
            except Exception:
                update_interval = 10
            while True:
                job_status = self.status.name
                status = str(job_status.value)
                if status == "DONE":
                    break
                if status == "ERROR":
                    for runId in job_status.errors:
                        self._add_run_for_retry(runId)
                    # Get errored run with retry_times < max_retries
                    error_runs = self._get_runs_for_retry(max_retries)

                    if len(error_runs) > 0:
                        # Proceed retry
                        runIds = self._retry_runs([run.runId for run in error_runs])
                        self._update_retry_times(runIds)
                    else:
                        logs = self.status.logs
                        log_msg = "; ".join(
                            logs.loc[logs.level == "ERROR"].message.tolist()
                        )
                        raise RuntimeError(
                            f"FREDJob '{self.job_id}' failed with "
                            f"the following error:\n"
                            f"{log_msg}"
                        )
                if time.time() > start_time + (time_out):
                    msg = f"FREDJob did not finish within {time_out / 60} minutes."
                    raise RuntimeError(msg)
                elif update_count >= update_interval:
                    update_count = 0
                    elapsed_time = time.time() - start_time
                    logger.info(
                        f"Job '{self.job_id}' is still processing "
                        f"after {elapsed_time} seconds."
                        f"{job_status.runs_done_count} runs are DONE, "
                        f"{job_status.runs_executing_count} runs are RUNNING "
                        f"and the total runs are {job_status.runs_total_count}."
                    )

                update_count += 1
                time.sleep(idle_time)

    def stop(self) -> str:
        """Stop the running job.

        Users can only stop a job with the job status is RUNNING.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
            If the job status is different "RUNNING"
        """
        params = {}
        if str(self.status) != "RUNNING":
            msg = f"Can not stop the job with status is {self.status}."
            raise RuntimeError(msg)
        if self.run_ids:
            params["id"] = self.run_ids

        endpoint_url = f"{read_auth_config('api-url')}/runs"
        # Patch request to delete SRS runs
        response = requests.patch(
            endpoint_url, headers=platform_api_headers(), params=params
        )
        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.text
        response_body = _StopResponse.model_validate_json(response_payload)

        return response_body.description

    def list_runs(self) -> UserRequests:
        """Retrieve Runs associated with a particular FREDJob.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        endpoint_url = f"{read_auth_config('api-url')}/runs"
        response = requests.get(
            endpoint_url,
            headers=platform_api_headers(),
            params={"job_id": self.job_id},
        )
        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.text
        logger.debug(f"Response payload: {response_payload}")
        response_body = UserRequests.model_validate_json(response_payload)

        return response_body

    def delete(self, interactive=True) -> None:
        """Delete all results data for the job.

        Parameters
        ----------
        interactive : bool, optional
            Whether or not the ``delete`` command should be run interactively.
            When ``True`` (the default), the user will be prompted to confirm
            the deletion of the job results data. When ``False``, no
            confirmation prompt will be given. The latter option is provided to
            support programmatic usage, e.g. to delete the data for all jobs in
            a collection of jobs.
        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        def confirm() -> bool:
            answer = input(f"Delete jobId '{self.job_id}'? [y/N]")
            if answer.lower() in ["y", "yes"]:
                return True
            else:
                return False

        def proceed():
            """
            Delete all run data and metadata storages if any
            """

            # Delete job data in local storage
            path = self._get_job_data_dir(self.job_id)
            try:
                if os.path.exists(path):
                    shutil.rmtree(path)
            except OSError:
                raise RuntimeError(
                    f"An error occurred while deleting jobId {self.job_id} "
                    f"from local storage."
                )

            # Delete job in FRED-DB
            endpoint_url = f"{read_auth_config('api-url')}/jobs/{self.job_id}"
            response = requests.delete(endpoint_url, headers=platform_api_headers())

            # Check HTTP response status code and raise exceptions as appropriate
            if not response.ok:
                if response.status_code == requests.codes.forbidden:
                    raise UnauthorizedUserError(
                        ForbiddenResponse.model_validate_json(response.text).description
                    )
                elif response.status_code == requests.codes.not_found:
                    raise NotFoundError(
                        NotFoundResponse.model_validate_json(response.text).description
                    )
                else:
                    raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
            print(f"FREDJob {self.job_id} deleted successfully.")

        if not interactive or confirm():
            proceed()

    def _write_job_config(self) -> None:
        file_path = self._get_input_dir(self.job_id) / "job.json"
        with open(file_path, "w") as f:
            f.write(_JobModel.from_job(self).model_dump_json(by_alias=True))

        # Get signed upload url to upload the job input
        payload = {"jobId": self.job_id, "context": "job", "type": "config"}
        url = get_signed_upload_url(payload)
        isSuccess = upload_file_to_s3_with_presigned_url(file_path, url)

        if not isSuccess:
            logger.error("Failed to upload the job configuration file to S3.")
        logger.info("Job config saved locally and uploaded successfully.")

    def _get_runs_for_retry(self, max_retry_times=0) -> List[_ErrorRun]:
        """Return a collection of errored runs.

        Attributes
        ----------
        max_retry_times : int
            If a max_retry_times is provided, filter by max_retry_times.

        Returns
        -------
        List[ErrorRun]
            Collection of errored runs.
        """

        if max_retry_times != 0:
            return [
                run for run in self._error_runs if run.retry_times < max_retry_times
            ]
        return self._error_runs

    def _add_run_for_retry(self, runId: int):
        """Add a run for retry.

        Attributes
        ----------
        runId : int
            The id of user request in DB
        """

        for run in self._error_runs:
            if run.runId == runId:
                return
        self._error_runs.append(_ErrorRun(runId=runId, retry_times=0))

    def _update_retry_times(self, runIds: List[int]):
        """Update number of retry_times for runIds in the list

        Attributes
        ----------
        runIds : List[int]
            Submitted userRequestId collection.
        """

        for run in self._error_runs:
            if run.runId in runIds:
                run.retry_times += 1

    def _retry_runs(self, runIds: List[int]) -> List[int]:
        """Retry error runs.

        Users can retry ERROR runs in a specific job .

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        endpoint_url = f"{read_auth_config('api-url')}/runs/retry"

        # Post request to retry SRS runs
        logger.debug(f"RunRetry - Request payload: {runIds}")
        response = requests.post(
            endpoint_url, headers=platform_api_headers(), data={"runRequestIds": runIds}
        )

        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")

        response_payload = response.text
        response_body = _RetryResponse.model_validate_json(response_payload)
        # Return submitted runIds
        return response_body.runRequestIds

    def _save_and_upload_models_to_s3(self) -> None:
        """
        Packages input files into a zip archive, saves it locally and uploads it to S3.

        This function performs the following steps:
        1. Creates a zip file from the job input(`fred_files`, `ref_files`)
           and stores it temporarily.
        2. Saves the zip file to the input storage directory.
        3. Uploads the zip file to `S3`.
        4. Deletes the temporary zip file.

        Raises
        ------
        RuntimeError
            If the `S3` upload fails.
        """
        # Create a tmp folder
        tmp_dir = tempfile.TemporaryDirectory()
        tmp_dir_path = tmp_dir.name
        # Concatenate the fred files
        filenames: List[str] = [str(file) for file in self.fred_files]
        self._concatenate_fred_files(filenames, tmp_dir_path)
        # Copy and rename
        if self.ref_files is not None:
            self._copy_and_rename_file(self.ref_files, tmp_dir_path)
        # Package all files into inputs.zip file
        input_zip_file_path = f"{tmp_dir_path}/inputs.zip"
        with zipfile.ZipFile(input_zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Iterate over all files in the tmp folder
            for root, dirs, files in os.walk(tmp_dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    #  Zip all except inputs.zip
                    if os.path.abspath(file_path) == os.path.abspath(
                        input_zip_file_path
                    ):
                        continue
                    # Add the file to the zip, using a relative path inside the zip
                    zipf.write(file_path, os.path.relpath(file_path, tmp_dir_path))

        # Save the zip file to the input storage directory
        input_dir = self._get_input_dir(self.job_id)
        shutil.copy2(input_zip_file_path, input_dir)

        # Get signed upload url to upload the job input
        payload = {"jobId": self.job_id, "context": "job", "type": "input"}
        url = get_signed_upload_url(payload)
        isSuccess = upload_file_to_s3_with_presigned_url(input_zip_file_path, url)

        # Detele tmp folder
        tmp_dir.cleanup()
        if not isSuccess:
            raise RuntimeError("Error occurred while uploading models")

    def _get_run_id_from_results_storage(self):
        """Locates and parses the run ID from the results storage directory structure"""
        path = self._get_results_dir(self.job_id)
        return [int(folder.name) for folder in Path(path).iterdir() if folder.is_dir()]

    def _init_job_storage(self) -> None:
        """
        Initializes the storage directories for input and output files.

        Ensures that the `inputs` and `results` directories exist within
        the `storage` folder, creating them if they don't already exist.
        """
        storage_path = self._get_job_data_dir(self.job_id)
        input_dir = storage_path / "inputs"
        results_dir = storage_path / "results"

        input_dir.mkdir(parents=True, exist_ok=True)
        results_dir.mkdir(parents=True, exist_ok=True)

    def _register_job_execution(self) -> int:
        """
        Registers a new job execution and returns its unique job ID.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """
        endpoint_url = f"{read_auth_config('api-url')}/jobs/register"
        payload = {"tags": self.tags}
        response = requests.post(
            endpoint_url, headers=platform_api_headers(), json=payload
        )
        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                logger.error(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                logger.error(
                    f"FRED Cloud error code: {response.status_code} : {response.text}"
                )
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")

        response_payload = response.text
        logger.debug(f"Payload: {response.text}")
        response_body = _RegisterJobResponse.model_validate_json(response_payload)
        return response_body.id

    @staticmethod
    def _validate_fred_files(fred_files: Iterable[Path | str]) -> list[Path | str]:
        """Checks if the given `fred_files` paths exist."""

        missing_files = [
            str(fname) for fname in fred_files if not Path(fname).is_file()
        ]
        if missing_files:
            logger.error(f"Could not find fred files: {missing_files}")
            raise FileExistsError(f"Could not find fred files: {missing_files}")
        return list(fred_files)

    @staticmethod
    def _validate_tags(tags: list[str]) -> list[str]:
        """Checks if tags param is valid."""

        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise ValueError("tags must be a list of strings")
        tags = list(dict.fromkeys(tags))  # Remove duplicates
        if not tags:
            raise ValueError("tags must contain at least one item")
        return tags

    @staticmethod
    def _create_auth_config_file(api_url: str, bearer_token: str) -> None:
        config_file = get_auth_config_dir()
        if not config_file.parent.exists():
            config_file.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "api-url": api_url,
            "bearer-token": bearer_token,
        }
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)

    @staticmethod
    def _concatenate_fred_files(filenames: List[str], output_path: str):
        """Concatenate the fred files together."""
        try:
            with open(f"{output_path}/main.fred", "w") as file:
                for index, fname in enumerate(filenames):
                    with open(fname, "r") as infile:
                        file.write(infile.read())
                        if index != len(filenames) - 1:
                            file.write("\n\n")
            logger.info(
                f"Successfully concatenated {len(filenames)} files into main.fred"
            )
        except Exception:
            logger.error("Error occurred while concatenate the FRED files")
            raise RuntimeError("Error occurred while concatenate the FRED files")

    @staticmethod
    def _copy_and_rename_file(
        ref_files: dict[str, Union[Path, str]], output_path: str
    ) -> None:
        """
        Copy and rename reference files, ensuring subdirectories are created.
        Parameters
        ----------
        ref_files : dict[str, Union[Path, str]]
            Dictionary where keys are the file path handles (relative to `output_path`)
            and values are the fully qualified source file paths to be copied.
        output_path : str
            The root directory where the files should be copied to.
        Raises
        ------
        RuntimeError
            If a source file specified in `ref_files` does not exist.
        """
        try:
            missing_files = [
                path for path in ref_files.values() if not Path(path).is_file()
            ]
            if missing_files:
                logger.error(f"Could not find reference files: {missing_files}")
                raise RuntimeError(
                    "Error occurred while copying files. Some files are missing."
                )

            for file in ref_files:
                src_path = ref_files[file]
                temporary_file_destination_path = os.path.join(output_path, file)
                temporary_destination_directory = os.path.dirname(
                    temporary_file_destination_path
                )
                if not os.path.exists(temporary_destination_directory):
                    os.makedirs(temporary_destination_directory)
                shutil.copy(src_path, temporary_file_destination_path)
        except Exception:
            logger.error("Failed to copy and rename files.")
            raise RuntimeError(
                "Error occurred while copying files. Some files are missing."
            )

    @staticmethod
    def _get_job_data_dir(job_id: int) -> Path:
        """Retrieves the storage directory path for a specific job's data.

        Args
        ------
            job_id (int): The unique ID for the job.
        Returns
        ------
            Path: The directory path for storing the job's data.
        """
        return get_job_storage_dir() / str(job_id)

    @staticmethod
    def _get_input_dir(job_id: int) -> Path:
        """Retrieves the input data directory for a specific job.

        Args
        ------
            job_id (int): The unique ID for the job.
        Returns
        ------
            Path: The path to the 'inputs' directory for the specified job.
        """
        return FREDJob._get_job_data_dir(job_id) / "inputs"

    @staticmethod
    def _get_results_dir(job_id: int) -> Path:
        """Retrieves the output data directory for a specific job.

        Args
        ------
            job_id (int): The unique ID for the job.
        Returns
        ------
            Path: The path to the 'results' directory for the specified job.
        """
        return FREDJob._get_job_data_dir(job_id) / "results"

    @staticmethod
    def _get_signed_download_url(job_id: int) -> _GetSignedDownloadUrlResponse:
        """Request to FRED Cloud API to get signed url for downloading job results.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        endpoint_url = f"{read_auth_config('api-url')}/jobs/results"

        response = requests.get(
            endpoint_url,
            headers=platform_api_headers(),
            params={"job_id": job_id},
        )

        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")

        response_payload = response.text
        logger.debug(f"Payload: {response.text}")
        response_body = _GetSignedDownloadUrlResponse.model_validate_json(
            response_payload
        )
        return response_body

    @classmethod
    def _build_runs(
        cls,
        config: Iterable[FREDModelConfig],
        job_id: int,
        size: str,
        fred_version: str,
        fred_files: list[Path | str],
    ) -> tuple[FREDRun, ...]:
        def disaggregate_model_config(
            model_config: FREDModelConfig,
        ) -> list[FREDModelConfig]:
            """Convert model config representing multiple realizations into a
            list of model configs each representing a single realization.
            """

            if model_config.n_reps == 1:
                return [model_config]
            if isinstance(model_config.seed, Iterable):
                seeds: list[Optional[int]] = list(model_config.seed)
            else:
                seeds = [None for _ in range(model_config.n_reps)]
            return [
                FREDModelConfig(
                    synth_pop=model_config.synth_pop,
                    start_date=model_config.start_date,
                    end_date=model_config.end_date,
                    model_params=model_config.model_params,
                    seed=seeds[i],
                    n_reps=1,
                )
                for i, _ in enumerate(range(model_config.n_reps))
            ]

        def validate_singular_seed(
            seed: Optional[Union[int, Iterable[int]]],
        ) -> Optional[int]:
            if seed is not None and not isinstance(seed, int):
                raise ValueError("Seed must be an integer if n_reps=1")
            return seed

        return tuple(
            FREDRun(
                params=RunParameters(
                    synth_pop=model_config.synth_pop,
                    start_date=model_config.start_date,
                    end_date=model_config.end_date,
                    model_params=model_config.model_params,
                    seed=validate_singular_seed(model_config.seed),
                ),
                size=size,
                fred_version=fred_version,
                job_id=job_id,
                fred_files=[str(path) for path in fred_files],
            )
            for run_id, model_config in enumerate(
                chain(
                    *[
                        disaggregate_model_config(model_config)
                        for model_config in config
                    ]
                )
            )
        )

    @classmethod
    def get_job_by_id(cls, job_id: int) -> Optional["FREDJob"]:
        """Retrieves a locally stored job configuration by its job ID.

        Args
        ------
        job_id (int): The unique ID of the job.

        Raises
        ------
        ValueError
            If the job configuration is not a valid FREDJob instance.
        """

        try:
            job_config_file = cls._get_input_dir(job_id) / "job.json"
            if job_config_file.exists():
                with open(job_config_file, "r") as f:
                    return _JobModel.model_validate_json(f.read()).as_job()
            else:
                logger.warning(f"job_config_file [{job_config_file}]does not exist")
                return None
        except ValueError as e:
            logger.error(e)
            raise

    @classmethod
    def get_jobs_by_tags(
        cls,
        tags: Optional[list[str]] = None,
        start_date: Optional[Union[str, "datetime"]] = None,
        end_date: Optional[Union[str, "datetime"]] = None,
    ) -> _GetListJobResponse:
        """Lists the my jobs filtered by tags, start_date, and end_date.

        Parameters
        ----------
        tags: Optional[list[str]], optional
            Filter jobs by tags.
        start_date: Optional[Union[str, datetime]], optional
            Filter jobs starting after this date.
        end_date: Optional[Union[str, datetime]], optional
            Filter jobs ending before this date.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        params: dict[str, Any] = {}
        # Make sure tags is a list
        if isinstance(tags, str):
            tags = [tags]

        if tags:
            params["tags"] = tags

        # Check and validate start_date by format
        if start_date:
            if isinstance(start_date, str):
                try:
                    temp_start_date = datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    raise RuntimeError(
                        f"start_date must be in format YYYY-MM-DD, {start_date}"
                    )
            else:
                temp_start_date = start_date
            params["startDate"] = temp_start_date.strftime("%Y-%m-%d")

        # Check and validate end_date by format
        if end_date:
            if isinstance(end_date, str):
                try:
                    temp_end_date = datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    raise RuntimeError(
                        f"end_date must be in format YYYY-MM-DD, {end_date}"
                    )
            else:
                temp_end_date = end_date
            params["endDate"] = temp_end_date.strftime("%Y-%m-%d")

        endpoint_url = f"{read_auth_config('api-url')}/jobs/me"

        # Patch request to get list my jobs
        response = requests.get(
            endpoint_url, headers=platform_api_headers(), params=params
        )
        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.json()
        response_body = _GetListJobResponse.model_validate(response_payload)

        return response_body

    @classmethod
    def get_latest_job(
        cls,
        tags: Optional[list[str]] = None,
    ) -> Optional["FREDJob"]:
        """Retrieves the most recently registered or executed job.

        Parameters
        ----------
        tags: Optional[list[str]], optional
            Filter a job that match the given tags

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        params: dict[str, Any] = {}
        if tags:
            params["tags"] = tags

        params["latest"] = "true"
        endpoint_url = f"{read_auth_config('api-url')}/jobs"

        # Get request to get my latest job
        response = requests.get(
            endpoint_url, headers=platform_api_headers(), params=params
        )
        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.text
        response_body = _JobDetails.model_validate_json(response_payload)

        if not response_body:
            print("No Job submitted")
        job_id = response_body.id
        return FREDJob.get_job_by_id(job_id)

    def __repr__(self) -> str:
        return (
            f"FREDJob("
            f"fred_files={self.fred_files}, "
            f"config={self.config}, "
            f"tags={self.tags}, "
            f"job_id={self._job_id}, "
            f"size={self.size}, "
            f"fred_version={self.fred_version}, "
            f"ref_files={self.ref_files}, "
            f"run_ids={self.run_ids}, "
            f"{f'visualize={self.visualize}' if self.visualize is not None else ''}"
            f")"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FREDJob):
            return False

        is_match = (
            self.config == other.config
            and self.size == other.size
            and self.fred_version == other.fred_version
        )
        if self.job_id is not None:
            return self.job_id == other.job_id and is_match
        return is_match
