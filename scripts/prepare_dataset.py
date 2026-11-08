#!/usr/bin/env python3
"""Download (optional), filter and export Pakistan-only BGS observations."""
import argparse
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pakground.pipeline import filter_country, load_workbook_rows, write_csv

BGS_URL = "https://webservices.bgs.ac.uk/accessions/download/167240?fileName=India_Pakistan_WL_NGDC.xlsx"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "India_Pakistan_WL_NGDC.xlsx")
    parser.add_argument("--sheet", default="Full_dataset")
    parser.add_argument("--country", default="PAK", help="Exact country code/value in source workbook (default: PAK)")
    parser.add_argument("--download", action="store_true", help="Download the original BGS workbook first")
    parser.add_argument("--site-column")
    parser.add_argument("--date-column")
    parser.add_argument("--depth-column")
    parser.add_argument("--country-column")
    args = parser.parse_args()
    if args.download or not args.input.exists():
        args.input.parent.mkdir(parents=True, exist_ok=True)
        print("Downloading original BGS workbook...")
        urllib.request.urlretrieve(BGS_URL, str(args.input))
    overrides = {k: v for k, v in {"site_id": args.site_column, "date": args.date_column,
                "depth_m": args.depth_column, "country": args.country_column}.items() if v}
    rows = load_workbook_rows(args.input, args.sheet, overrides)
    selected = filter_country(rows, args.country)
    if not selected:
        raise SystemExit("No rows matched country=%r. Inspect source country values and pass --country / column overrides." % args.country)
    output = ROOT / "data" / "pakistan_groundwater_observations.csv"
    count = write_csv(selected, output)
    print("Source rows parsed: %d" % len(rows))
    print("Pakistan rows exported: %d" % count)
    print("Output: %s" % output)
    print("Reminder: the source combines Pakistan and India; do not publish unfiltered records as Pakistan-only data.")

if __name__ == "__main__":
    main()
