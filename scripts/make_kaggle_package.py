#!/usr/bin/env python3
"""Build kaggle/1-upload-these and kaggle/2-helpers from the validated outputs."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SUBTITLE = "Pakistan-only well observations and site trends from the BGS Punjab compilation"


def cover(path: Path, summary: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12.8, 6.4), dpi=100)
    fig.patch.set_facecolor("#0f1932")
    fig.text(0.06, 0.70, "Pakistan Punjab", color="#7fa2ff", fontsize=30, weight="bold")
    fig.text(0.06, 0.55, "Groundwater levels", color="white", fontsize=46, weight="bold")
    fig.text(0.06, 0.40, "%s observations | %s wells | %s-%s" % (
        format(summary["observations"], ","), format(summary["sites"], ","),
        summary["first_year"], summary["last_year"]), color="#e8eefd", fontsize=22)
    fig.text(0.06, 0.12, "Pakistan-only derivative of the BGS / NERC dataset | Muzammal Hussain",
             color="#9aa5b8", fontsize=16)
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def fields_md(summary: dict) -> str:
    t = summary["trends_by_min_observations"]["4"]
    return """# Kaggle fields (copy into the dataset page)

**Title:** {title}

**Subtitle:** {subtitle}

**Licence:** Other (specified in description)

**Tags:** Earth and Nature, Pakistan, Water Bodies, Time Series, Geospatial Analysis

**Description:**

Groundwater-level observations for Pakistan Punjab, filtered from the British Geological Survey compilation
"A century of groundwater accumulation in Pakistan and northwest India - dataset" (MacAllister, Krishan, Basharat
and MacDonald, 2021, DOI 10.5285/150c95f7-18bf-4f66-880b-8364b7257b26). The source covers Pakistan and northwest
India; only rows tagged Pakistan are kept.

Contents
- `pakistan_groundwater_observations.csv`: {obs:,} observations from {sites:,} wells, {fy}-{ly}. Depth is metres
  below ground level.
- `site_trends.csv`: one row per well with 4 or more observations ({n:,} wells): ordinary least-squares trend in
  m/year (positive = water level deeper below ground).
- `DATASET_CARD.md`, `DATA_DICTIONARY.md`: fields, method and limitations.

Built with the open pipeline at https://github.com/MHKhan50/pakground-groundwater-monitoring (tests included).

Limitations: wells are not a random sample; sampling is irregular; a deeper water level is not a measure of
aquifer storage; the data end in {ly}.

Licence and attribution: the source is published by BGS under the Open Government Licence. Contains data supplied
by permission of the Natural Environment Research Council [YEAR]. (Confirm the year on the BGS catalogue page
before publishing.)
""".format(title="Pakistan Punjab Groundwater Levels %s-%s" % (summary["first_year"], summary["last_year"]), subtitle=SUBTITLE, obs=summary["observations"], sites=summary["sites"],
           fy=summary["first_year"], ly=summary["last_year"], n=t["n_sites"])


def notebook() -> dict:
    def code(src):
        return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
    cells = [
        {"cell_type": "markdown", "metadata": {}, "source": "# Pakistan Punjab groundwater levels: starter\n"
         "Load the observations and site trends, plot coverage and the trend distribution."},
        code("import glob, pandas as pd, matplotlib.pyplot as plt\n"
             "obs = pd.read_csv(glob.glob('/kaggle/input/**/pakistan_groundwater_observations.csv', recursive=True)[0], parse_dates=['date'])\n"
             "trends = pd.read_csv(glob.glob('/kaggle/input/**/site_trends.csv', recursive=True)[0])\n"
             "print(obs.shape, obs.site_id.nunique(), obs.date.min().date(), obs.date.max().date())\n"
             "obs.head()"),
        code("obs.groupby(obs.date.dt.year).size().plot(kind='bar', figsize=(12,3), color='#2b5ce6', title='Observations per year')\n"
             "plt.xticks([]); plt.show()"),
        code("trends.linear_trend_m_per_year.clip(-2, 2).plot(kind='hist', bins=40, color='#2b5ce6', title='Site trends (m/year, + = deeper)')\n"
             "plt.show()\n"
             "trends.linear_trend_m_per_year.describe()"),
        code("site = trends.sort_values('n_observations').iloc[-1].site_id\n"
             "obs[obs.site_id == site].plot(x='date', y='depth_m', title='Longest record: ' + str(site), legend=False)\n"
             "plt.gca().invert_yaxis(); plt.ylabel('m below ground'); plt.show()"),
    ]
    return {"cells": cells, "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}},
            "nbformat": 4, "nbformat_minor": 5}


def main() -> None:
    summary = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))
    up = ROOT / "kaggle" / "1-upload-these"
    helpers = ROOT / "kaggle" / "2-helpers"
    for d in (up, helpers):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    for src in (ROOT / "data" / "pakistan_groundwater_observations.csv", ROOT / "results" / "site_trends.csv",
                ROOT / "docs" / "DATASET_CARD.md", ROOT / "docs" / "DATA_DICTIONARY.md"):
        shutil.copy(src, up / src.name)
    cover(helpers / "cover_1280x640.png", summary)
    (helpers / "KAGGLE_FIELDS.md").write_text(fields_md(summary), encoding="utf-8")
    (helpers / "starter_notebook.ipynb").write_text(json.dumps(notebook(), indent=1), encoding="utf-8")
    print("Kaggle package ready in", ROOT / "kaggle")


if __name__ == "__main__":
    main()
