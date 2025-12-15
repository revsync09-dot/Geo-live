from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")


def create_weather_graph(
    times: Sequence[str],
    temps: Sequence[float],
    dewpoints: Sequence[float],
    location_name: str,
) -> Path:
    """
    Render temperature vs. dew point graph with light styling.
    """
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.set_facecolor("#f9f9f9")

    # Temperature line and area fill
    ax.fill_between(times, temps, color="#b8f5b1", alpha=0.7, label="Temperature")
    ax.plot(times, temps, color="#2f7d32", linewidth=2.2)

    # Dew point line
    ax.plot(times, dewpoints, color="#d62828", linewidth=2, label="Dew point")

    ax.set_title(f"Temperature / Dew Point – {location_name}", fontsize=14, color="#1f2937")
    ax.set_xlabel("Time")
    ax.set_ylabel("°C")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.6)
    ax.legend(frameon=False, loc="upper left")
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()

    out_path = Path("temp") / "graph.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return out_path
