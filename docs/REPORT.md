# Spatiotemporal Urban Heat Vulnerability Assessment — Multan, Pakistan (2003–2023)


Exploratory research report | Musab Shahid | 7 November 2026

A reproducible analysis of satellite surface temperature, vegetation and built-up indicators across five benchmark years: 2003, 2008, 2013, 2018 and 2023.


## Abstract


This portfolio study reanalyzes 440 polygon-year records from 88 source polygons in Multan district. A within-year percentile score combines land-surface temperature (LST), built-up signal (NDBI) and vegetation deficit (SAVI). Source geometry identities are retained to avoid ambiguous council-name joins. All five years are included, including 2013, which was excluded from an earlier classifier because nighttime-light values were missing.

A separate Random Forest regression predicts LST from SAVI and NDBI. Mean fold MAE is 2.42 degrees Celsius under council-group holdout, compared with 3.22 for a training-mean baseline. Under year holdout it rises to 4.42, worse than the baseline of 3.68. The model therefore shows weak transfer to unseen years. The screening categories describe relative environmental conditions and are not validated health-risk classes.


## 1. Research questions and scope


How do surface-temperature and environmental indicators vary among the source polygons within each benchmark year? Can a model trained on vegetation and built-up indicators predict LST for unseen council groups or years? How sensitive are the highest screening ranks to alternative proposed weights?

The 88 polygons contain 82 unique council names/codes; multipart source features must not be counted as 88 unique councils. Repeated observations are spatially and temporally dependent. The study does not estimate population exposure, air temperature, mortality, or a calibrated long-term warming trend.


## 2. Data and extraction provenance


Inputs are the supplied Earth Engine polygon export and legacy model-results CSV. The original extraction uses Landsat Collection 2 Level 2: Landsat 7 in 2003/2008, Landsat 8 in 2013/2018 and Landsat 9 in 2023. The 2003 window is April 1-May 30; other years use June 1-July 1, with exclusive end dates. Scene counts are 6, 2, 8, 6 and 8 respectively. These are historical extraction choices, not newly harmonized inputs.

Cloud/shadow masking, scale factors, median composites and a MNDWI-based water mask were applied in the supplied workflow. Valid-pixel fractions are unavailable, and two 2008 scenes do not establish complete SLC-off gap repair. The chosen VIIRS VCMSLCFG product starts in 2014. Earlier missing or placeholder light values are not observations of zero light.


## 3. Methods


Identity: SOURCE_ID is retained from the source feature index, with unchanged geometry asserted across years. Legacy rows are joined using YEAR, UC_C, WARD_NAME, Shape_Area and Shape_Leng with one-to-one validation for this snapshot. Year-specific map layers carry their own attributes, eliminating a separate name-only CSV join.

Screening: For each year, rank each variable using average ranks divided by the number of polygons. Score = 0.5 rank(LST) + 0.3 rank(NDBI) + 0.2 [1 - rank(SAVI)]. Categories Lower, Middle and Higher use fixed cutoffs 1/3 and 2/3. They are not equal-size terciles. Weights are proposed exploratory choices, not health thresholds.

Evaluation: The LST regression uses a Random Forest with 200 trees, minimum leaf size 3 and seed 42. Five-fold council-code grouping keeps all parts and years of a council together. Leave-one-year-out evaluates transfer across time. A training-mean predictor is the baseline. Reported summaries are unweighted means of fold metrics; no test-fold tuning was performed.


## 4. Descriptive results



| Year | Polygons | Mean LST (C) | Mean SAVI |
|---|---|---|---|
| 2003 | 88 | 35.91 | 0.137 |
| 2008 | 88 | 45.24 | 0.133 |
| 2013 | 88 | 42.43 | 0.209 |
| 2018 | 88 | 40.79 | 0.173 |
| 2023 | 88 | 40.36 | 0.263 |



![Figure 1. Observed LST-SAVI associations shown separately by year. These descriptive comparisons are not estimates of a causal vegetation-cooling effect.](../figures/lst_savi_by_year.png)


Year means summarize polygon means rather than area-weighted district temperature. Differing sensors, seasons, masks and coverage limit comparison. A higher mean SAVI or lower LST in one year does not by itself establish an intervention effect.


## 5. Model evaluation and sensitivity



| Evaluation | RF MAE (C) | Baseline MAE (C) |
|---|---|---|
| Held-out council groups | 2.42 | 3.22 |
| Held-out years | 4.42 | 3.68 |



![Figure 2. Errors by held-out year. The 2003 fold is particularly difficult; the seasonal mismatch is one plausible contributor, not a demonstrated causal explanation.](../figures/temporal_generalization.png)


All five held-out-year RF R-squared values are negative. Good agreement within a mixed-year council split is therefore insufficient evidence for temporal generalization. Council-group holdout is not spatially buffered validation.

The earlier classifier achieved about 86.65% grouped accuracy in the local rerun versus 86.37% in the preceding Colab environment. Its target classes were constructed globally before splitting. This is agreement with a constructed target, not independent validation of vulnerability. Feature importance from that experiment should not be described as causal environmental drivers.

Weight sensitivity keeps the additive formulation fixed. Thermal-emphasis weights (0.7, 0.2, 0.1) and vegetation-emphasis weights (0.4, 0.2, 0.4) each retain 13 of the baseline top 14 polygons in 2023. This limited scenario comparison does not validate optimal policy priorities.


## 6. Mapping and interpretation


Open one maps/screening_YEAR.geojson at a time in QGIS or ArcGIS Pro. Attributes and geometry are already matched. Each layer has 88 source features and one year. Use the category and score fields from the layer; do not join a five-year table by ward name. Compare locations within a year. Changes in color across years are not physical warming or cooling measurements.


## 7. Spatial outputs



![Figure 3. Five separate relative screening maps. Ranking is recalculated within each year; colors have no fixed physical-temperature or health-risk meaning.](../figures/relative_screening_maps.png)



## 8. Limitations and next research steps


A stronger scientific study requires consistent-season extraction, valid-pixel and observation-count diagnostics, defensible cross-sensor comparison, and verification of boundary vintage and redistribution terms. Independent reference observations and geographically buffered validation would strengthen model assessment. Population, age, socioeconomic and health data would be required for a separately justified exposure or vulnerability study.

The earlier mean/variance matching to 2023 was not physical sensor calibration. Earlier health-risk composites used missing or uninformative fields and are retired. Original notebooks are retained as an audit trail; the release analysis and this report define the current interpretation.


## 9. Reproducibility and conclusion


Install requirements.txt and run python src/analyze.py from the repository root, or run notebooks/Analysis.ipynb. The release executes from the supplied CSVs without Earth Engine authentication. It regenerates tables, diagnostics and GeoJSON maps. Exact tested package versions are recorded in results/environment.json. The analysis notebook was executed successfully during release preparation; the original satellite extraction was not independently rerun.

This is a completed exploratory portfolio release. Its contribution is traceable polygon identity, transparent screening assumptions and an explicit demonstration of model-transfer limits. It is not a peer-reviewed publication or an operational heat-health tool.


## Sources and citation


Primary evidence: repository data/ CSVs, results/ tables, src/analyze.py, and docs/METHODS.md, REVIEW.md and DATA_PROVENANCE.md. The provenance note links the official Landsat, VIIRS and scikit-learn documentation. Third-party data rights remain with their providers; no blanket geometry license is asserted.

<link href="https://github.com/musab-shahid/multan-environmental-heat-screening" color="#146548">Repository: github.com/musab-shahid/multan-environmental-heat-screening</link>

Suggested citation: Shahid, M. (2026). Spatiotemporal Urban Heat Vulnerability Assessment — Multan, Pakistan (2003–2023): exploratory polygon-level analysis and validation audit. Research portfolio report, 7 November 2026.
