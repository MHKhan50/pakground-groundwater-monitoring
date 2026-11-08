# Dataset card: Pakistan Punjab groundwater observations

## Summary

A Pakistan-filtered derivative of the BGS historical groundwater workbook. It is intended for reproducible exploratory analysis and research training, not as a complete census of groundwater conditions in Punjab.

## Source

MacAllister, D.J., Krishan, G., Basharat, M. & MacDonald, A.M. (2021), *A century of groundwater accumulation in Pakistan and northwest India - dataset*, NERC EDS NGDC, DOI: `10.5285/150c95f7-18bf-4f66-880b-8364b7257b26`.

## Geographic and temporal coverage

The parent source includes Pakistan Punjab and northwest India (Punjab and Haryana). Source observations span 1884–2020. The derivative created by this project retains Pakistan records only. Its actual row count, site count, and date range must be generated from the downloaded source; they are not pre-populated here.

## Construction

The preparation script reads the `Full_dataset` worksheet, detects required fields from documented header aliases (or explicit command-line overrides), normalizes dates and numeric values, excludes rows missing core fields, and filters the country field to Pakistan. The original workbook is not redistributed in this repository.

## Intended use

- Exploratory site-level groundwater-level trend analysis.
- Data-quality and monitoring-coverage assessment.
- Reproducible teaching and research pipeline development.

## Out-of-scope use

- Drinking-water safety decisions.
- Individual well abstraction or pumping advice.
- Province-wide depletion claims without spatial sampling correction and hydrogeological validation.
- Causal attribution to climate, irrigation, policy or pumping.

## Biases and limitations

Historical records have uneven temporal sampling, different source organizations and measurement protocols, and spatially uneven site coverage. The dataset is not a random or necessarily representative sample. The source itself disclaims warranty of accuracy/fitness. A change in depth below ground is not directly equivalent to change in groundwater storage.

## Privacy and sensitive data

No personal data is expected in the source schema. Check for unexpected personal or sensitive fields before releasing any derivative.

## Licence and attribution

The BGS catalogue lists the source dataset under the Open Government Licence, with required acknowledgement: “Contains data supplied by permission of the Natural Environment Research Council [YEAR]”. Confirm the applicable year and current terms on the BGS source page before redistribution. This derivative's repository code licence does not replace the source data licence.
