# Spatial evaluation and weighting sensitivity

This supplement uses the existing 440 observations and source geometries. It does not re-extract satellite data or change the baseline screening score.

## Geographic separation

Council parts are dissolved by UC_C in EPSG:32642. KMeans forms five blocks from council centroids with seed 42 and 20 starts; the response variable is not used. Blocks are labeled west to east for presentation. All years and parts of each council remain together.

Each block is tested once at each prespecified exclusion distance: 0, 2 and 5 km. Zero is an unbuffered geographic split. At positive distances, an entire training council is removed if its geometry comes closer than the specified distance to any test-council geometry. Thus the buffer is measured between polygon edges, not centroid pairs. Test sets are unchanged across buffer settings.

RF uses SAVI and NDBI to predict LST with 200 trees, minimum leaf size 3 and seed 42. The training-mean baseline uses identical splits. No fold-specific tuning, favorable block selection or favorable buffer selection is performed. All 15 splits and both models are reported.

| Buffer | RF mean fold MAE | Mean-baseline MAE |
| --- | ---: | ---: |
| 0 km | 2.88°C | 3.41°C |
| 2 km | 2.95°C | 3.44°C |
| 5 km | 2.99°C | 3.44°C |

At 5 km, RF fold MAE ranges from 1.96 to 4.12°C and mean fold R² is −0.18. RF has lower MAE than the baseline in four of five blocks. This supports a modest average advantage, not reliable prediction in every area. Unequal folds are averaged without size weighting, matching the earlier reporting convention; individual predictions allow alternative summaries.

The test evaluates new geographic areas within the supplied years. It does not evaluate a simultaneously unseen location and year. Buffers do not establish independent residuals, and the chosen distances are sensitivity settings rather than estimated spatial correlation ranges. Earlier leave-one-year-out performance remains worse than the baseline.

Outputs: `spatial_blocks.csv`, `spatial_split_membership.csv`, `spatial_split_checks.csv`, `spatial_predictions.csv`, `spatial_validation.csv`, `spatial_validation_summary.csv` in `results/`.

## Weight grid

All nonnegative weight triples summing to one in increments of 0.1 produce 66 scenarios per year. These include the baseline (0.5, 0.3, 0.2) and single-variable extremes. Each scenario selects 14 of 88 polygons; tied scores are ordered by SOURCE_ID. Rank ranges use average ranks for ties. Classification cutoffs remain 1/3 and 2/3.

The grid is a stress test, not a probability distribution over plausible policy weights. `top14_fraction` means selection frequency across this specific grid, not likelihood of vulnerability. Across years, minimum top-group overlap with the baseline is 10–12 of 14; maximum is 14 in every year. The baseline formula is unchanged.

Outputs: `weight_grid_scenarios.csv`, `polygon_weight_stability.csv`, `weight_grid_summary.csv`, with parameters and input hashes in `robustness_settings.json`.

## Reproduce

```sh
python src/analyze.py
python src/robustness.py
python -m unittest discover -s tests -v
```

The executed `notebooks/Analysis.ipynb` runs both analysis stages. No new Earth Engine authentication is required. The separate GIS and PDF builders are documented in `maps/README.md`.

Methodological references: [scikit-learn grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) and [Roberts et al. (2017), cross-validation for structured data](https://www.wsl.ch/lud/biodiversity_events/papers/Roberts_et_al-2017-Ecography.pdf). The implementation and selected distances are specific to this exploratory study, not a prescribed standard.
