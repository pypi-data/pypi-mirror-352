from dataclasses import dataclass
from datetime import date
from typing import (
    Iterable,
    Optional,
    TypeAlias,
    Union,
)

from epx.core.models.synthpop import SynthPop


FREDModelParams: TypeAlias = dict[str, Union[float, str]]


@dataclass
class FREDModelConfig:
    """Configuration for a model run, including multiple realizations if
    applicable.

    Attributes
    ----------
    synth_pop : SynthPop
        Synthetic population to use for the run.
    start_date : Union[date, str], optional
        Simulation start date. If a ``str`` is given, should be in ISO 8601
        format, i.e. ``YYYY-MM-DD``.
    end_date : Union[date, str], optional
        Simulation end date. If a ``str`` is given, should be in ISO 8601
        format, i.e. ``YYYY-MM-DD``.
    model_params : ModelParams, optional
        Dictionary where the keys are model variable names and the values are
        the corresponding numeric or string values.
    seed : Union[int, Iterable[int]], optional
        Random number seeds for the configured runs. If ``None`` (the default),
        random seeds will be generated as required. If ``n_reps>1`` and a
        non-null value is given, this must be an iterable of length ``n_reps``.
    n_reps : int, optional
        Number of realizations of the model to run. By default, 1.
    """

    synth_pop: Optional[SynthPop] = None
    start_date: Optional[Union[date, str]] = None
    end_date: Optional[Union[date, str]] = None
    model_params: Optional[FREDModelParams] = None
    seed: Optional[Union[int, Iterable[int]]] = None
    n_reps: int = 1

    def __post_init__(self):
        self.seed = self._normalize_seed(self.seed, self.n_reps)

    @staticmethod
    def _normalize_seed(
        seed: Optional[Union[int, Iterable[int]]], n_reps: int
    ) -> Optional[Union[int, Iterable[int]]]:
        """Normalize and validate given seed value(s).

        Ensures that ``seed`` is compatible with the specified number of
        repetitions, ``n_reps``.
        """
        norm_seed: Optional[Union[int, Iterable[int]]]
        if seed is None:
            norm_seed = None
        else:
            if isinstance(seed, int):
                if n_reps == 1:
                    norm_seed = seed
                else:
                    raise IndexError(f"n_reps={n_reps} but a single seed given")
            elif isinstance(seed, Iterable):
                tuple_seeds = tuple(seed)
                if n_reps != len(tuple_seeds):
                    raise IndexError(
                        f"n_reps={n_reps} but {len(tuple_seeds)} seeds given"
                    )
                if len(tuple_seeds) == 1:
                    norm_seed = tuple_seeds[0]
                else:
                    norm_seed = tuple_seeds
        return norm_seed
