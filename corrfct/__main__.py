"""Measure the two-point correlation function of transit stations for each city.

    python -m corrfct                     # all cities, plots + animations
    python -m corrfct paris --no-anim     # one city, plots only
"""

import argparse
from pathlib import Path

import numpy as np

from . import plot_style
from .animate import animate
from .cities import CITIES
from .correlation import footprint_randoms, local_projection, measure
from .plots import save_city_plots, save_comparison, xi_maximum

RANDOMS_PER_STATION = 20


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cities", nargs="*", choices=list(CITIES), default=list(CITIES))
    parser.add_argument("--no-anim", action="store_true", help="skip the animations")
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    plot_style.apply()
    results = {}
    for key in args.cities:
        city = CITIES[key]
        outdir = args.out / key
        outdir.mkdir(parents=True, exist_ok=True)

        lon, lat = city.load()
        to_km = local_projection(lon.mean(), lat.mean())
        data = to_km(lon, lat)
        rng = np.random.default_rng(args.seed)
        randoms = footprint_randoms(data, RANDOMS_PER_STATION * len(data), city.footprint_cell_km, rng)
        corr = measure(data, randoms, city.edges)
        results[city.name] = corr
        print(f"{city.name}: {len(data)} stations, {len(randoms)} randoms")

        save_city_plots(city, to_km, data, randoms, corr, outdir)
        np.savetxt(outdir / "xi.csv", np.column_stack([corr.edges[:-1], corr.edges[1:], corr.xi]),
                   delimiter=",", header="r_min_km,r_max_km,xi", comments="")
        if not args.no_anim:
            animate(city, to_km, data, randoms, corr, outdir / "animation.mp4", seed=args.seed)
            print(f"  wrote {outdir / 'animation.mp4'}")

    if len(results) > 1:
        save_comparison(results, args.out / "xi_comparison.png")
        with open(args.out / "xi_maxima.csv", "w") as f:
            f.write("city,r_km,xi_max\n")
            for name, corr in results.items():
                f.write("{},{:.4f},{:.4f}\n".format(name, *xi_maximum(corr)))


if __name__ == "__main__":
    main()
