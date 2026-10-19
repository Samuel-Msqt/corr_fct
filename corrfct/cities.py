"""Station catalogues, one point per stop (platforms of the same stop are merged)."""

import csv
import io
import json
import os
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CTS_STOPS_URL = "https://api.cts-strasbourg.eu/v1/siri/2.0/stoppoints-discovery"


@dataclass(frozen=True)
class City:
    name: str
    load: Callable[[], tuple[np.ndarray, np.ndarray]]  # -> (lon, lat) in degrees
    edges: np.ndarray  # separation bin edges [km]
    # Size of the grid cells used to trace the network footprint for the randoms.
    # Must be larger than the separations we measure, or the randoms copy the clustering.
    footprint_cell_km: float = 2.0
    # Optional background image: (path, (lon_min, lon_max, lat_min, lat_max)).
    background: tuple[Path, tuple[float, float, float, float]] | None = None


def load_paris(zones=("1", "2", "3")):
    """IDFM GTFS feed: stations (parent stops) having at least one platform in `zones`."""
    with zipfile.ZipFile(DATA_DIR / "IDFM-gtfs.zip") as zf, zf.open("stops.txt") as f:
        rows = list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")))
    by_id = {row["stop_id"]: row for row in rows}
    parents = sorted({row["parent_station"] for row in rows
                      if row["location_type"] == "0" and row["zone_id"] in zones})
    stations = [by_id[p] for p in parents]
    lon = np.array([float(s["stop_lon"]) for s in stations])
    lat = np.array([float(s["stop_lat"]) for s in stations])
    return lon, lat


def load_grenoble(lat_range=(45.11, 45.22)):
    """SEM stops, restricted to the Grenoble basin."""
    with open(DATA_DIR / "grenoble_stops.json") as f:
        stops = json.load(f)
    lon = np.array([s["lon"] for s in stops])
    lat = np.array([s["lat"] for s in stops])
    keep = (lat > lat_range[0]) & (lat < lat_range[1])
    return lon[keep], lat[keep]


def fetch_strasbourg(path):
    """Download CTS stop points; needs an API token in the CTS_API_TOKEN environment variable."""
    import requests

    token = os.environ.get("CTS_API_TOKEN")
    if not token:
        raise RuntimeError(f"{path} missing: set CTS_API_TOKEN to download it from {CTS_STOPS_URL}")
    response = requests.get(CTS_STOPS_URL, auth=(token, ""), timeout=60)
    response.raise_for_status()
    path.write_text(response.text)


def load_strasbourg():
    """CTS stop points, merged by logical stop (mean position of its platforms)."""
    path = DATA_DIR / "strasbourg_stops.json"
    if not path.exists():
        fetch_strasbourg(path)
    with open(path) as f:
        points = json.load(f)["StopPointsDelivery"]["AnnotatedStopPointRef"]
    platforms = defaultdict(list)
    for p in points:
        platforms[p["Extension"]["LogicalStopCode"]].append(
            (p["Location"]["Longitude"], p["Location"]["Latitude"]))
    lon, lat = np.array([np.mean(v, axis=0) for v in platforms.values()]).T
    return lon, lat


CITIES = {
    "paris": City(
        name="Paris",
        load=load_paris,
        edges=np.linspace(0., 2., 41),
        background=(DATA_DIR / "paris_satellite.png", (2.14, 2.54, 48.725, 48.98)),
    ),
    "grenoble": City(
        name="Grenoble",
        load=load_grenoble,
        edges=np.linspace(0., 2., 21),
    ),
    "strasbourg": City(
        name="Strasbourg",
        load=load_strasbourg,
        edges=np.linspace(0., 2., 21),
    ),
}
