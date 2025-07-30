"""Raw profile data files."""

import abc
import csv
from pathlib import Path

import numpy as np

__all__ = [
    "RawProfileBase",
    "RawProfileCsvs",
]


class RawProfileBase(abc.ABC):
    """Base class to read raw profile data.

    All raw profiles must have the same length.
    """

    def __init__(self, path):
        self.path = Path(path).expanduser()

    @abc.abstractmethod
    def count_profiles(self):
        """Number of raw profiles.

        Returns
        -------
        int
        """

    @abc.abstractmethod
    def profiles(self):
        """Yield raw profiles.

        Yields
        ------
        1-D ndarray
        """

    def all_profiles(self):
        """Return all profiles as an 2-D array.

        Returns
        -------
        2-D ndarray
        """
        return np.array([p for p in self.profiles()])

    @abc.abstractmethod
    def profile_names(self):
        """Yield profile names.

        Yields
        ------
        str
        """


class RawProfileCsvs(RawProfileBase):
    """Read raw profile data from a directory containing CSV files.

    Directory structure:

    .. code-block::

        rawdata/
        ├── profile1.csv
        ├── profile2.csv
        └── ...

    Parameters
    ----------
    path : pathlike
        Path to the directory containing the raw CSV files.

    Notes
    -----
    - Each CSV file must contain a single column of numeric values (no header).
    - The order of profiles is determined by the sorted filenames.
    - The profile name is derived from the filename stem.

    Examples
    --------
    >>> from heavyedge import get_sample_path, RawProfileCsvs
    >>> profiles = RawProfileCsvs(get_sample_path("Type3")).all_profiles()
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    ... for Y in profiles:
    ...     plt.plot(Y)
    """

    def _files(self):
        return sorted(self.path.glob("*.csv"))

    def count_profiles(self):
        return len(list(self._files()))

    def profiles(self):
        for f in self._files():
            with open(f, newline="") as csvfile:
                reader = csv.reader(csvfile)
                prof = np.array([float(row[0]) for row in reader])
            yield prof

    def profile_names(self):
        for f in self._files():
            yield str(f.stem)
