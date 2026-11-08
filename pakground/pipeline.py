"""Import, validate, filter and analyse the BGS Punjab groundwater workbook."""
from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ALIASES = {
    "site_id": ("site_id", "site", "well_id", "well", "observation_well", "ow_id", "name", "id"),
    "date": ("date", "measurement_date", "observation_date", "time", "year"),
    "depth_m": ("depth_m", "wl_mbgl", "groundwater_level", "water_level", "level", "gw_level", "waterlevel", "mbgl"),
    "country": ("country", "country_code", "nation"),
    "latitude": ("latitude", "lat", "y"),
    "longitude": ("longitude", "lon", "long", "x"),
}


def _norm(value: object) -> str:
    return "".join(ch.lower() for ch in str(value).strip() if ch.isalnum())


def _parse_date(value: object) -> Optional[str]:
    if value is None or str(value).strip() == "":
        return None
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text[:10], fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    try:
        year = int(float(text))
        if 1800 <= year <= 2100:
            return "%04d-01-01" % year
    except ValueError:
        pass
    return None


def _float(value: object) -> Optional[float]:
    if value is None or str(value).strip() == "":
        return None
    try:
        result = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _find_columns(headers: Sequence[object], overrides: Optional[Dict[str, str]] = None) -> Dict[str, int]:
    normalized = {_norm(h): i for i, h in enumerate(headers)}
    found: Dict[str, int] = {}
    overrides = overrides or {}
    for field, aliases in ALIASES.items():
        requested = overrides.get(field)
        candidates = (_norm(requested),) if requested else tuple(_norm(a) for a in aliases)
        for candidate in candidates:
            if candidate in normalized:
                found[field] = normalized[candidate]
                break
    # The BGS workbook has no country column; its well IDs start with PAK or IND (see country_from_site_id).
    missing = [field for field in ("site_id", "date", "depth_m") if field not in found]
    if missing:
        raise ValueError("Could not identify required columns: %s. Available headers: %s" % (", ".join(missing), list(headers)))
    return found


def country_from_site_id(site_id: str) -> str:
    """Return PAK or IND from a BGS well ID such as PAK2041 or IND17; empty string otherwise."""
    prefix = "".join(ch for ch in str(site_id).strip().upper()[:3] if ch.isalpha())
    return prefix if prefix in ("PAK", "IND") else ""


def load_workbook_rows(path: Path, sheet_name: Optional[str] = None, overrides: Optional[Dict[str, str]] = None) -> List[dict]:
    """Read an XLSX sheet. Requires openpyxl; never silently guesses country."""
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("Install workbook support with: python3 -m pip install -r requirements.txt") from exc
    workbook = load_workbook(str(path), read_only=True, data_only=True)
    try:
        if sheet_name:
            if sheet_name not in workbook.sheetnames:
                raise ValueError("Sheet %r not found; available: %s" % (sheet_name, workbook.sheetnames))
            sheet = workbook[sheet_name]
        else:
            sheet = workbook[workbook.sheetnames[0]]
        iterator = sheet.iter_rows(values_only=True)
        headers = next(iterator, None)
        if not headers:
            raise ValueError("Workbook sheet is empty")
        columns = _find_columns(headers, overrides)
        output = []
        for row in iterator:
            if not row or all(value is None for value in row):
                continue
            get = lambda key: row[columns[key]] if columns[key] < len(row) else None
            country = (str(get("country") or "").strip().upper() if "country" in columns
                       else country_from_site_id(get("site_id") or ""))
            parsed_date = _parse_date(get("date"))
            depth = _float(get("depth_m"))
            site = str(get("site_id") or "").strip()
            if not site or not parsed_date or depth is None or not country:
                continue
            record = {"site_id": site, "date": parsed_date, "depth_m": depth, "country": country}
            for field in ("latitude", "longitude"):
                record[field] = _float(get(field)) if field in columns else None
            output.append(record)
        return output
    finally:
        workbook.close()


def _country_matches(value: object, requested: str) -> bool:
    actual = str(value or "").strip().upper()
    code = requested.strip().upper()
    aliases = {"PAK": {"PAK", "PAKISTAN", "PK"}, "IND": {"IND", "INDIA", "IN"}}
    return actual in aliases.get(code, {code})


def filter_country(rows: Iterable[dict], country_code: str = "PAK") -> List[dict]:
    return [row for row in rows if _country_matches(row.get("country"), country_code)]


def write_csv(rows: Iterable[dict], destination: Path) -> int:
    fields = ["site_id", "date", "depth_m", "country", "latitude", "longitude"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def read_csv(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = []
        for row in csv.DictReader(handle):
            depth = _float(row.get("depth_m"))
            parsed_date = _parse_date(row.get("date"))
            if depth is None or parsed_date is None:
                continue
            rows.append({"site_id": row["site_id"], "date": parsed_date, "depth_m": depth,
                         "country": row.get("country", "PAK"), "latitude": _float(row.get("latitude")),
                         "longitude": _float(row.get("longitude"))})
        return rows


def _slope_per_year(points: Sequence[Tuple[float, float]]) -> Optional[float]:
    if len(points) < 2:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    mean_x, mean_y = statistics.mean(xs), statistics.mean(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0:
        return None
    return sum((x - mean_x) * (y - mean_y) for x, y in points) / denominator


def analyse_sites(rows: Iterable[dict], min_observations: int = 4) -> List[dict]:
    grouped = defaultdict(list)
    for row in rows:
        try:
            year = float(str(row["date"])[:4])
            depth = float(row["depth_m"])
        except (KeyError, TypeError, ValueError):
            continue
        grouped[str(row["site_id"])].append((year, depth, row))
    results = []
    for site_id, observations in sorted(grouped.items()):
        observations.sort(key=lambda item: item[0])
        if len(observations) < min_observations:
            continue
        slope = _slope_per_year([(year, depth) for year, depth, _ in observations])
        if slope is None:
            continue
        # Positive depth trend = water table is getting deeper (potential decline).
        first, last = observations[0], observations[-1]
        results.append({
            "site_id": site_id,
            "n_observations": len(observations),
            "first_year": int(first[0]),
            "last_year": int(last[0]),
            "first_depth_m": round(first[1], 3),
            "last_depth_m": round(last[1], 3),
            "linear_trend_m_per_year": round(slope, 5),
            "trend_interpretation": "deeper_water_level" if slope > 0 else "shallower_water_level" if slope < 0 else "approximately_stable",
            "latitude": last[2].get("latitude"),
            "longitude": last[2].get("longitude"),
        })
    return results


def write_site_summary(rows: Iterable[dict], destination: Path, min_observations: int = 4) -> int:
    summary = analyse_sites(rows, min_observations)
    fields = ["site_id", "n_observations", "first_year", "last_year", "first_depth_m", "last_depth_m", "linear_trend_m_per_year", "trend_interpretation", "latitude", "longitude"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)
    return len(summary)
