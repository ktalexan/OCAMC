##############################################################
# PYTHON AUTOMATED MAP CHECKING ANALYSIS                     #
# Geoprocessing Script Tool for ArcGIS Pro                   #
# Version: 1.4                                               #
# Author: Dr. Kostas Alexandridis, GISP                      #
# Organization: OC Survey Geospatial Services                #
# Date: February 2020                                        #
##############################################################


# Importing the required libraries into the project
import arcpy, os



# Declaring input parameters for the geoprocessing tool
cadpath = arcpy.GetParameterAsText(0) # The path to the project directory
cadname = arcpy.GetParameterAsText(1) # The name of the map (tract, parcel, or record of survey)
prjpath = arcpy.GetParameterAsText(2) # The workspace folder path of the project directory
outpath = arcpy.GetParameterAsText(3) # The output workspace folder path to store the results
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


# Load AMC python class 
from amc import amc

# Instantiate class object from input parameters
amc1 = amc(cadpath, prjpath, outpath, cadname, scale, scalefactor, tpob, direction, tolerance)
# Execute base checks method of AMC class
amc1.baseChecks()
# Execute boundary processing method of AMC class
amc1.boundaryProcessing()
# Execute legal description method of AMC class
amc1.createLegalDescription()
# Execute Excel table results of AMC class
amc1.boundaryToTable()
# Finalize AMC class execution and close report
jsonResponse = amc1.finalizeReport()

# Obtain the execution report document
reportOutput = os.path.join(outpath, cadname, "ExecutionReport.txt")
# Obtain the JSON result file
jsonOutput = os.path.join(outpath, cadname, "jsonResponse.json")
# Get the output geodatabase path
gdbOutput = os.path.join(outpath, cadname, "Reference.gdb")
# Get the excel data output path
excelOutput = os.path.join(outpath, cadname, "BoundaryData.xlsx")

# Change the current workspace to the geodatabase output path
arcpy.env.workspace = gdbOutput
arcpy.env.OverwriteOutput = True

# Get the resulting feature classes
fcBoundaryArea = arcpy.ListFeatureClasses("BoundaryArea")[0] # Boundary polygon area feature class in the geodatabase
fcGPS = arcpy.ListFeatureClasses("GPSPoints")[0] # GPS points feature class in the geodatabase
fcTies = arcpy.ListFeatureClasses("BasisOfBearingGpsTies")[0] # Basis of bearings ties line feature class in the geodatabase
fcBoundary = arcpy.ListFeatureClasses("Boundary")[0] # Boundary multilines feature class in the geodatabase
fcTPOB = arcpy.ListFeatureClasses("TPOB")[0] # True point of beginning point feature class in the geodatabase


# Final outputs for the geoprocessing script tool
arcpy.SetParameter(9, reportOutput)
arcpy.SetParameter(10, jsonOutput)
arcpy.SetParameter(11, fcBoundaryArea)
arcpy.SetParameter(12, fcGPS)
arcpy.SetParameter(13, fcTies)
arcpy.SetParameter(14, fcBoundary)
arcpy.SetParameter(15, fcTPOB)
arcpy.SetParameter(16, excelOutput)
arcpy.SetParameter(17, jsonResponse)


#========================= END OF PROGRAM =========================#

