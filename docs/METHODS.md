# Methods and interpretation

## Inputs
The existing extraction uses Landsat 7 for 2003/2008, Landsat 8 for 2013/2018, and Landsat 9 for 2023. 2003 uses April 1–May 30; remaining years use June 1–July 1 (exclusive end dates). Scene counts were 6, 2, 8, 6, 8. Cloud/shadow bits were masked, optical and surface-temperature scale factors applied, and median composites created. MNDWI<0 masks water for LST, SAVI and NDBI. These historical extraction choices are documented rather than represented as newly optimized preprocessing.

Only two scenes were available in 2008. Median compositing is not proof of complete Landsat 7 SLC-off gap repair. Per-polygon valid pixel fractions and observation counts are absent. Sensor differences, clouds, water-mask behavior and nonmatching seasons remain limitations.

## Identity and joins
Each source Earth Engine feature retains a unique SOURCE_ID from the suffix of system:index. The release asserts unchanged geometry for each SOURCE_ID across years. Legacy rows were matched by YEAR, UC_C, WARD_NAME, Shape_Area and Shape_Leng with a one-to-one check. These keys are verified for this snapshot, not recommended as universal identifiers. A fresh extraction should preserve source feature IDs directly.

## Within-year relative screening
Rank each of LST, NDBI and SAVI within a year using average ranks divided by n. Score = 0.5*rank(LST) + 0.3*rank(NDBI) + 0.2*(1-rank(SAVI)). Lower/Middle/Higher categories use fixed score cutoffs 1/3 and 2/3, not tercile quotas. This preserves location ordering without pretending to physically calibrate years. It is a proposed screening index with no health-risk meaning.

## Validation
The legacy classification reproduces the earlier GroupKFold experiment using ward-name groups and the original globally constructed target. Target construction and thresholding were performed before splitting; accuracy is only conditional agreement with that target. Unseen groups are not necessarily geographically distant.

The separate regression experiment predicts original LST from SAVI and NDBI. Five-fold council-code holdout keeps all parts and years of a council together. Leave-one-year-out tests all five years. Random Forest uses 200 trees, minimum leaf size 3, seed 42. A training-mean dummy model is the reference. MAE and R² are reported per fold; summary values are unweighted means of fold metrics. No tuning on test folds was performed. Observations share spatial and temporal dependence and are not 440 independent samples.

## Sensitivity
The additive rank formulation remains fixed. Compare baseline weights (.5,.3,.2), thermal emphasis (.7,.2,.1), and vegetation emphasis (.4,.2,.4). Compare overlap/Jaccard for the top 14 polygons in 2023, tie-broken by SOURCE_ID. These scenarios do not validate causality or optimal intervention priorities.
