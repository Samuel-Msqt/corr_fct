"""Animation of the correlation function being built station by station.

Stations are visited in random order. Each frame adds a batch of stations: their pairs
with every other station (DD) and with the randoms (DR) are accumulated, and the running
Landy-Szalay estimate converges to the full measurement. Batches grow geometrically, so
the first frames show single stations and the last ones sweep through the network.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
from scipy.spatial import cKDTree

from .correlation import landy_szalay, pair_counts
from .plot_style import PAIR_COLOR
from .plots import draw_map, draw_pair_counts, draw_xi, xi_limits


def accumulate(data, randoms, edges, n_frames, rng):
    """Yield (batch, n_done, dd, dr) with dd, dr normalised over the stations done so far."""
    nd, nr = len(data), len(randoms)
    data_tree, rand_tree = cKDTree(data), cKDTree(randoms)
    order = rng.permutation(nd)
    dd, dr = np.zeros(len(edges) - 1), np.zeros(len(edges) - 1)
    done = 0
    for n_done in np.unique(np.geomspace(1, nd, n_frames).astype(int)):
        batch = cKDTree(data[order[done:n_done]])
        dd += pair_counts(batch, data_tree, edges)
        dr += pair_counts(batch, rand_tree, edges)
        yield order[done:n_done], n_done, dd / (n_done * (nd - 1)), dr / (n_done * nr)
        done = n_done


def pair_segments(data_tree, data, batch, r_max):
    """Line segments from each station in `batch` to its neighbours within r_max."""
    neighbours = data_tree.query_ball_point(data[batch], r_max)
    starts = np.repeat(data[batch], [len(n) for n in neighbours], axis=0)
    ends = data[np.concatenate(neighbours).astype(int)]
    return np.stack([starts, ends], axis=1)


def animate(city, to_km, data, randoms, corr, path, n_frames=120, hold=25, fps=12, seed=0):
    frames = list(accumulate(data, randoms, corr.edges, n_frames, np.random.default_rng(seed)))
    frames += [frames[-1]] * hold

    fig, (ax_map, ax_dd, ax_xi) = plt.subplots(1, 3, figsize=(21, 6.5),
                                               gridspec_kw={"width_ratios": [1.1, 1, 1]})
    stations = draw_map(ax_map, city, to_km, data, color="0.6")
    done = ax_map.scatter([], [], s=stations.get_sizes(), color="k", lw=0, zorder=2)
    current = ax_map.scatter([], [], s=60, facecolors="none", edgecolors=PAIR_COLOR, lw=1.5, zorder=4)
    lines = ax_map.add_collection(LineCollection([], colors=PAIR_COLOR, lw=0.6, alpha=0.5, zorder=3))
    ax_map.set_title(city.name)

    dd_steps = draw_pair_counts(ax_dd, corr, dd=np.zeros_like(corr.dd))
    ax_dd.set_title("Pair counts")

    draw_xi(ax_xi, corr, color="0.6", ls="--", label="All stations")
    running = draw_xi(ax_xi, corr, label="Stations so far")
    ax_xi.set_ylim(*xi_limits(corr.xi, pad=0.5))
    ax_xi.legend(loc="upper right")
    ax_xi.set_title("Correlation function")
    counter = ax_xi.text(0.03, 0.04, "", transform=ax_xi.transAxes, fontsize=14)
    fig.tight_layout()

    data_tree, r_max = cKDTree(data), corr.edges[-1]

    def update(i):
        batch, n_done, dd, dr = frames[i]
        is_hold = i >= len(frames) - hold
        visited = np.concatenate([f[0] for f in frames[:min(i + 1, len(frames) - hold)]])
        done.set_offsets(data[visited])
        current.set_offsets(np.empty((0, 2)) if is_hold else data[batch])
        lines.set_segments([] if is_hold else pair_segments(data_tree, data, batch, r_max))
        dd_steps.set_data(dd)
        running.set_ydata(landy_szalay(dd, dr, corr.rr))
        counter.set_text(f"{n_done} / {len(data)} stations")
        return done, current, lines, dd_steps, running, counter

    anim = FuncAnimation(fig, update, frames=len(frames), blit=False)
    anim.save(path, fps=fps, dpi=100)
    plt.close(fig)
