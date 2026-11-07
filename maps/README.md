# Year-specific GIS layers

Each `screening_YEAR.geojson` contains 88 source polygons with attributes already joined, in longitude/latitude coordinates (GeoJSON WGS84). There are five files: 2003, 2008, 2013, 2018 and 2023.

## QGIS / ArcGIS Pro

1. Add **one** GeoJSON year as a vector layer (ArcGIS Pro can use JSON To Features if required by the installed version).
2. Check the attribute table: 88 rows, a single YEAR, unique SOURCE_ID.
3. Categorize by `RELATIVE_CLASS`: Lower = green, Middle = gold, Higher = red. `RELATIVE_SCORE` contains the continuous proposed score. These names refer to the new screening, not legacy `RF_CLASS`.
4. Include year, data sources, scale bar and a caption stating 'relative environmental screening; not health risk'.
5. Keep a separate layer for each year. If joining another table, filter it by year and verify one-to-one SOURCE_ID matches before styling.

Never join the full five-year table by WARD_NAME alone. Council names/codes repeat across years and source polygons. Colors compare polygons **within** a year, not calibrated temperatures across time. See [methods](../docs/METHODS.md) and the [report](../docs/REPORT.md).
