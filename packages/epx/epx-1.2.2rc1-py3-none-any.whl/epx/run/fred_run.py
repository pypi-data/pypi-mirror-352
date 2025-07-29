import os
import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from epx.core.types.common import RunExecuteStrategy, RunParameters, RunParametersModel
from epx.core.utils.config import get_job_storage_dir
from epx.core.utils.s3_helpers import (
    get_signed_upload_url,
    upload_file_to_s3_with_presigned_url,
)
from epx.run.fs import FileFinderFactory
from epx.run.result.fred_run_results import FREDRunResults, FREDRunResultsFactory
from epx.run.exec.compat import (
    adapt_params_for_fred_version,
    fred_major_version,
    rescale_seed_to_run_number,
)
from epx.run.exec import (
    RunExecuteCloudStrategy,
)
from epx.run.run import Run
from epx.run.status.fred_run_status import FREDRunStatus, FREDRunStatusFactory

logger = logging.getLogger(__name__)


class _RunModel(BaseModel):
    job_id: int
    fred_files: list[str]
    run_id: int | None
    params: RunParametersModel
    size: str
    fred_version: str

    @staticmethod
    def from_run(run: "FREDRun") -> "_RunModel":
        return _RunModel(
            job_id=run.job_id,
            fred_files=run.fred_files,
            run_id=run.run_id,
            params=RunParametersModel.from_run_parameters(run.params),
            size=run.size,
            fred_version=run.fred_version,
        )

    def as_run(self) -> "FREDRun":
        return FREDRun._from_file(
            job_id=self.job_id,
            fred_files=self.fred_files,
            run_id=self.run_id,
            params=self.params.as_run_parameters(),
            size=self.size,
            fred_version=self.fred_version,
        )


class FREDRun(Run):
    """Client interface for manipulating individual simulation runs.

    Parameters
    ----------
    job_id : int
        Unique ID for the job.
    params : RunParameters
        Parameters to be passed to FRED configuring the run.
    size : str, optional
        Size of cloud instance to use for the run. Defaults to ``hot``.
    fred_version : str, optional
        FRED version to use for the run. Defaults to ``latest``.
    Attributes
    ----------
    job_id : int
        Unique ID for the job.
    _run_id : int, optional
        The runId returned from the API on execute.
    params : RunParameters
        Parameters to be passed to FRED configuring the run.
    size : str, optional
        Size of cloud instance to use for the run.
    fred_version : str, optional
        FRED version to use for the run.
    """

    def __init__(
        self,
        job_id: int,
        params: RunParameters,
        fred_files: list[str],
        size: str = "hot",
        fred_version: str = "latest",
    ):
        self.job_id = job_id
        self._run_id: int | None = None
        self.params = params
        self.size = size
        self.fred_version = fred_version
        self.fred_files = fred_files
        self._exec_strategy: RunExecuteStrategy = RunExecuteCloudStrategy(
            self.job_id,
            adapt_params_for_fred_version(self.params, fred_version),
            self.size,
            self.fred_version,
            fred_files,
        )

    @classmethod
    def from_job_and_run_id(cls, job_id: int, run_id: int) -> "FREDRun":
        """Construct a ``FREDRun`` object from a previously executed simulation run.

        Uses data from the ``_get_run_input_dir`` to obtain a FREDRun object.

        Arguments
        ----------
            job_id (int): The unique ID for the job.
            run_id (int): The unique ID for the run.
        Returns
        ----------
            A `FREDRun` object
        Raises
        ------
        FileNotFoundError
            If no run config is found in storage.
        ValueError
            If the object is not an instance of FREDRun.
        """

        try:
            run_config_file = cls._get_run_input_dir(job_id, run_id) / "run.json"
            with open(run_config_file, "r") as f:
                run_model = _RunModel.model_validate_json(f.read())
                return run_model.as_run()
        except FileNotFoundError as e:
            logger.error(e)
            raise FileNotFoundError(
                f"Run config job={job_id}, run={run_id} missing or removed."
            )
        except ValueError as e:
            logger.error(e)
            raise

    @staticmethod
    def _from_file(
        params: RunParameters,
        job_id: int,
        fred_files: list[str],
        size: str = "hot",
        fred_version: str = "latest",
        run_id: int | None = None,
    ) -> "FREDRun":
        run = FREDRun(job_id, params, fred_files, size, fred_version)
        if run_id is not None:
            run._set_run_id(run_id)
        return run

    @staticmethod
    def _get_run_input_dir(job_id: int, run_id: int) -> Path:
        """Retrieves the input directory for the specified run.

        Arguments
        ----------
            job_id (int): The unique ID for the job.
            run_id (int): The unique ID for the run.
        Returns
        ----------
            Path: The directory path in which to store metadata for the
            run.
        """

        job_input_dir = get_job_storage_dir() / str(job_id) / "inputs"
        return job_input_dir / str(run_id)

    @staticmethod
    def _get_run_output_dir(job_id: int, run_id: int) -> Path:
        """Retrieves the output directory for the specified run.
        s
                Arguments
                ----------
                    job_id (int): The unique ID for the job.
                    run_id (int): The unique ID for the run.
                Returns
                ----------
                    Path: The directory path to the output directory for the run.
        """

        job_output_dir = get_job_storage_dir() / str(job_id) / "results"
        return job_output_dir / str(run_id)

    def _set_run_id(self, run_id: int):
        self._run_id = run_id

    def _init_run_input_storage(self) -> None:
        """Initializes the input storage for the specified run."""
        self._get_run_input_dir(self.job_id, self.run_id).mkdir(
            exist_ok=True, parents=True
        )

    def _write_run_config(self) -> None:
        file_path = self._get_run_input_dir(self.job_id, self.run_id) / "run.json"
        with open(file_path, "w") as f:
            f.write(_RunModel.from_run(self).model_dump_json())

        # Get signed upload url and upload to s3
        url = get_signed_upload_url(
            {
                "jobId": self.job_id,
                "context": "run",
                "type": "config",
                "runId": self.run_id,
            }
        )
        isSuccess = upload_file_to_s3_with_presigned_url(file_path, url)

        if not isSuccess:
            logger.error("Failed to upload the run configuration file to S3.")
        logger.info("Run config saved locally and uploaded successfully.")

    def execute(self) -> None:
        """Execute the simulation run."""
        result = self._exec_strategy.execute()
        self._set_run_id(result.run_id)
        self._init_run_input_storage()
        self._write_run_config()

    def delete(self, interactive=True) -> None:
        """Delete all results data for the run.

        Parameters
        ----------
        interactive : bool, optional
            Whether or not the ``delete`` command should be run interactively.
            When ``True`` (the default), the user will be prompted to confirm
            the deletion of all files in the run directory. When ``False``, no
            confirmation prompt will be given. The latter option is provided to
            support programmatic usage, e.g. to delete the data for all runs in
            a collection of runs.
        """

        output_dir = self._get_run_output_dir(self.job_id, self.run_id)

        def confirm(output_dir: Path) -> bool:
            answer = input(f"Delete contents of {output_dir}? [y/N]")
            if answer.lower() in ["y", "yes"]:
                return True
            else:
                return False

        def proceed():
            for root, dirs, files in os.walk(output_dir, topdown=False):
                for name in files:
                    (Path(root) / name).unlink()
                for name in dirs:
                    (Path(root) / name).rmdir()
            output_dir.rmdir()
            print(f"Run job={self.job_id}, run={self.run_id} deleted successfully.")

        if not interactive or confirm(output_dir):
            proceed()

    @property
    def run_id(self) -> int:
        """Returns the unique ID of the run.

        Raises
        ----------
            AttributeError: If the run ID is missing.
        """
        if self._run_id is None:
            raise AttributeError("Run ID is missing.")
        return self._run_id

    @property
    def status(self) -> FREDRunStatus:
        """Status object for the run."""
        output_dir = self._get_run_output_dir(self.job_id, self.run_id) / "work/outputs"

        return FREDRunStatusFactory(
            FileFinderFactory(output_dir).build(),
            run_id=self.run_id,
        ).build()

    @property
    def results(self) -> Optional[FREDRunResults]:
        """RunResults, optional: Results object for the run. If the results
        directory has not been populated yet, returns ``None``.
        """
        output_dir = self._get_run_output_dir(self.job_id, self.run_id) / "work/outputs"
        if str(self.status) != "DONE":
            return None
        if fred_major_version(self.fred_version) < 11:
            run_number = rescale_seed_to_run_number(self.params.seed)
        else:
            run_number = None
        return FREDRunResultsFactory(
            FileFinderFactory(
                output_dir,
                run_number,
            ).build()
        ).build()

    def __repr__(self) -> str:
        return (
            f"FREDRun("
            f"job_id={self.job_id}, "
            f"run_id={self._run_id}, "
            f"params={self.params}, "
            f"size={self.size}, "
            f"fred_version={self.fred_version}"
            f")"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, FREDRun):
            return False
        if (
            (self.job_id == other.job_id)
            and (self.params == other.params)
            and (self.size == other.size)
            and (self.fred_version == other.fred_version)
        ):
            return True
        return False
