# General Formatting
- **Indentation:** Always use exactly 4 spaces.
- **Spacing:** Always use spaces before and after operators (e.g., `area = length * width`).
- **Line Breaks:** Do not manually break code lines; allow the editor to wrap.

# Naming Conventions
- **Julia:** `lowercase` for variables/functions, `PascalCase` for Types/Modules.
- **Python:** `snake_case` for variables/functions, `PascalCase` for classes.
- **Geospatial Specifics:** 
    - Use `sdf_` prefix for ArcPy Spatially Enabled DataFrames or general spatial dataframes (e.g., `sdf_incident_zones`).
    - Use `gdf_` prefix specifically when using GeoPandas.
    - Use `_crs` suffix for Coordinate Reference System objects.
    - Use `_geom` for geometry columns or objects.
- **Complex Systems:** Use `model` for simulation objects and `agents` for agent collections.

# Logic & Standards
- **Naming Logic:** Suggest names reflecting physical or mathematical properties (e.g., `estimate_population_density`).
- **Tools:** Use `arcpy` for ESRI geodatabase workflows and `Agents.jl` for your Julia-based ABM simulations.
