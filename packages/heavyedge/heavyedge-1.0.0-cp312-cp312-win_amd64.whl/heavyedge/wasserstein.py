"""
Wasserstein distance
--------------------

Wasserstein-related functions.
"""

import numpy as np

from ._wasserstein import optimize_q

__all__ = [
    "wdist",
    "wmean",
]


def quantile(pdf, x):
    """Convert probability distribution function to quantile function.

    Parameters
    ----------
    pdf : ndarray
        An 1D array of probability distribution function values.
    x : ndarray
        An 1D array of X values for quantile function. Must be strictly increasing
        from 0 to 1.

    Returns
    -------
    ndarray
        Quantile function of *pdf* over *x*.
    """
    cdf = np.insert(np.cumsum(pdf), 0, 0)
    return np.interp(x, cdf, np.arange(len(cdf)))


def wdist(G1, G2, grid_num):
    r"""Wasserstein distance between two 1D probability distributions.

    .. math::

        d_W(G_1, G_2)^2 = \int^1_0 (G_1^{-1}(t) - G_2^{-1}(t))^2 dt

    Parameters
    ----------
    G1, G2 : ndarray
        The probability distribution functions of the input data.
    grid_num : int
        Number of sample points in [0, 1] to compute integration.

    Returns
    -------
    scalar
        Wasserstein distance.
    """
    grid = np.linspace(0, 1, grid_num)
    return np.trapezoid((quantile(G1, grid) - quantile(G2, grid)) ** 2, grid) ** 0.5


def wmean(Y, grid_num):
    """Fréchet mean of probability distrubution functions using Wasserstein metric.

    Parameters
    ----------
    Y : list of array
        Probability distribution functions.
    grid_num : int
        Number of sample points in [0, 1] to construct regression results.

    Returns
    -------
    ndarray
        Averaged *Y*.
    """
    grid = np.linspace(0, 1, grid_num)
    Q = np.array([quantile(y, grid) for y in Y])
    g = np.mean(Q, axis=0)

    if np.all(np.diff(g) >= 0):
        q = g
    else:
        q = optimize_q(g)
    cdf = np.interp(np.arange(int(q[-1])), q, np.linspace(0, 1, len(q)))
    return np.concatenate([np.diff(cdf), [0]])
