#########################
# TEST CODE FOR AMC CLASS
# PHASE2 CAD DRAWING
#########################


# Importing the required libraries into the project
import arcpy, os, sys, math, json, datetime, socket, pandas




# Settings for execution
cadname = "TR18184"
scale = "grid"
scalefactor = 0.99996770
tpob = None
direction = None
tolerance = 2

# Environmental variable should Exist: 'GITREPOS': 'C:\Users\ktale\source\repos\ktalexan'
prjpath = os.path.join(os.environ["GITREPOS"], "OCAMC", "amc16")
os.chdir(prjpath)
prjin = os.path.join(prjpath, "Test", "Input")
outpath = os.path.join(prjpath, "Test", "Output")
cadpath = os.path.join(prjin, "TR18184_PHASE2.dwg")


warnings = []

from amc16 import amc

# Instantiate class object from input parameters
amc1 = amc(cadpath, prjpath, outpath, cadname, scale, scalefactor, tpob, direction, tolerance)



