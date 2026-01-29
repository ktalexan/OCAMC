---
trigger: glob
globs: **/*.{py,jl}
---

# Science & Geospatial Standards
- **Julia:** Prioritize multiple dispatch and type stability. Use `Agents.jl` for ABM.
- **Python:** Use `snake_case` for variables/functions and `PascalCase` for classes.
- **Geospatial Specifics:** - Use `sdf_` prefix for Spatially Enabled DataFrames (ArcPy).
    - Use `gdf_` prefix for GeoPandas DataFrames.
    - Use `_crs` suffix for Coordinate Reference Systems.
    - Use `_geom` for geometry columns.
