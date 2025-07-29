from abc import ABC, abstractmethod
from typing import Any


class Job(ABC):
    """Base class for interacting with job."""

    @property
    @abstractmethod
    def status(self) -> Any:
        """Get the status of the job."""
        ...

    @property
    @abstractmethod
    def results(self) -> Any:
        """Get the result of the job."""
        ...

    @abstractmethod
    def delete(self) -> Any:
        """Delete the job."""
        ...

    @abstractmethod
    def stop(self) -> Any:
        """Stop the job."""
        ...

    @abstractmethod
    def execute(self) -> None:
        """Execute the job."""
        ...
