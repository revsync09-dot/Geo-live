from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")


def create_earthquake_map(lat: float, lon: float, magnitude: float, place: str) -> Path:
    plt.figure(figsize=(8, 4))
    plt.scatter(lon, lat, s=120, c="red")
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(f"Earthquake M{magnitude} – {place}")

    out_path = Path("temp") / "quake_map.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close()
    return out_path
