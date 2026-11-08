import csv
from datetime import datetime
import tempfile
import unittest
from pathlib import Path

from pakground.pipeline import analyse_sites, filter_country, load_workbook_rows, write_csv, read_csv


class CountryFilterTests(unittest.TestCase):
    def test_keeps_only_pakistan_aliases(self):
        rows = [{"country": "PAK"}, {"country": "Pakistan"}, {"country": "IND"}]
        self.assertEqual(len(filter_country(rows)), 2)


class TrendTests(unittest.TestCase):
    def test_positive_depth_slope_means_deeper_water_level(self):
        rows = [{"site_id": "W1", "date": "%d-01-01" % year, "depth_m": depth}
                for year, depth in [(2000, 10), (2001, 11), (2002, 12), (2003, 13)]]
        result = analyse_sites(rows, min_observations=4)[0]
        self.assertAlmostEqual(result["linear_trend_m_per_year"], 1.0, places=4)
        self.assertEqual(result["trend_interpretation"], "deeper_water_level")

    def test_insufficient_observations_are_excluded(self):
        rows = [{"site_id": "W1", "date": "2000-01-01", "depth_m": 10}]
        self.assertEqual(analyse_sites(rows, min_observations=4), [])

    def test_flat_series_is_stable(self):
        rows = [{"site_id": "W1", "date": "%d-01-01" % year, "depth_m": 10}
                for year in (2000, 2001, 2002, 2003)]
        self.assertEqual(analyse_sites(rows)[0]["trend_interpretation"], "approximately_stable")


class CsvRoundTripTests(unittest.TestCase):
    def test_csv_round_trip(self):
        rows = [{"site_id": "A", "date": "2001-01-01", "depth_m": 9.2,
                 "country": "PAK", "latitude": 31.5, "longitude": 74.3}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "observations.csv"
            write_csv(rows, path)
            loaded = read_csv(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["site_id"], "A")
            self.assertAlmostEqual(loaded[0]["depth_m"], 9.2)

    def test_workbook_import_and_sheet_header_detection(self):
        try:
            from openpyxl import Workbook
        except ImportError:
            self.skipTest("openpyxl not installed")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.xlsx"
            wb = Workbook(); ws = wb.active; ws.title = "Full_dataset"
            ws.append(["Site ID", "Date", "Groundwater Level", "Country", "Latitude", "Longitude"])
            ws.append(["W1", "2001-01-01", 12.4, "Pakistan", 31.5, 74.3])
            ws.append(["W2", "2001-01-01", 8.1, "India", 30.0, 75.0])
            wb.save(path)
            rows = load_workbook_rows(path, "Full_dataset")
            self.assertEqual(len(filter_country(rows)), 1)
            self.assertEqual(filter_country(rows)[0]["site_id"], "W1")


    def test_bgs_layout_without_country_column(self):
        from openpyxl import Workbook
        from pakground.pipeline import country_from_site_id
        self.assertEqual(country_from_site_id("PAK2041"), "PAK")
        self.assertEqual(country_from_site_id("IND17"), "IND")
        self.assertEqual(country_from_site_id("X9"), "")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bgs.xlsx"
            wb = Workbook(); ws = wb.active; ws.title = "Full_dataset"
            ws.append(["OW_ID", "DATE", "LONG", "LAT", "WL_MBGL", "LOCATION"])
            ws.append(["IND1", datetime(1973, 10, 1), 74.29, 30.07, "NA", "ABOHAR"])
            ws.append(["IND1", datetime(1974, 10, 1), 74.29, 30.07, 12.5, "ABOHAR"])
            ws.append(["PAK99", datetime(2001, 6, 1), 73.1, 31.4, 8.25, "LAHORE"])
            wb.save(path)
            rows = load_workbook_rows(path, "Full_dataset")
            self.assertEqual(len(rows), 2)  # the 'NA' depth row is skipped
            pak = filter_country(rows)
            self.assertEqual([(r["site_id"], r["depth_m"], r["latitude"]) for r in pak], [("PAK99", 8.25, 31.4)])


if __name__ == "__main__":
    unittest.main()
