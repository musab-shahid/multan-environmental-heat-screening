# Spatiotemporal Urban Heat Vulnerability Assessment — Multan, Pakistan (2003–2023)

## Portable GIS package

Extract `Multan_Heat_Screening_GIS.zip`, then open `Multan_Heat_Screening.qgz` in QGIS. Keep the `.qgz` project and `Multan_Heat_Screening.gpkg` together. The project stores relative paths and was tested after moving to a different directory.

Five layers contain the years 2003, 2008, 2013, 2018 and 2023. Only 2023 is visible initially. Turn on one year at a time. Open the corresponding `Screening YEAR` print layout to export a map. Each layer has 88 source polygons, one YEAR and unique SOURCE_ID values; no separate table join is needed.

- `RELATIVE_CLASS`: Lower (green), Middle (gold), Higher (red).
- `RELATIVE_SCORE`: the baseline within-year rank score.
- `SOURCE_ID`: stable source-feature identity.
- `UC_C`: council grouping; it is not a unique polygon identifier.

The layer CRS is EPSG:4326; layouts use EPSG:32642 with a kilometre scale and grid-north arrow. The accompanying QML files allow restoring the same style. ArcGIS Pro can read the GeoPackage layers; QGZ layouts and QML styles are QGIS-specific.

The map book is a separate public PDF. The input boundaries and attributes were already supplied with the research project; no new boundary authority or redistribution license is asserted. Colors compare locations within a year and do not measure health risk or calibrated changes through time.

## Rebuild

Run `src/build_gis.py` with a QGIS Python interpreter (tested with QGIS 3.40.3). This is separate from the scientific requirements. On Windows, a typical command is:

```powershell
& C:/OSGeo4W/bin/python-qgis.bat src/build_gis.py
```

If this machine has conflicting PROJ installations, `HEAT_PROJ_DATA` can point to a compatible PROJ data directory before launching the builder. No path override is needed in a correctly configured QGIS installation. The builder also explicitly loads installed Arial fonts on Windows for headless rendering.

For the report and combined map book, install `requirements-report.txt` and run `python src/render_report.py`. The report renderer uses installed Arial or DejaVu Sans fonts.
