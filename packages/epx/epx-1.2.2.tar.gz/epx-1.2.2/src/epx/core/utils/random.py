from typing import Optional

import numpy as np


def generate_random_seeds(
    meta_seed: Optional[int] = None, number_of_seeds: Optional[int] = 1
) -> list[int]:
    """Generate a list of RNG seeds for the simulation engine.

    Used to generate a list of simulation seeds for the user if they haven't specified
    one themselves.

    Parameters
    ----------
    meta_seed : Optional[int], optional
        Seed used to initialize the RNG that will itself be used to
        pseudo-randomly generate the simulation seed. If ``None`` (the default),
        unpredictable entropy from the OS is used in place of a ``meta_seed``.
        (see `docs`_ for ``numpy.random.default_rng``).
    number_of_seeds : Optional[int], optional (default: 1)
        The number of random seeds to generate
    Returns
    -------
    list[int]
        A list containing `number_of_seeds` randomly generated integer seeds in range [0, 2**64).

    .. _docs: https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.default_rng  # noqa

    Notes
    -----
    Generated seeds can take any value in the range that can be represented by a
    64-bit unsigned integer, matching the range of seed values that FRED can
    accept as input.
    """
    rng = np.random.default_rng(meta_seed)
    return rng.integers(0, 2**64, size=number_of_seeds, dtype=np.uint64).tolist()
