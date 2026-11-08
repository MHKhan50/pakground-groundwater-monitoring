#!/usr/bin/env python3
"""Write results/summary.json and figures from the prepared Pakistan-only CSV."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pakground.pipeline import read_csv  # noqa: E402
from pakground.report import build_summary, make_figures, write_summary  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "pakistan_groundwater_observations.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    rows = read_csv(args.input)
    if not rows:
        raise SystemExit("No observations found. Run scripts/prepare_dataset.py first.")
    summary = build_summary(rows)
    write_summary(summary, args.out / "summary.json")
    for p in make_figures(rows, args.out):
        print("Figure:", p)
    t = summary["trends_by_min_observations"]["4"]
    print("Observations %d, sites %d, years %s-%s" % (summary["observations"], summary["sites"],
                                                     summary["first_year"], summary["last_year"]))
    print("Sites with 4+ observations: %d (deeper %d, shallower %d, about stable %d)" % (
        t["n_sites"], t["deeper"], t["shallower"], t["about_stable"]))
    print("Summary:", args.out / "summary.json")


if __name__ == "__main__":
    main()
