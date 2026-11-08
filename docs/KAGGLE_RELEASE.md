# Kaggle release checklist

This repository contains the reproducible pipeline and dataset documentation. The real Pakistan-only CSV is generated on the researcher's machine from the original BGS workbook; no fabricated observations are supplied in this release.

Before uploading a Kaggle dataset:

1. Run `python3 scripts/prepare_dataset.py --download`.
2. Run `python3 scripts/validate_dataset.py` and inspect the output CSV independently.
3. Record the actual row count, unique site count, date range, missing-coordinate rate, and country values. Do not copy the parent workbook's regional counts into Pakistan-only metadata.
4. Upload `data/pakistan_groundwater_observations.csv`, `docs/DATASET_CARD.md`, and `docs/DATA_DICTIONARY.md`.
5. Include the original BGS dataset DOI and required NERC acknowledgement: “Contains data supplied by permission of the Natural Environment Research Council [YEAR]”. Confirm the year and terms on the BGS catalogue before publishing.
6. Clearly label the dataset as a Pakistan-filtered derivative of a mixed Pakistan/India source.
7. Do not describe the observations as complete, spatially representative, or current beyond the source's 2020 end date.

The Kaggle dataset should not be published until these checks pass. The actual source workbook is not bundled with this software release.
