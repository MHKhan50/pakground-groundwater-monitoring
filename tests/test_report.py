import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pakground.report import build_summary, classify, make_figures  # noqa: E402


def _rows():
    rows = []
    for i, slope in enumerate((0.5, -0.4, 0.02)):
        for k, year in enumerate(range(1990, 2015, 2)):
            rows.append({"site_id": "S%d" % i, "date": "%d-06-01" % year, "depth_m": 5 + slope * k * 2,
                         "country": "PAK", "latitude": 30 + i, "longitude": 72 + i})
    return rows


class ReportTests(unittest.TestCase):
    def test_classify_uses_band(self):
        self.assertEqual(classify(0.5), "deeper")
        self.assertEqual(classify(-0.5), "shallower")
        self.assertEqual(classify(0.05), "about_stable")

    def test_summary_counts(self):
        s = build_summary(_rows())
        self.assertEqual(s["sites"], 3)
        self.assertEqual(s["first_year"], 1990)
        t = s["trends_by_min_observations"]["4"]
        self.assertEqual((t["deeper"], t["shallower"], t["about_stable"]), (1, 1, 1))
        self.assertEqual(s["trends_by_min_observations"]["20"]["n_sites"], 0)
        json.dumps(s)

    def test_figures_and_kaggle_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for sub in ("pakground", "scripts", "docs", "data", "results"):
                (root / sub).mkdir()
            for f in ("pakground/__init__.py", "pakground/pipeline.py", "pakground/report.py",
                      "scripts/report.py", "scripts/analyse.py", "scripts/make_kaggle_package.py",
                      "docs/DATASET_CARD.md", "docs/DATA_DICTIONARY.md"):
                (root / f).write_text((ROOT / f).read_text(encoding="utf-8"), encoding="utf-8")
            with (root / "data" / "pakistan_groundwater_observations.csv").open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=["site_id", "date", "depth_m", "country", "latitude", "longitude"])
                w.writeheader()
                w.writerows(_rows())
            for script in ("analyse.py", "report.py", "make_kaggle_package.py"):
                subprocess.run([sys.executable, str(root / "scripts" / script)], check=True, capture_output=True)
            self.assertTrue((root / "results" / "fig_site_map.png").exists())
            up = root / "kaggle" / "1-upload-these"
            self.assertEqual(sorted(p.name for p in up.iterdir()),
                             ["DATASET_CARD.md", "DATA_DICTIONARY.md", "pakistan_groundwater_observations.csv", "site_trends.csv"])
            fields = (root / "kaggle" / "2-helpers" / "KAGGLE_FIELDS.md").read_text()
            self.assertIn("39 observations from 3 wells", fields)
            self.assertTrue((root / "kaggle" / "2-helpers" / "cover_1280x640.png").exists())


if __name__ == "__main__":
    unittest.main()
