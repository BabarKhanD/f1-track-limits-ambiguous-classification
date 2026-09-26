# Data Dictionary

Describes columns in `data/dataset_ready_for_modeling.csv` (final modeling dataset, 4,254 rows).

## Metadata columns

| Column | Type | Description |
|---|---|---|
| `year` | int | F1 season (2018–2025) |
| `race` | string | Race/event name (e.g. "Bahrain Grand Prix") |
| `session` | string | Session code: FP1, FP2, FP3, Q, SQ, S, R |
| `driver` | string | 3-letter driver code (e.g. "HAM") |
| `lap` | int | Lap number on which the incident occurred |
| `turn` | int/blank | Turn number, where extractable from the race control message |
| `label` | string | Target class: `clear_violation` or `no_advantage` |

## Telemetry features (per-lap summary statistics)

| Column | Type | Description |
|---|---|---|
| `max_speed` | float | Maximum recorded speed (km/h) during the lap |
| `min_speed` | float | Minimum recorded speed (km/h) during the lap |
| `avg_speed` | float | Average speed (km/h) during the lap |
| `max_throttle` | float | Maximum throttle application (%) during the lap |
| `avg_brake` | float | Average brake application during the lap |
| `brake_points` | int | Count of distinct braking events during the lap |

## Normalized features

| Column | Type | Description |
|---|---|---|
| `speed_ratio` | float | `max_speed` divided by the maximum `max_speed` observed across all incidents in the same session (0–1) |
| `avg_speed_ratio` | float | `avg_speed` divided by the mean `avg_speed` across all incidents in the same session |

## Context flags

| Column | Type | Description |
|---|---|---|
| `is_practice` | 0/1 | 1 if session is FP1, FP2, or FP3 |
| `is_qualifying` | 0/1 | 1 if session is Q or SQ |
| `is_race` | 0/1 | 1 if session is R |
| `is_sprint` | 0/1 | 1 if session is S |
| `post_2022_regs` | 0/1 | 1 if year ≥ 2022 (post aerodynamic regulation change) |

## Circuit indicators

| Column | Type | Description |
|---|---|---|
| `circuit_<Grand Prix Name>` | 0/1 | One-hot encoded circuit identity, one column per Grand Prix (38 total) |

## Label definitions

- **`clear_violation`**: Lap where `Deleted = True` in official FastF1 lap data, with `DeletedReason` citing a track limits infringement. Directly resulted in a lap-time penalty.
- **`no_advantage`**: Incident where race control explicitly noted the driver gained no advantage from leaving the track, or an investigation concluded with no penalty. Identified via keyword matching on official race control message text (see README for exact phrases matched).

## Known data quality notes

- 2018 season contains zero `clear_violation` rows (see README Limitations).
- 2025 season contains fewer `no_advantage` rows than expected due to evolving FIA message phrasing (see README Limitations).
- Pre-season testing sessions are excluded from this dataset.
- 93 rows with implausible telemetry (>2000 data points per lap, or average speed <50 km/h) were removed during cleaning.
