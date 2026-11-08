# Research methodology and experiment protocol — v0.1.0

## Study design

This release is an observational, retrospective data-engineering and exploratory-statistics study. It is designed to establish a traceable Pakistan-only subset from a mixed-country historical workbook and produce site-level descriptive trends. It is not a causal study and does not estimate groundwater storage volume.

## Data provenance

Primary source: MacAllister et al. (2021), BGS/NERC NGDC dataset, DOI `10.5285/150c95f7-18bf-4f66-880b-8364b7257b26`. The source catalogue describes observations from 1884 to 2020 and two worksheets: `Full_dataset` (68,783 observations from 4,028 sites across the regional dataset) and `LTS` (7,547 observations from 130 sites meeting the source's long-term coverage criteria). These counts refer to the combined regional source, not the Pakistan-only output.

## Inclusion and exclusion

- Include rows with a non-empty site identifier, parseable date, numeric groundwater level, and country value matching Pakistan (`PAK`, `PK`, or `Pakistan`).
- Exclude rows missing any required core field.
- Preserve latitude/longitude when available; missing coordinates do not exclude a record.
- Do not infer country from coordinates, district names, or site names in v0.1.0.

## Primary analysis

For each site with at least four observations, fit an ordinary least-squares regression:

`depth_m = intercept + slope * calendar_year`

The slope is expressed in metres per year. Positive slope means measured depth below ground increases (water level is deeper); negative slope means measured depth decreases (water level is shallower). The slope is a descriptive statistic for the observed site/time window only.

## Planned robustness experiments (not run by this code release)

These are prespecified follow-on analyses; no outcomes are asserted here.

1. Minimum-observation sensitivity: compare thresholds of 3, 4, 6 and 10 observations.
2. Temporal-window sensitivity: compare full available record with common windows (e.g. 1970–2000 and 2001–2020), only where enough observations exist.
3. Full versus long-term subset: repeat extraction from `LTS` and compare coverage and trend distributions.
4. Robust trend estimation: compare OLS with Theil–Sen slopes and Mann–Kendall tests in a later version, including multiple-testing considerations.
5. Spatial representativeness: map observation density before interpreting spatial patterns; report districts/areas with sparse or absent observations.
6. Seasonal confounding: where month/season information is reliable, stratify pre-/post-monsoon observations rather than mixing them indiscriminately.

## Quality assurance

Automated tests verify country filtering, date/depth parsing paths, trend direction, stable series, minimum observation count, workbook header detection and CSV round-trip. The validation script checks that output contains only Pakistan-tagged rows and has the expected schema. Researchers should additionally inspect source headers, country categories, duplicates, coordinate ranges, date distribution and site counts before publication.

## Results policy

No empirical result is included in this release because the source workbook could not be bundled or independently executed in this environment. Run the pipeline against the original BGS workbook and report actual output counts and diagnostics. Never substitute the regional BGS row counts for Pakistan-only counts. Never describe a site-level depth trend as province-wide depletion without a defensible sampling and hydrogeological model.
