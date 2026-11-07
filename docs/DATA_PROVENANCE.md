# Provenance

Local analysis inputs were downloaded from the user's connected Google Drive GEE_Exports folder on 7 November 2026:

- `Multan_Heat_Vulnerability.csv` → `data/earth_engine_polygon_statistics.csv` (440 rows; original Earth Engine polygon geometry included).
- `final_vulnerability_table.csv` → `data/legacy_model_results.csv` (352 rows).

Extraction source: the user-supplied executed Colab notebook, Earth Engine project `u-h-v-assessment`, boundary asset `projects/u-h-v-assessment/assets/Multan_UCs`. Project/asset identifiers are resource names, not credentials. No authentication tokens are distributed.

Official product references:
- https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LE07_C02_T1_L2
- https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2
- https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2
- https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG
- https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html

The chosen VIIRS product begins 2014-01-01. Treat missing early lights as unavailable, not zero measured light. Official documentation recommends checking cloud-free coverage and notes remaining transient-light artifacts.

All rights in third-party source data remain with their providers. The original administrative boundary source/vintage and redistribution terms need verification; this release makes no blanket license grant for those geometries.
