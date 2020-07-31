import arcpy, os

cadfile = arcpy.GetParameterAsText(0)
tolerance = arcpy.GetParameter(1)
scalefactor = arcpy.GetParameter(2)
#tpob = arcpy.GetParameter(3)
#tpob = arcpy.GetParameter(3)

point = arcpy.Point(arcpy.GetParameter(3))


arcpy.AddMessage("'tolerance' is Integer: {}".format(isinstance(tolerance, int)))
arcpy.AddMessage("'scalefactor' is Double: {}".format(isinstance(scalefactor, float)))
arcpy.AddMessage("TPOB: {}".format(point))