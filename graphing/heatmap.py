from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Iterable, Mapping

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Agg")


def world_heatmap(points: Iterable[Mapping[str, float]], title: str) -> Path:
    """
    Create a simple scatter-style heat map for lat/lon intensity points.
    """
    lats = [p.get("lat") for p in points if p.get("lat") is not None]
    lons = [p.get("lon") for p in points if p.get("lon") is not None]
    mag = [p.get("value", 1) for p in points if p.get("lat") is not None]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_facecolor("#0b1224")
    scatter = ax.scatter(lons, lats, c=mag, cmap="coolwarm", alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.colorbar(scatter, ax=ax, label="Intensity")
    fig.tight_layout()

    out_path = Path(tempfile.gettempdir()) / "geolive_heatmap.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path
