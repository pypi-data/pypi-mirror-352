from pathlib import Path


class JobExistsError(Exception):
    """Raised when a job with a requested ID already exists in the results."""

    def __init__(self, results_dir: Path, job_id: int):
        self.results_dir = results_dir
        self.job_id = job_id
        super().__init__(
            f"A job with ID '{job_id}' already exists in results directory "
            f"'{results_dir}'"
        )


class JobDoesNotExistError(Exception):
    """Raised when a job with a requested ID does not exist in the cache."""

    def __init__(self, job_id: int):
        self.job_id = job_id
        super().__init__(f"No job with ID '{job_id}' exists")


class RunExistsError(Exception):
    """Thrown when user specifies an output_dir that already contains data."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        super().__init__(
            f"Run data already exists in output_dir: {self.output_dir}. "
            "Call Run.delete to delete this data and reuse output_dir."
        )
