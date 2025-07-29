from datetime import date
from itertools import islice, product, repeat, takewhile
from typing import (
    Any,
    Iterable,
    Optional,
    TypeAlias,
    TypeVar,
    Union,
)

from epx.job.config.fred_model_config import FREDModelConfig, FREDModelParams
from epx.core.models.synthpop import SynthPop
from epx.core.utils.random import generate_random_seeds

PackedModelParams: TypeAlias = dict[
    str, Union[Iterable[Union[float, str]], Union[float, str]]
]

T = TypeVar("T")


class FREDModelConfigSweep:
    """Sweep over parameters for a given model.

    The set of model configurations represented by ``ModelConfigSweep`` objects
    constructed by taking the cartesian product of the given sequences of input
    parameters (see Examples).

    Parameters
    ----------
    synth_pop : Iterable[SynthPop]
        Sequence of populations to use for the runs.
    start_date : Iterable[Union[date, str]], optional
        Sequence of simulation start dates to use for the runs. If start dates
        are given as ``str``, they should be in ISO 8601 format, i.e.
        ``YYYY-MM-DD``.
    end_date : Iterable[Union[date, str]], optional
        Sequence of simulation end dates to use for the runs. If end dates
        are given as ``str``, they should be in ISO 8601 format, i.e.
        ``YYYY-MM-DD``.
    model_params : Iterable[PackedModelParams], optional
        Packed model parameters to use for the runs. Each item should be
        a dictionary where the keys are model variable names and the values
        can be a list of numeric or string values (float | str)
        or simply single numeric or string values. By default ``None``.
    seed : Union[Iterable[int], int], optional
        If an iterable is given, the number of elements must equal the number of
        combinations of values in the ``synth_pop``, ``start_date``,
        ``end_date``, and ``model_params`` iterables **multiplied** by
        ``n_reps``. If a single value is given, this is used as the 'meta seed'
        to pseudo-randomly generate seeds for each of the runs. If ``None`` is
        given, seeds for each run are generated using unpredictable entropy from
        the OS (see `docs`_ for ``numpy.random.default_rng``).
    n_reps : int, optional
        Number of realizations of each model configuration. By default, 1.

    .. _docs: https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.default_rng  # noqa: E501

    Examples
    --------
    >>> sweep = ModelConfigSweep(
    ...     synth_pop=[SynthPop("US_2010.v5", ["Location1", "Location2"])],
    ...     start_date=["2024-01-01"],
    ...     end_date=["2024-01-31", "2024-02-29"],
    ...     model_params=[{"initialization_threshold": [0.95, 0.99], "ba_network": [0, 1]}]
    ... )
    >>> model_configs = list(sweep)
    >>> print(len(model_configs))
    8
    >>> print(model_configs[0].end_date)
    2024-01-31
    >>> print(model_configs[4].end_date)
    2024-02-29
    >>> print(model_configs[0].model_params)
    {'initialization_threshold': 0.95, 'ba_network': 0}
    """

    def __init__(
        self,
        synth_pop: Iterable[SynthPop],
        start_date: Optional[Iterable[Union[date, str]]],
        end_date: Optional[Iterable[Union[date, str]]],
        model_params: Optional[Iterable[PackedModelParams]] = None,
        seed: Optional[Union[Iterable[int], int]] = None,
        n_reps: int = 1,
    ):
        self.synth_pop = synth_pop
        self.start_date = self._normalize_optional_param(start_date)
        self.end_date = self._normalize_optional_param(end_date)
        self.model_params = self._unpack_model_params(
            self._normalize_optional_param(model_params)
        )
        self.seed = seed
        self.n_reps = n_reps
        self._configs = self._generate_configs()

    @staticmethod
    def _normalize_optional_param(
        param: Optional[Iterable[T]],
    ) -> Iterable[Optional[T]]:
        """Ensure that ``param`` is an iterable of ``T``.

        Converting from Optional[Iterable[T]] to an Iterable[Optional[T]]
        allows us to pass the return value of this function to ``product``.
        Without this normalization, when ``None`` (rather than ``[None]``) was
        passed to ``product`` the returned iterable would be empty.
        """
        if param is None:
            return [None]
        return [x for x in param]

    def _unpack_model_params(
        self, model_params: Iterable[Optional[PackedModelParams]]
    ) -> Iterable[Optional[FREDModelParams]]:
        if not isinstance(model_params, list):
            raise ValueError("model_params should be a non-empty list of dictionaries")

        if model_params == [None]:
            return [None]

        unpacked_model_params = []

        for param in model_params:
            param_list = []
            for value in param.values():
                if isinstance(value, list):
                    param_list.append(value)
                else:
                    param_list.append([value])

            for combination in product(*param_list):
                unpacked_model_params.append(dict(zip(param.keys(), combination)))

        return unpacked_model_params

    def _generate_configs(self) -> list[FREDModelConfig]:
        """Broadcast parameter combinations into a list of FREDModelConfigs."""
        configs = [
            x
            for x in product(
                self.synth_pop,
                self.start_date,
                self.end_date,
                self.model_params,
            )
        ]
        n_configs = len(configs) * self.n_reps
        seeds: list[int]
        if self.seed is None:
            seeds = generate_random_seeds(number_of_seeds=n_configs)
        elif isinstance(self.seed, int):
            seeds = generate_random_seeds(self.seed, n_configs)
        else:
            try:
                iter(self.seed)
                seeds = [x for x in self.seed]
                if (n_seeds := len(seeds)) != n_configs:
                    raise IndexError(
                        f"Received {n_configs} configs but {n_seeds} seeds"
                    )
            except TypeError:
                raise ValueError("Invalid seed value")

        configs_with_seeds = zip(configs, self._split_every(self.n_reps, seeds))
        return [
            FREDModelConfig(
                synth_pop, start_date, end_date, model_params, seed, self.n_reps
            )
            for (
                synth_pop,
                start_date,
                end_date,
                model_params,
            ), seed in configs_with_seeds
        ]

    def get_configs(self) -> list[FREDModelConfig]:
        """Public getter for the generated model configurations."""
        return self._configs

    @staticmethod
    def _split_every(n: int, iterable: Iterable[Any]) -> Iterable[list[Any]]:
        """Slice an iterable into chunks of n elements.

        Parameters
        ----------
        n : int
            Number of elements in each chunk.
        iterable : Iterable
            Iterable to slice.

        Returns
        -------
        Iterator
            Iterator over the chunks of the input iterable.
        """
        iterator = iter(iterable)
        return takewhile(bool, (list(islice(iterator, n)) for _ in repeat(None)))

    def __iter__(self):
        return (x for x in self._configs)

    def __repr__(self) -> str:
        return (
            f"FREDModelConfigSweep("
            f"synth_pop={self.synth_pop}, "
            f"start_date={self.start_date}, "
            f"end_date={self.end_date}, "
            f"model_params={self.model_params}, "
            f"seed={self.seed}, "
            f"n_reps={self.n_reps}"
            f")"
        )
