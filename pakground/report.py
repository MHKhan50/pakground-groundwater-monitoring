"""Summary statistics, sensitivity checks and figures for the Pakistan-only observations."""
from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .pipeline import analyse_sites

STABLE_BAND_M_PER_YEAR = 0.1  # |slope| below this is reported as "about stable"


def classify(slope: float, band: float = STABLE_BAND_M_PER_YEAR) -> str:
    if slope > band:
        return "deeper"
    if slope < -band:
        return "shallower"
    return "about_stable"


def _quantiles(values: Sequence[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {"p25": None, "median": None, "p75": None}
    if len(values) == 1:
        return {"p25": values[0], "median": values[0], "p75": values[0]}
    q = statistics.quantiles(values, n=4)
    return {"p25": round(q[0], 4), "median": round(statistics.median(values), 4), "p75": round(q[2], 4)}


def trend_summary(sites: List[dict], band: float = STABLE_BAND_M_PER_YEAR) -> dict:
    slopes = [s["linear_trend_m_per_year"] for s in sites]
    counts = Counter(classify(v, band) for v in slopes)
    n = len(sites)
    return {
        "n_sites": n,
        "deeper": counts["deeper"],
        "shallower": counts["shallower"],
        "about_stable": counts["about_stable"],
        "share_deeper": round(counts["deeper"] / n, 4) if n else None,
        "slope_m_per_year": _quantiles(slopes),
    }


def build_summary(rows: List[dict], min_obs_levels: Sequence[int] = (4, 10, 20),
                  recent_from: int = 2000) -> dict:
    years = [int(str(r["date"])[:4]) for r in rows]
    sites = {r["site_id"] for r in rows}
    with_coords = sum(1 for r in rows if r.get("latitude") is not None and r.get("longitude") is not None)
    per_site = Counter(r["site_id"] for r in rows)
    summary = {
        "observations": len(rows),
        "sites": len(sites),
        "first_year": min(years) if years else None,
        "last_year": max(years) if years else None,
        "country_values": sorted({str(r.get("country")) for r in rows}),
        "share_rows_with_coordinates": round(with_coords / len(rows), 4) if rows else None,
        "observations_per_site": _quantiles(sorted(float(v) for v in per_site.values())),
        "depth_m": _quantiles(sorted(float(r["depth_m"]) for r in rows)),
        "stable_band_m_per_year": STABLE_BAND_M_PER_YEAR,
        "trends_by_min_observations": {},
    }
    for k in min_obs_levels:
        summary["trends_by_min_observations"][str(k)] = trend_summary(analyse_sites(rows, k))
    recent = [r for r in rows if int(str(r["date"])[:4]) >= recent_from]
    summary["recent_window"] = {"from_year": recent_from,
                                "observations": len(recent),
                                "trends_min_obs_4": trend_summary(analyse_sites(recent, 4))}
    return summary


def write_summary(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def make_figures(rows: List[dict], out_dir: Path, min_observations: int = 4) -> List[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    blue, navy, red, grey = "#2b5ce6", "#0f1932", "#c0392b", "#9aa5b8"
    paths = []

    per_year = Counter(int(str(r["date"])[:4]) for r in rows)
    xs = sorted(per_year)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.bar(xs, [per_year[x] for x in xs], width=0.9, color=blue)
    ax.set_title("Pakistan observations per year (BGS compilation)")
    ax.set_ylabel("Observations")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    paths.append(out_dir / "fig_observations_per_year.png")
    fig.savefig(paths[-1], dpi=160)
    plt.close(fig)

    sites = analyse_sites(rows, min_observations)
    slopes = [s["linear_trend_m_per_year"] for s in sites]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    clipped = [max(-2.0, min(2.0, v)) for v in slopes]
    ax.hist(clipped, bins=40, color=blue)
    ax.axvline(0, color=navy, lw=1)
    ax.set_title("Site trends, %d sites with %d+ observations" % (len(sites), min_observations))
    ax.set_xlabel("Linear trend, m/year (positive = deeper below ground; clipped at +/-2)")
    ax.set_ylabel("Sites")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    paths.append(out_dir / "fig_trend_histogram.png")
    fig.savefig(paths[-1], dpi=160)
    plt.close(fig)

    located = [s for s in sites if s.get("latitude") is not None and s.get("longitude") is not None]
    if located:
        fig, ax = plt.subplots(figsize=(6.4, 6))
        colors = [red if classify(s["linear_trend_m_per_year"]) == "deeper" else
                  blue if classify(s["linear_trend_m_per_year"]) == "shallower" else grey for s in located]
        ax.scatter([s["longitude"] for s in located], [s["latitude"] for s in located], c=colors, s=10, alpha=0.8)
        for c, label in ((red, "deeper"), (blue, "shallower"), (grey, "about stable")):
            ax.scatter([], [], c=c, s=20, label=label)
        ax.legend(frameon=False, loc="lower right")
        ax.set_title("Site trend direction (|slope| < %.1f m/yr = about stable)" % STABLE_BAND_M_PER_YEAR)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_aspect("equal", adjustable="datalim")
        fig.tight_layout()
        paths.append(out_dir / "fig_site_map.png")
        fig.savefig(paths[-1], dpi=160)
        plt.close(fig)
    return paths
