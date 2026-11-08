# PakGround: Pakistan Groundwater Monitoring

**Release:** v0.2.0  
**Repository:** `MHKhan50/pakground-groundwater-monitoring`  
**Research focus:** Reproducible extraction and exploratory trend analysis of historical groundwater-level observations for Punjab, Pakistan.

PakGround is a research pipeline, not a claim that all groundwater in Punjab is declining. It takes the British Geological Survey (BGS) workbook covering Punjab in Pakistan and northwest India, isolates Pakistan records, exports a documented machine-readable CSV, validates the result, and calculates transparent per-site linear trends.

## Why this project

Groundwater is a critical resource for agriculture and communities in Pakistan. Long-term well observations can help describe where measured water levels have changed, while also exposing uneven observation coverage and data-quality limitations. The underlying BGS compilation spans 1884–2020 and includes 68,783 observations from 4,028 sites across the wider study region. It is a mixed Pakistan/India source; the workbook has no country column, so this project keeps wells whose BGS ID starts with `PAK` (IDs start with `PAK` or `IND`).

## Quick start (macOS / Python 3.9+)

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 scripts/prepare_dataset.py --download
python3 scripts/validate_dataset.py
python3 scripts/analyse.py --min-observations 4
python3 scripts/report.py
python3 scripts/make_kaggle_package.py
```

Or in one step: `make all`.

The download step retrieves the original BGS XLSX workbook. If the BGS endpoint is unavailable, download the workbook from the BGS dataset page and save it as `data/India_Pakistan_WL_NGDC.xlsx`, then run `python3 scripts/prepare_dataset.py`.

If the source workbook uses different column labels, inspect its header row and pass explicit column names, for example:

```bash
python3 scripts/prepare_dataset.py --site-column 'Site ID' --date-column 'Date' --depth-column 'Water Level' --country-column 'Country'
```

The importer defaults to the `Full_dataset` sheet. It accepts country values `PAK`, `PK`, or `Pakistan` when filtering `--country PAK`. It deliberately fails loudly if required fields cannot be identified or if no Pakistan records match; it does not silently treat the combined regional dataset as Pakistan-only.

## Outputs

- `data/pakistan_groundwater_observations.csv`: Pakistan-filtered observations.
- `results/site_trends.csv`: per-site observation count, period, endpoint depths, linear slope and plain-language direction.
- `results/summary.json`: row and site counts, years, coordinate coverage, depth quantiles, trend counts (|slope| < 0.1 m/year counted as about stable), sensitivity to minimum observations (4, 10, 20) and a since-2000 window.
- `results/fig_observations_per_year.png`, `results/fig_trend_histogram.png`, `results/fig_site_map.png`.
- `kaggle/1-upload-these/` and `kaggle/2-helpers/`: files for the Kaggle dataset, its field text, cover and starter notebook.

## Results (first full run, 8 November 2026)

From the BGS workbook, 58,699 rows had a usable water level (rows marked `NA` are skipped). Of these, **38,450
observations from 3,311 Pakistan wells** were kept (all IDs start with `PAK`; every row has coordinates). They span
1900-2020, but almost all fall between 1979 and 2010 (`results/fig_observations_per_year.png`). The median well has
11 observations; the median depth is 3.2 m below ground (middle half 2.0-5.0 m).

Per-well linear trends (positive = water level deeper below ground; |slope| < 0.1 m/year counted as about stable):

| Wells included | Wells | Deeper | Shallower | About stable | Median trend (m/year) |
|---|---|---|---|---|---|
| 4+ observations | 3,008 | 1,022 (34%) | 419 (14%) | 1,567 (52%) | +0.055 |
| 10+ observations | 1,750 | 648 (37%) | 48 (3%) | 1,054 (60%) | +0.071 |
| 20+ observations | 557 | 178 (32%) | 15 (3%) | 364 (65%) | +0.067 |
| Since 2000, 4+ observations | 2,054 | 575 (28%) | 577 (28%) | 902 (44%) | -0.007 |

- In wells with longer records, about a third have water levels moving deeper and only about 3% moving shallower.
- Most "shallower" wells in the first row have short records: requiring 10 observations drops them from 419 to 48.
  Short records are sensitive to when in the year they were measured.
- Since 2000 (mostly 2000-2010) deeper and shallower wells are equal in number; this window is short.
- The largest group of deeper trends is in the centre of the map, roughly 30-32 N and 72-74 E (`results/fig_site_map.png`).

These are descriptive per-well trends. They are not a test of the BGS authors' own analysis (MacAllister et al.,
2022), which uses a different method.

Kaggle dataset: <https://www.kaggle.com/datasets/muzammalhussain11/pakistan-punjab-groundwater-levels>.
Article: <https://masmatixinnovations.co.uk/insights/pakistan-punjab-groundwater.html>.

The raw BGS workbook is downloaded locally and is not committed by default. The prepared CSV is generated from the source and should only be published after validating its row count, country values, and source acknowledgement.

## Methodology

1. Read the `Full_dataset` worksheet from the BGS Excel workbook.
2. Identify the site identifier (`OW_ID`), observation date (`DATE`), groundwater level (`WL_MBGL`) and coordinates (`LAT`, `LONG`); rows with a missing level (`NA`) are skipped. Optional latitude/longitude fields are retained when present.
3. Normalize dates and numeric values; rows missing core fields are skipped.
4. Take the country from the well ID prefix (`PAK` or `IND`) and keep Pakistan only. If a future version of the source adds a country column, it is used instead.
5. Export a stable CSV schema and validate that every exported row is Pakistan-tagged.
6. For each site with at least four observations, fit ordinary least-squares depth-versus-calendar-year slope.

`depth_m` is metres below ground level. A **positive** slope means the measured water level is becoming deeper below ground at that site; a **negative** slope means it is becoming shallower. This is a descriptive site-level trend, not a direct estimate of aquifer storage, sustainable yield, or causal impact. The analysis does not pool wells into a province-wide depletion estimate.

## Research questions for the next study stage

- How do site-level trends vary spatially and temporally within Pakistan Punjab?
- How sensitive are trend classifications to minimum observation count and observation-window selection?
- Do results change when using the BGS long-term-sites (`LTS`) subset rather than the full compilation?
- How much of the apparent spatial pattern is explained by uneven monitoring density and irregular sampling?

## Reproducibility and tests

The analysis uses deterministic arithmetic and no random sampling. Unit tests cover country filtering, trend direction, flat trends, minimum-observation filtering, CSV round-tripping, and workbook import. Run:

```bash
python3 -m unittest discover -s tests -v
```

## Data dictionary

| Field | Type | Description |
|---|---|---|
| `site_id` | string | Source observation-well/site identifier. |
| `date` | ISO date | Observation date (`YYYY-MM-DD`). Year-only source values are represented as 1 January of that year. |
| `depth_m` | float | Groundwater level in metres below ground level, as provided by source. |
| `country` | string | Country code/name retained from source; output is filtered to Pakistan. |
| `latitude` | float/null | Site latitude if present in source. |
| `longitude` | float/null | Site longitude if present in source. |

Trend output fields are documented in `docs/METHODOLOGY.md`.

## Limitations and responsible interpretation

- The source is a historical compilation from multiple organizations and observation programmes; measurement frequency and temporal coverage vary.
- The regional workbook includes Indian and Pakistani records. The country filter depends on the source country field being correctly populated.
- Site coverage is not spatially uniform and must not be interpreted as a representative random sample of all Punjab groundwater.
- A rise in depth below ground is not equivalent to a quantified loss of groundwater storage. Aquifer properties, land-surface elevation, well construction, seasonality, pumping, recharge and measurement protocols matter.
- Linear trends can hide seasonal cycles, structural breaks and non-linear behaviour. They are exploratory summaries, not forecasts.
- No causal claims about climate, pumping or policy are made in this release.
- The source metadata states that BGS/NERC gives no warranty as to accuracy or fitness for a particular purpose.

## Primary data and research sources

1. MacAllister, D.J., Krishan, G., Basharat, M. & MacDonald, A.M. (2021). *A century of groundwater accumulation in Pakistan and northwest India - dataset*. NERC EDS National Geoscience Data Centre. DOI: [10.5285/150c95f7-18bf-4f66-880b-8364b7257b26](https://doi.org/10.5285/150c95f7-18bf-4f66-880b-8364b7257b26).
2. BGS dataset catalogue: <https://www2.bgs.ac.uk/nationalgeosciencedatacentre/citedData/catalogue/150c95f7-18bf-4f66-880b-8364b7257b26.html>.
3. MacAllister, D.J. et al. (2022). “A century of groundwater accumulation in Pakistan and northwest India.” *Nature Geoscience*, 15, 390–396. [https://doi.org/10.1038/s41561-022-00926-1](https://doi.org/10.1038/s41561-022-00926-1).
4. British Geological Survey, “Groundwater challenges in India and Pakistan”: <https://www.bgs.ac.uk/geology-projects/global-geological-risk/groundwater-challenges-in-india-and-pakistan/>.

## Licence and attribution

- **Code:** MIT License (see `LICENSE`).
- **Source data:** The BGS catalogue identifies the source dataset as available under the Open Government Licence and requires this acknowledgement on reproduced materials: **“Contains data supplied by permission of the Natural Environment Research Council [YEAR]”.** Retain the correct year and review the source terms before redistributing any derived data. The BGS source workbook is not bundled in this repository.
- This code licence does not relicense the underlying source observations.

## Citation

See `CITATION.cff`. Cite the BGS dataset and the 2022 Nature Geoscience paper when using source observations or discussing the published regional analysis. Cite this repository release separately once it has a public archival identifier.

## Release scope

v0.1.0 provides a reproducible import/filter/validation/site-trend baseline. v0.2.0 adds the summary, figures and Kaggle package. It does not include a province-wide risk map, a predictive model or causal conclusions. Those should be added only after source schema and Pakistan-only extraction have been independently checked.
