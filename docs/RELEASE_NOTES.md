# November 9 research and GIS release

Added geographic block validation with 0, 2 and 5 km exclusion distances, retaining entire councils and all their years. Added 66 weight scenarios for each of five years and per-polygon rank/selection summaries. Six tests pass; both scientific stages have executed in the release notebook.

The baseline score, five historical extraction windows and source inputs are unchanged. The existing council-group and year-holdout evaluations remain available. Spatial separation is now tested explicitly; temporal transfer remains weak.

The research report has been expanded to seven pages with the new design, results and interpretation. A five-page map book and portable QGIS package use the current screening fields. Each map layer contains exactly one year and 88 unique SOURCE_ID values. The QGIS project was reopened successfully after relocation with its GeoPackage.

Historical RF maps and original notebooks remain archived. The current package includes 2013 screening results; it does not relabel missing legacy RF predictions as observed data. Current public files replace the earlier report and add new artifacts; original inputs are preserved.

Research by Musab Shahid, with AI-assisted code development, verification and editorial work for this release. This is an exploratory portfolio study, not an independently validated heat-health model.
