# Changelog

## 0.2.0 - 2026-11-08

- `scripts/report.py`: summary.json (coverage, depth, trend counts with a 0.1 m/year stable band, sensitivity to
  minimum observations 4/10/20 and a since-2000 window) and three figures.
- `scripts/make_kaggle_package.py`: builds the Kaggle upload folder, field text, cover and a tested starter notebook.
- `make all` runs the full pipeline; tests cover the report and the package builder.

## 0.1.0: 2026-11-08

- Initial reproducible BGS workbook import and Pakistan-only filtering pipeline.
- Stable CSV schema, integrity validator and site-level OLS trend summary.
- Unit tests, data dictionary, dataset card, research protocol, Kaggle release checklist and citation metadata.
