"""Structures used by all run execution strategies."""

from datetime import date, datetime
from typing import Any, Protocol, Optional, Union, Literal, List, Dict

from pydantic import BaseModel, Field, ConfigDict

from epx.core.models.synthpop import SynthPop, SynthPopModel
from epx.core.utils import generate_random_seeds


class FREDArg(BaseModel):
    """A FRED command line argument/ value pair.

    Attributes
    ----------
    flag : str
        The command line flag to pass to FRED, e.g. ``-d``.
    value : str
        The value corresponding to the command line flag, e.g.
        ``/home/results``.
    """

    flag: str
    value: str


class RunRequest(BaseModel):
    """Configuration for an individual run to be executed.

    Attributes
    ----------
    job_id : int
        Unique ID for the job.
    working_dir : str
        Working directory that FRED should be called from. This ensures
        that e.g relative paths within the model code are resolved correctly.
    size : str
        Name of instance size to use for the run.
    fred_version : str
        Version of FRED to use for the run.
    population : SynthPopModel
        The specific locations within a synthetic population that should be
        used for the simulation.
    fred_args : list[FREDArg]
        Command line arguments to be passed to FRED.
    fred_files : list[str]
        The list of all additional .fred files to be appended to the main.fred
    """

    model_config = ConfigDict(populate_by_name=True)

    job_id: int = Field(alias="jobId")
    working_dir: str = Field(alias="workingDir")
    size: str
    fred_version: str = Field(alias="fredVersion")
    population: Optional[SynthPopModel] = None
    fred_args: list[FREDArg] = Field(alias="fredArgs")
    fred_files: list[str] = Field(alias="fredFiles")


class RunInfo(BaseModel):
    """Response object from the /runs endpoint for an individual run.

    Attributes
    ----------
    id : int
        Unique ID for the run.
    jobId : int
        Unique ID for the job.
    userId : int
        Unique ID for each user.
    createdTs : Union[date, str]
        Time when the run  was created .
    run_request : RunRequest
        A copy of the originating request object that the response relates to.
    podPhase: str
        Textual description of the phase of the run.
    containerStatus: Any
        Contains container's info of the run.
    status: Literal["QUEUED", "NOT_STARTED", "RUNNING", "ERROR", "DONE"]
        Textual description of the status of the run.
    userDeleted: bool
        When ``True``, the run was deleted.
    epxClientVersion: str
        Version of exp-client that executes the run.
    """

    id: int
    jobId: int
    userId: int
    createdTs: Union[date, str]
    request: RunRequest
    podPhase: Optional[
        Literal["Pending", "Running", "Succeeded", "Failed", "Unknown"]
    ] = None
    containerStatus: Optional[Any] = None
    status: Literal["QUEUED", "NOT_STARTED", "RUNNING", "ERROR", "DONE"]
    userDeleted: bool
    epxClientVersion: Optional[str] = None


class UserRequests(BaseModel):
    """Response object for a batch of submitted runs associated with a particular Job

    Attributes
    ----------
    runs : list[RunInfo]
        Collection for individual runs associated with a particular Job.
    """

    runs: list[RunInfo]


class _RunError(BaseModel):
    """A run configuration error in FRED Cloud responses.

    Attributes
    ----------
    key : str
        The general category of the error reported by FRED Cloud API, e.g.
        ``size`` for errors related to instance size, or ``fredVersion`` if the
        specified FRED version is not recognized.
    error : str
        Detailed description of the error.
    """

    key: str
    error: str


class RunResponse(BaseModel):
    """Response object from the /runs endpoint for an individual run.

    Attributes
    ----------
    run_id : int
        Unique ID for the run.
    status : Literal["Submitted", "Failed"]
        Textual description of the status of the run.
    errors : list[_RunError], optional
        List of any errors in the run configuration identified by the API
    run_request : _RunRequestPayload
        A copy of the originating request object that the response relates to.
    """

    model_config = ConfigDict(populate_by_name=True)

    run_id: int = Field(alias="runId")
    job_id: int = Field(alias="jobId")
    status: Literal["Submitted", "Failed"]
    errors: Optional[list[_RunError]] = None
    run_request: RunRequest = Field(alias="runRequest")


class RunParameters:
    """Parameters to configure a run.

    Notes
    -----
    In a future version of the client, we plan to support ``program`` being
    specified with type ``Union[Path, list[Path], str, list[str]]``. This will
    make it possible for users to avoid specifying a single entrypoint file
    and instead provide an ordered list of ``.fred`` model files to include.

    Parameters
    ----------
    synth_pop : SynthPop
        Synthetic population to use for the run.
    start_date : Union[date, str], optional
        Simulation start date. If a ``str`` is given, should be in ISO 8601
        format, i.e. ``YYYY-MM-DD``.
    end_date : Union[date, str], optional
        Simulation end date. If a ``str`` is given, should be in ISO 8601
        format, i.e. ``YYYY-MM-DD``.
    model_params : dict[str, Union[float, str]], optional
        Dictionary where the keys are model variable names and the values are
        the corresponding numeric or string values.
    seed : int, optional
        Random number seed for the run. If ``None``, a random seed will be
        generated.
    compile_only : bool, optional
        If ``True``, compile the FRED model, but do not run it. Defaults to
        ``False``.

    Attributes
    ----------
    synth_pop : SynthPop
        Synthetic population to use for the run.
    start_date : date
        Simulation start date.
    end_date : date
        Simulation end date.
    model_params : dict[str, Union[float, str]], optional
        Dictionary where the keys are model variable names and the values are
        the corresponding numeric or string values.
    seed : int
        Random number seed for the run.
    compile_only : bool
        If ``True``, compile the FRED model, but do not run it. Defaults to
        ``False``.
    """

    def __init__(
        self,
        synth_pop: Optional[SynthPop] = None,
        start_date: Optional[Union[date, str]] = None,
        end_date: Optional[Union[date, str]] = None,
        model_params: Optional[dict[str, Union[float, str]]] = None,
        seed: Optional[int] = None,
        compile_only: bool = False,
    ):
        self.synth_pop = synth_pop
        self.start_date = self._normalize_date(start_date) if start_date else None
        self.end_date = self._normalize_date(end_date) if end_date else None
        self.model_params = model_params
        self.seed: int = seed if seed is not None else generate_random_seeds()[0]
        self.compile_only = compile_only

    @staticmethod
    def _normalize_date(d: Union[date, str]) -> date:
        if isinstance(d, date):
            return d
        elif isinstance(d, str):
            return datetime.strptime(d, r"%Y-%m-%d").date()
        else:
            raise TypeError(f"Date format not recognized: {d}")

    def __repr__(self) -> str:
        return (
            f"RunParameters("
            f"synth_pop={self.synth_pop}, "
            f"start_date={self.start_date}, "
            f"end_date={self.end_date}, "
            f"model_params={self.model_params}, "
            f"seed={self.seed}, "
            f"compile_only={self.compile_only}"
            f")"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, RunParameters):
            return False
        if (
            (self.synth_pop == other.synth_pop)
            and (self.start_date == other.start_date)
            and (self.end_date == other.end_date)
            and (self.model_params == other.model_params)
            and (self.seed == other.seed)
            and (self.compile_only == other.compile_only)
        ):
            return True
        return False


class RunParametersModel(BaseModel):
    """Data model facilitating JSON serialization of ``RunParameters`` objects.

    The reason for having both a Pydantic model (this class) and a vanilla
    Python class (``RunParameters``) is that Pydantic models' constructors
    require arguments to be passed as keywords, and their method signatures
    (i.e. those exposed by the builtin ``help`` function) do not explicitly show
    required arguments and types. ``RunParameters`` is part of the public API,
    and these limitations would make Pydantic models awkward for users to
    interact with.
    """

    synth_pop: Optional[SynthPopModel] = None
    start_date: Optional[Union[date, str]]
    end_date: Optional[Union[date, str]]
    sim_model_params: Optional[dict[str, Union[float, str]]] = None
    seed: Optional[int] = None
    compile_only: bool = False

    @staticmethod
    def from_run_parameters(run_parameters: RunParameters) -> "RunParametersModel":
        return RunParametersModel(
            synth_pop=(
                SynthPopModel.from_synth_pop(run_parameters.synth_pop)
                if run_parameters.synth_pop
                else None
            ),
            start_date=run_parameters.start_date,
            end_date=run_parameters.end_date,
            sim_model_params=run_parameters.model_params,
            seed=run_parameters.seed,
            compile_only=run_parameters.compile_only,
        )

    def as_run_parameters(self) -> RunParameters:
        return RunParameters(
            synth_pop=self.synth_pop.as_synth_pop() if self.synth_pop else None,
            start_date=self.start_date,
            end_date=self.end_date,
            model_params=self.sim_model_params,
            seed=self.seed,
            compile_only=self.compile_only,
        )


class AttributeResponse(BaseModel):
    """
    Response object for the API.

    Attributes:
    -----------
    message : str
        A short message about the API response.
    result : str
        Detailed result, including logs or information from the API.
    """

    message: str = Field(..., alias="message")
    result: str = Field(..., alias="result")


class GetStatusUploadAttrRes(BaseModel):
    """
    Response object for the API.

    Attributes:
    -----------
    message : str
        A short message about the API response.
    status : Literal["RUNNING", "DONE"]
        The current status of the upload attribute process.
    """

    message: str = Field(..., alias="message")
    status: Optional[Literal["RUNNING", "DONE"]] = None


class UploadAttributeResponse(BaseModel):
    """
    Response object for the API.

    Attributes:
    -----------
    message : str
        A short message about the API response.
    upload_id : str
        the upload_id to retrieve the status of the uploaded attributes
    """

    message: str = Field(..., alias="message")
    upload_id: str


class MatchAttribute(BaseModel):
    """
    set: str
        The name of the attribute set holding the desired attribute.
    name: str
        The name of the desired attribute.
    version: int
        The version of the desired attribute.
    col: str
        The column header of the input data file holding data to which
        the attribute should be matched.
    """

    set: str
    name: str
    version: int
    col: str


class GenerationMethod(BaseModel):
    """
    type: str
        Assignment method to be used. Valid values at present are "direct"
        and "distribution".
    entity_type: str
        The type of entity for which attribute values will be calculated.
    distribution: dict (optional)
        [Only if type == "distribution"]: Defines the distribution family
        to be used and the data columns to be used in constructing
        distributions.
    match_attributes: MatchAttributeParams
    """

    type: Literal["direct", "distribution"]
    entity_type: str
    match_attributes: List[MatchAttribute]
    distribution: Optional[Dict[str, str]] = None


class AttributeSpec(BaseModel):
    """
    name: str
        The name of the attribute.
    description: str
        description of the attribute.
    data_path: str
        A path to a CSV file containing the data needed to conduct attribute
        assignment.
    """

    name: str
    description: str
    data_path: str
    generation_method: GenerationMethod


class UploadAttributeParams(BaseModel):
    """
    Parameters for uploading attribute data.
    Attributes:
    ----------
    spec : AttributeSpec
        Detailed specifications for the attribute to be uploaded.
    attribute_set : str
        The name of the attribute set (e.g., "epistemix").
    synth_pops : list of str
        A list of synchronized population sets, e.g., ["0"].
    """

    spec: AttributeSpec
    attribute_set: str
    synth_pops: List[str]


class RunExecuteStrategy(Protocol):
    def execute(self) -> RunResponse: ...


class RunExecuteMultipleStrategy(Protocol):
    def execute_all(self) -> List[RunResponse]: ...
