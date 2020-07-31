##############################################################
# PYTHON AUTOMATED MAP CHECKING ANALYSIS                     #
# Python Stand-Alone Execution Script                        #
# Version: 1.2                                               #
# Author: Dr. Kostas Alexandridis, GISP                      #
# Organization: OC Survey Geospatial Services                #
# Date: January 2020                                         #
##############################################################


# Importing the required libraries into the project
import arcpy, os
from tkinter import filedialog
from tkinter import *


prjpath = filedialog.askdirectory(title = "Select Project Directory")
cadpath = filedialog.askopenfilename(initialdir=os.path.split(prjpath)[0], title="Select CAD Drawing", filetypes=(("CAD Drawing","*.dwg"), ("All files", "*.*")))
outpath = filedialog.askdirectory(title = "Select Output Directory")
cadname = "TR18141"
scale = "grid"
scalefactor = 0.99996770
tpob = None
direction = None
tolerance = 2

os.chdir(prjpath)


from amc.amc import cad2amc
amc1 = cad2amc(cadpath, prjpath, outpath, cadname, scale, scalefactor, tpob, direction, tolerance)
amc1.baseChecks()
amc1.boundaryProcessing()
amc1.createLegalDescription()
jsonResponse = amc1.finalizeReport()
