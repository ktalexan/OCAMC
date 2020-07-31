##############################################################
# PYTHON AUTOMATED MAP CHECKING ANALYSIS                     #
# Geoprocessing Tool for ArcGIS Pro                          #
# Version: 1.2                                               #
# Author: Dr. Kostas Alexandridis, GISP                      #
# Organization: OC Survey Geospatial Services                #
# Date: January 2020                                         #
##############################################################


# Importing the required libraries into the project
import arcpy, os


# Declaring input parameters for the geoprocessing tool
cadpath = arcpy.GetParameterAsText(0) # The path to the project directory
prjpath = arcpy.GetParameterAsText(1) # The workspace folder path of the project directory
outpath = arcpy.GetParameterAsText(2) # The output workspace folder path to store the results
cadname = arcpy.GetParameterAsText(3) # The name of the map (tract, parcel, or record of survey)
scale = arcpy.GetParameterAsText(4) # The scale parameter, choice of 'grid' (default) or 'ground'
scalefactor = arcpy.GetParameterAsText(5) # The scale factor of the drawing, e.g., 0.99996770
tpob = arcpy.GetParameterAsText(6) # The true point of beginning (optional, default = None) - if provided must be XY coordinates
direction = arcpy.GetParameterAsText(7) # The direction of the boundary course (optional, default = None) - choose 'clockwise' or 'counter-clockwise'
tolerance = arcpy.GetParameterAsText(8) # The tolerance of the decimal points when comparing (optional, default = 2)


if tpob == "":
    tpob = None
if direction == "":
    direction = None
tolerance = int(tolerance)
scalefactor = float(scalefactor)


os.chdir(prjpath)

from amc import cad2amc

amc1 = cad2amc(cadpath, prjpath, outpath, cadname, scale, scalefactor, tpob, direction, tolerance)
amc1.baseChecks()
amc1.boundaryProcessing()
amc1.createLegalDescription()
jsonResponse = amc1.finalizeReport()
executionReport = os.path.join(outpath, cadname, "ExecutionReport.txt")
jsonOutput = os.path.join(outpath, cadname, "jsonResponse.json")
gdbpath = os.path.join(outpath, cadname, "Reference.gdb")
arcpy.env.workspace = gdbpath
arcpy.env.OverwriteOutput = True
fcGPS = arcpy.ListFeatureClasses("GPSPoints")[0]
fcTies = arcpy.ListFeatureClasses("BasisOfBearingGpsTies")[0]
fcBoundary = arcpy.ListFeatureClasses("Boundary")[0]
fcTPOB = arcpy.ListFeatureClasses("TPOB")[0]


arcpy.SetParameter(9, executionReport)
arcpy.SetParameter(10, jsonOutput)
arcpy.SetParameter(11, fcGPS)
arcpy.SetParameter(12, fcTies)
arcpy.SetParameter(13, fcBoundary)
arcpy.SetParameter(14, fcTPOB)
arcpy.SetParameter(15, jsonResponse)


