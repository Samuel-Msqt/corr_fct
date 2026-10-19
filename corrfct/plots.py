import matplotlib.pyplot as plt
import numpy as np

from .plot_style import RANDOMS_COLOR, STATIONS_COLOR

SEP_LABEL = "Distance between stations [km]"


def draw_map(ax, city, to_km, data, color=STATIONS_COLOR):
    """Station scatter in km, on top of the city's background image if it has one."""
    if city.background is not None:
        path, (lon_min, lon_max, lat_min, lat_max) = city.background
        (x0, y0), (x1, y1) = to_km([lon_min, lon_max], [lat_min, lat_max])
        ax.imshow(plt.imread(path), extent=[x0, x1, y0, y1], alpha=0.6, zorder=0)
    size = max(3., 3000. / len(data))  # sparse networks get bigger markers
    stations = ax.scatter(data[:, 0], data[:, 1], s=size, color=color, lw=0, zorder=1)
    ax.set_xlim(data[:, 0].min() - 0.5, data[:, 0].max() + 0.5)
    ax.set_ylim(data[:, 1].min() - 0.5, data[:, 1].max() + 0.5)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$\Delta x$ [km]")
    ax.set_ylabel(r"$\Delta y$ [km]")
    return stations


def draw_pair_counts(ax, corr, dd=None):
    """Normalised DD and RR histograms; `dd` overrides corr.dd (used for partial counts)."""
    dd_steps = ax.stairs(corr.dd if dd is None else dd, corr.edges,
                         color=STATIONS_COLOR, lw=2, label="Stations (DD)")
    ax.stairs(corr.rr, corr.edges, color=RANDOMS_COLOR, lw=2, label="Randoms (RR)")
    ax.set_xlim(corr.edges[0], corr.edges[-1])
    ax.set_ylim(0., 1.25 * max(corr.dd.max(), corr.rr.max()))
    ax.set_xlabel(SEP_LABEL)
    ax.set_ylabel("Fraction of pairs")
    ax.legend(loc="upper left")
    return dd_steps


def draw_xi(ax, corr, **kwargs):
    ax.axhline(0., color="k", ls="--", alpha=0.5)
    (line,) = ax.plot(corr.centers, corr.xi, **{"color": "k", "lw": 2, **kwargs})
    ax.set_xlim(corr.edges[0], corr.edges[-1])
    ax.set_xlabel(SEP_LABEL)
    ax.set_ylabel(r"$\xi(r)$")
    ax.grid(alpha=0.3)
    return line


def xi_limits(xi, pad=0.2):
    lo, hi = np.nanmin(xi), np.nanmax(xi)
    margin = pad * (hi - lo)
    return min(lo, 0.) - margin, hi + margin


def save_city_plots(city, to_km, data, randoms, corr, outdir):
    fig, ax = plt.subplots(figsize=(7, 7))
    draw_map(ax, city, to_km, data)
    shown = randoms[:5 * len(data)]  # randoms are in random order: any slice is a fair subsample
    ax.scatter(shown[:, 0], shown[:, 1], s=1, color=RANDOMS_COLOR, lw=0, zorder=0.5)
    ax.scatter([], [], color=STATIONS_COLOR, label=f"Stations ({len(data)})")
    ax.scatter([], [], color=RANDOMS_COLOR, label="Randoms")
    ax.legend(loc="upper left", ncol=2)
    ax.set_title(f"{city.name}: stations and randoms")
    fig.savefig(outdir / "map.png")
    plt.close(fig)

    fig, ax = plt.subplots()
    draw_pair_counts(ax, corr)
    ax.set_title(f"{city.name}: pair counts")
    fig.savefig(outdir / "pair_counts.png")
    plt.close(fig)

    fig, ax = plt.subplots()
    draw_xi(ax, corr)
    ax.set_ylim(*xi_limits(corr.xi))
    ax.set_title(f"{city.name}: correlation function")
    fig.savefig(outdir / "xi.png")
    plt.close(fig)


def save_comparison(results, path):
    fig, ax = plt.subplots()
    for name, corr in results.items():
        draw_xi(ax, corr, color=None, label=name)
    ax.set_ylim(*xi_limits(np.concatenate([c.xi for c in results.values()])))
    ax.legend()
    ax.set_title("Station correlation function")
    fig.savefig(path)
    plt.close(fig)
