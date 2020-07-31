import os, arcpy

workspace = arcpy.env.workspace
workspace2 = os.path.split(arcpy.env.workspace)[0]

arcpy.SetParameter(0, workspace)
arcpy.SetParameter(1, workspace2)