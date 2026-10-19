# Two-point correlation function of transit stations

Measures how transit stations cluster in Paris, Grenoble and Strasbourg with the
two-point correlation function ξ(r): the excess probability, compared to a random
distribution, of finding two stations at distance r.

```sh
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m corrfct                  # all cities, plots + animations
.venv/bin/python -m corrfct paris --no-anim  # one city, plots only
```

Outputs go to `output/<city>/`: `map.png`, `pair_counts.png`, `xi.png`, `xi.csv`,
`animation.mp4` (needs `ffmpeg`), plus `output/xi_comparison.png`.

## Method

1. **Stations** (`corrfct/cities.py`): one point per stop, platforms merged.
   - Paris: IDFM GTFS feed (`data/IDFM-gtfs.zip`), parent stations in zones 1–3.
   - Grenoble: SEM stops (`data/grenoble_stops.json`), latitude 45.11–45.22.
   - Strasbourg: CTS stop points (`data/strasbourg_stops.json`), merged by logical stop.
     If the file is missing it is downloaded, which needs `CTS_API_TOKEN` set.
2. **Projection**: lon/lat to km with a local equirectangular projection.
3. **Randoms**: uniform points, kept with probability proportional to the station
   density on a 2 km grid, so they follow the network footprint without its small-scale clustering.
4. **Pair counts** DD, DR, RR with a KD-tree (`scipy.spatial.cKDTree.count_neighbors`).
5. **Estimator**: Landy–Szalay, ξ = (DD − 2DR + RR) / RR on normalised counts.

The animation visits stations in random order and accumulates their pairs, showing
the pair-count histogram and ξ(r) converging to the full measurement.
