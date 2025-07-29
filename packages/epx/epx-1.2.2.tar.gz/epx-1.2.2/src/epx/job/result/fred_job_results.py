"""Classes for combining and exposing results from multiple runs in a job."""

import io
import logging
from pathlib import Path
import zipfile
from typing import Iterable, TypeAlias, Optional

import pandas as pd
import requests

from epx.core.utils.file import empty_directory
from epx.run.fs import CountType
from epx.run.result.fred_run_results import FREDRunResults

RunResultsWithId: TypeAlias = tuple[int, FREDRunResults]

logger = logging.getLogger(__name__)


class FREDJobResults:
    def __init__(self, run_results_with_ids: Iterable[RunResultsWithId]):
        """Results for all runs in a job.

        Parameters
        ----------
        run_results_with_ids : Iterable[RunResultsWithId]
            Iterable of ``RunResults`` objects that have been associated with
            run ids. These ids are used to associate results with their
            originating runs.

        Notes
        -----
        Calling code is responsible for checking that all ``RunResults`` are
        available, and none are ``None``.
        """

        self._run_results_with_ids = run_results_with_ids

    def state(self, condition: str, state: str, count_type: CountType) -> pd.DataFrame:
        """Return a time series of agent occupancy of a given FRED state.

        Parameters
        ----------
        condition : str
            Name of the FRED model condition containing the target state.
        state : str
            Name of the target state.
        count_type : CountType
            Type of count to report. Options are:
                * `count`, the number of agents occupying the state at the end
                  of each simulated day.
                * `new`, the number of agents entering the state at any time
                  during each simulated day.
                * `cumulative`, the cumulative number of times any agent has
                  entered the state since the beginning of the simulation,
                  reported at the end of each simulated day.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``
                * ``sim_day``
                * The name of the requested count type, i.e. one of ``count``,
                  ``new``, or ``cumulative``.
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].state(condition, state, count_type),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def pop_size(self) -> pd.DataFrame:
        """Return a time series of population size during the run.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``
                * ``sim_day``
                * ``pop_size``.
        """
        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].pop_size(),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def epi_weeks(self) -> pd.DataFrame:
        """Return a mapping from simulation days to epidemiological weeks.

        An epidemiological week, commonly referred to as an epi week or a CDC
        week, is a standardized method of counting weeks to allow for the
        comparison of data year after year.

        By definition, the first epi week of the year ends on the first Saturday
        of January that falls at least four days into the month. Each epi week
        begins on a Sunday and ends on a Saturday.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``
                * ``sim_day``
                * ``epi_week`` with string values in ``YYYY.MM`` format.
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].epi_weeks(),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def dates(self) -> pd.DataFrame:
        """Return a mapping from simulation days to calendar dates.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``
                * ``sim_day``
                * ``sim_date``
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].dates(),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def print_output(self) -> pd.DataFrame:
        """Return a series of messages output by FRED's ``print()`` action.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``
                * ``print_output``
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].print_output().to_frame(),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def csv_output(self, filename: str) -> pd.DataFrame:
        """Return data output by FRED's ``print_csv`` action.

        Parameters
        ----------
        filename : str
            Name of output file as specified in the calls to ``print_csv`` in
            the FRED model code.

        Returns
        -------
        pd.DataFrame
            DataFrame containing data written to ``filename``. Columns are
            ``run_id`` (identifying the specific run that the output
            corresponds to), plus all columns specified in the call to
            ``open_csv`` in the model code.
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].csv_output(filename),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def file_output(self, filename: str) -> pd.DataFrame:
        """Return data output by FRED's ``print_file`` action.

        Parameters
        ----------
        filename : str
            Name of output file as specified in the calls to ``print_file`` in
            the FRED model code.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``, identifying the specific run that the output
                  corresponds to.
                * ``file_output``, a string for entry output by calls to
                  ``print_file`` within the model code.
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].file_output(filename).to_frame(),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def numeric_var(self, varname: str) -> pd.DataFrame:
        """Return a time series of the value of a shared numeric variable.

        Parameters
        ----------
        varname : str
            Name of the shared numeric variable.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``
                * ``sim_day``
                * ``value``
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].numeric_var(varname),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def list_var(self, varname: str, wide=False) -> pd.DataFrame:
        """Return a time series of the value of a shared list variable.

        Parameters
        ----------
        varname : str
            Name of the shared list variable.
        wide : bool, optional
            Return data in 'wide' format where a column is created for each
            list element. Defaults to ``False``.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``
                * ``sim_day``
                * ``list_index``
                * ``value``
            if ``wide=False``. Otherwise:
                * ``run_id``
                * ``sim_day``
                * ``item_0``
                * ``item_1``
                * ...
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].list_var(varname, wide=wide),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def list_table_var(self, varname: str, wide=False) -> pd.DataFrame:
        """Return a time series of the value of a shared list_table variable.

        Parameters
        ----------
        varname : str
            Name of the shared list_table variable.
        wide : bool, optional
            Return data in 'wide' format where a column is created for each
            list element. Defaults to ``False``.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
                * ``run_id``
                * ``sim_day``
                * ``key``
                * ``list_index``
                * ``value``
            if ``wide=False``. Otherwise:
                * ``run_id``
                * ``sim_day``
                * ``key``
                * ``item_0``
                * ``item_1``
                * ...
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].list_table_var(varname, wide=wide),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def table_var(self, varname: str) -> pd.DataFrame:
        """Return a time series of the value of a shared table variable.

        Parameters
        ----------
        varname : str
            Name of the shared table variable.

        Returns
        -------
        pd.DataFrame
                * ``run_id``
                * ``sim_day``
                * ``key``
                * ``value``
        """

        return self._combine_results_across_runs(
            (
                (
                    run_result_with_id[0],
                    run_result_with_id[1].table_var(varname),
                )
                for run_result_with_id in self._run_results_with_ids
            )
        )

    def network(
        self, network_name: str, is_directed: bool = True, sim_day: Optional[int] = None
    ) -> pd.Series:
        """Return a series of network objects from a job.

        Parameters
        ----------
        network_name : str
            Name of the FRED network.
        is_directed : bool, optional
            Whether the network is directed. Defaults to ``True``.
        sim_day : Optional[int], optional
            Simulation day to return the network for. If ``None``, return the
            network for the final simulation day. Defaults to ``None``.

        Returns
        -------
        pd.Series
            Series with the network objects from the runs within the job.
        """

        sim_day_network_map = {
            run_result_with_id[0]: run_result_with_id[1].network(
                network_name, is_directed, sim_day
            )
            for run_result_with_id in self._run_results_with_ids
        }

        return pd.Series(sim_day_network_map, name=network_name)

    @staticmethod
    def _is_output_dir_exists(output_dir: Path) -> bool:
        """Checks whether the specified output directory exists.

        Attributes
        ----------
        output_dir (Path): The path to the output directory.

        Returns
        ----------
        bool: True if the directory exists, False otherwise.
        """

        logger.info(f"checking output dir: {output_dir}")
        if output_dir.is_dir() and any(output_dir.iterdir()):
            return True
        return False

    @classmethod
    def download(cls, job_id: int) -> None:
        """Download job results from a job ID.

        If the result already exists locally, the user will be prompted
        to confirm whether to overwrite the existing data. If the user agrees,
        the existing result will be replaced. Otherwise, the operation is skipped.

        If no existing result is found, the download proceeds as normal.

        Parameters
        ----------
        job_id : int
            Unique ID for the job.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        def confirm_overwrite_output() -> bool:
            answer = input(
                f"Job ID {job_id} output already exists. "
                f"Do you want to overwrite it? (y/N)"
            )
            if answer.lower() in ["y", "yes"]:
                empty_directory(str(output_path))
                return True
            else:
                return False

        def proceed():
            """
            Proceed download job results from S3.
            """
            signedUrls = FREDJob._get_signed_download_url(job_id).urls

            if not len(signedUrls):
                raise RuntimeError(error_message)
            # Download output files from signed url and extract them
            for run_id, url in signedUrls:
                response = requests.get(url[1])
                # Check HTTP response status code and raise exceptions as appropriate
                if not response.ok:
                    raise RuntimeError(error_message)
                # Get file content and extract all on the fly
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    path = FREDJob._get_results_dir(job_id) / str(run_id[1])
                    zip_ref.extractall(str(path))
            print("Download job results successfully.")

        error_message = "Error occurred while downloading job results"
        from epx.job.fred_job import FREDJob

        output_path = FREDJob._get_results_dir(job_id)
        is_output_dir_exists = FREDJobResults._is_output_dir_exists(output_path)

        if not is_output_dir_exists or confirm_overwrite_output():
            proceed()

    @staticmethod
    def _combine_results_across_runs(
        results_dfs_with_ids: Iterable[tuple[int, pd.DataFrame]],
    ) -> pd.DataFrame:

        def proc_result_df(run_id: int, df: pd.DataFrame) -> pd.DataFrame:
            cols = list(df.columns)
            cols.insert(0, "run_id")
            return df.assign(run_id=run_id).loc[:, cols]

        return pd.concat(
            [proc_result_df(run_id, df) for run_id, df in results_dfs_with_ids]
        ).reset_index(drop=True)
