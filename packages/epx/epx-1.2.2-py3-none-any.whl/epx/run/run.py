from abc import ABC, abstractmethod
from typing import Any


class Run(ABC):
    """Base class for interacting with runs."""

    @property
    @abstractmethod
    def status(self) -> Any:
        """Get the status of the run."""
        ...

    @property
    @abstractmethod
    def results(self) -> Any:
        """Get the result of the run."""
        ...

    @abstractmethod
    def execute(self) -> None:
        """Execute the run."""
        ...
