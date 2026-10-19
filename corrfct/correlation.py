"""Two-point correlation function of a 2D point set, Landy-Szalay estimator."""

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

EARTH_RADIUS_KM = 6371.0


def local_projection(lon0, lat0):
    """Equirectangular projection to km around (lon0, lat0); accurate at city scale."""
    km_per_deg = np.radians(1.) * EARTH_RADIUS_KM
    coslat0 = np.cos(np.radians(lat0))

    def to_km(lon, lat):
        lon, lat = np.asarray(lon), np.asarray(lat)
        return np.column_stack([(lon - lon0) * km_per_deg * coslat0,
                                (lat - lat0) * km_per_deg])

    return to_km


def pair_counts(a, b, edges):
    """Number of ordered pairs (i in a, j in b) per separation bin (edges[k], edges[k+1]].

    `a` and `b` are (N, 2) arrays or prebuilt cKDTrees. Self-pairs (separation 0) never
    land in a bin, so pair_counts(x, x, edges) counts each distinct pair twice.
    """
    ta = a if isinstance(a, cKDTree) else cKDTree(a)
    tb = b if isinstance(b, cKDTree) else cKDTree(b)
    return np.diff(ta.count_neighbors(tb, edges)).astype(float)


def footprint_randoms(data, n, cell_km, rng):
    """About `n` random points following the large-scale density of `data`.

    Uniform points in the bounding box are kept with probability proportional to the
    data density on a grid of `cell_km` cells, so empty regions (rivers, fields) get
    no randoms while clustering below the cell size is not reproduced.
    """
    lo, hi = data.min(axis=0), data.max(axis=0)
    nbins = np.maximum(np.ceil((hi - lo) / cell_km).astype(int), 1)
    hist, xedges, yedges = np.histogram2d(data[:, 0], data[:, 1], bins=nbins,
                                          range=list(zip(lo, hi)))
    accept = hist / hist.max()
    candidates = rng.uniform(lo, hi, size=(int(np.ceil(n / accept.mean())), 2))
    ix = np.clip(np.digitize(candidates[:, 0], xedges) - 1, 0, nbins[0] - 1)
    iy = np.clip(np.digitize(candidates[:, 1], yedges) - 1, 0, nbins[1] - 1)
    return candidates[rng.uniform(size=len(candidates)) < accept[ix, iy]]


def landy_szalay(dd, dr, rr):
    """xi = (DD - 2 DR + RR) / RR, with each pair count normalised to a pair fraction."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return (dd - 2. * dr + rr) / rr


@dataclass
class Correlation:
    edges: np.ndarray
    dd: np.ndarray  # normalised pair fractions per bin
    dr: np.ndarray
    rr: np.ndarray

    @property
    def centers(self):
        return 0.5 * (self.edges[:-1] + self.edges[1:])

    @property
    def xi(self):
        return landy_szalay(self.dd, self.dr, self.rr)


def measure(data, randoms, edges):
    nd, nr = len(data), len(randoms)
    data_tree, rand_tree = cKDTree(data), cKDTree(randoms)
    return Correlation(
        edges=edges,
        dd=pair_counts(data_tree, data_tree, edges) / (nd * (nd - 1)),
        dr=pair_counts(data_tree, rand_tree, edges) / (nd * nr),
        rr=pair_counts(rand_tree, rand_tree, edges) / (nr * (nr - 1)),
    )
