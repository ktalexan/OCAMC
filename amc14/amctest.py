# TR18141_REVISION2_SEPARATE_GPS.dwg
#point1 = 6118551.3820, 2197667.7252
#point2 = 6121592.6109, 2196552.2793
#tpob = [point1, point2]

#########################
# TEST CODE FOR AMC CLASS
# SINGLE PARCEL BOUNDARY
#########################


# Importing the required libraries into the project
import arcpy, os, sys, math, json, datetime, socket, pandas




# Settings for execution
cadname = "TR18141"
scale = "grid"
scalefactor = 0.99996770
tpob = None
direction = None
tolerance = 2

# Environmental variable should Exist: 'GITREPOS': 'C:\Users\ktale\source\repos\ktalexan'
prjpath = os.path.join(os.environ["GITREPOS"], "OCAMC", "amc14")
os.chdir(prjpath)
prjin = os.path.join(prjpath, "Test", "input")
outpath = os.path.join(prjpath, "Test", "output")
cadpath = os.path.join(prjin, "TR18141_REVISION2_MASTER.dwg")


warnings = []

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

