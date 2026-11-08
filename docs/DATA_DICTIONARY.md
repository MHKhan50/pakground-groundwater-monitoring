# Data dictionary

## `data/pakistan_groundwater_observations.csv`

| Column | Type | Unit / format | Definition |
|---|---|---|---|
| `site_id` | string | Source identifier | Observation well/site identifier from BGS workbook. |
| `date` | string | `YYYY-MM-DD` | Date of measurement; year-only values are normalized to 1 January. |
| `depth_m` | float | metres below ground level | Groundwater level/depth as supplied by the source. |
| `country` | string | source code/name | Country value; output must be Pakistan only. |
| `latitude` | float/null | decimal degrees | Source latitude, if present. |
| `longitude` | float/null | decimal degrees | Source longitude, if present. |

## `results/site_trends.csv`

| Column | Type | Definition |
|---|---|---|
| `site_id` | string | Site identifier. |
| `n_observations` | integer | Number of valid observations used. |
| `first_year`, `last_year` | integer | First and last observation years. |
| `first_depth_m`, `last_depth_m` | float | Depth at first and last observed date. |
| `linear_trend_m_per_year` | float | OLS slope of depth against calendar year. Positive means increasing depth below ground. |
| `trend_interpretation` | category | `deeper_water_level`, `shallower_water_level`, or `approximately_stable`. |
| `latitude`, `longitude` | float/null | Coordinates from the last observation where present. |

Missing coordinates are blank in CSV. They must not be imputed without a documented method.
