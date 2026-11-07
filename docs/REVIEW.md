# Review of the November 2026 exploratory notebook

The original executed notebook is preserved in Drive, including exploratory outputs. It is not the canonical release analysis.

1. **2013 exclusion:** all 88 LIGHTS values were missing. The exact VCMSLCFG product starts January 2014. The release retains 2013's measured LST/SAVI/NDBI and excludes lights from its five-year screening score. Historical zeros are marked unavailable in LIGHTS_OBSERVED.
2. **Mean/variance matching is not sensor calibration.** Forcing every year's spatial LST distribution to 2023's mean and SD removes real as well as spurious differences. No paired reference observations or physical calibration model were used. The “guaranteed” removal of seasonal/sensor artifacts is unsupported.
3. **Unchanged RF predictions:** the normalization changed LST and CLASS but passed unchanged SAVI/NDBI/LIGHTS to the same fitted RF. Thus the calibrated transition plot necessarily repeated the earlier RF predictions. It did not validate the recalibration.
4. **Duplicate polygons:** independently numbering repeated council codes by row order does not establish correspondence. The HHRI export additionally assigns `_1` to every duplicated boundary, repeating the first record. Use source-ID joins in this release instead.
5. **Health-risk claims retired:** U_R is blank in these exports and School and Area are zero throughout all 352 model records. Blank rural/urban fields defaulted to a numerical weight. Polygon area is not demographic sensitivity. The resulting HHRI is an unvalidated composite, not an IPCC-validated health model. Do not label its top five as requiring urgent health interventions.
6. **Sensitivity confounding:** the original sensitivity cell compared multiplicative and additive formulas at the same time as changing weights. The release varies only weights within one additive formulation.
7. **Labels:** Stable/Emerging/Chronic imply temporal evidence the original class assignment did not establish. Release labels are Lower/Middle/Higher relative screening score.

Remaining work for a stronger scientific study: consistent-season extraction with coverage diagnostics; defensible cross-sensor assessment; population, age and vulnerability measures with metadata; independent reference observations; spatial blocking/buffering; documented boundary provenance.
