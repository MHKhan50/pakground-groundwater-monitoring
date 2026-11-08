#!/usr/bin/env python3
"""Generate transparent site-level linear trend summaries from prepared CSV."""
import argparse
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pakground.pipeline import read_csv, write_site_summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "pakistan_groundwater_observations.csv")
    parser.add_argument("--min-observations", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "site_trends.csv")
    args = parser.parse_args()
    if args.min_observations < 2:
        parser.error("--min-observations must be at least 2")
    rows = read_csv(args.input)
    if not rows:
        raise SystemExit("No valid observations found. Run scripts/prepare_dataset.py first.")
    count = write_site_summary(rows, args.output, args.min_observations)
    print("Observations analysed: %d" % len(rows))
    print("Sites with sufficient observations: %d" % count)
    print("Site trend summary: %s" % args.output)
    print("Interpretation: positive m/year means depth below ground increased; it does not by itself prove aquifer storage depletion.")

if __name__ == "__main__":
    main()
