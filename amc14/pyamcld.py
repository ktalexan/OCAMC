##############################################################
# PYTHON AUTOMATED MAP CHECKING ANALYSIS                     #
# Python Stand-Alone Execution Script                        #
# Version: 1.4                                               #
# Author: Dr. Kostas Alexandridis, GISP                      #
# Organization: OC Survey Geospatial Services                #
# Date: February 2020                                        #
##############################################################

# Importing the required libraries into the project
import arcpy, os, pandas
#import tkinter as tk
from tkinter import filedialog
from tkinter import *


#============================================================#
# PART 1: CAD AUTOMATED MAP CHECKING                         #
#============================================================#


# Generate a tkinter object that you can close
root = Tk()

# Dialog for the project directory
prjpath = filedialog.askdirectory(title = "Select Project Directory")
# Dialog for the path to the CAD drawing (.dwg)
cadpath = filedialog.askopenfilename(initialdir = os.path.split(prjpath)[0], title = "Select CAD Drawing", filetypes = (("CAD Drawing", "*.dwg"), ("All files", "*.*")))
# Dialog for the output results folder
outpath = filedialog.askdirectory(title = "Select Output Directory")

# Kill the tkinter object
root.destroy()

# Settings for execution
cadname = "TR18141"
scale = "grid"
scalefactor = 0.99996770
tpob = None
direction = None
tolerance = 2

# Change working directory to the project path
os.chdir(prjpath)

# Import the AMC class library module
from amc14.amc import amc

# Instantiate a new AMC class object
amc1 = amc(cadpath, prjpath, outpath, cadname, scale, scalefactor, tpob, direction, tolerance)
# Perform basic integrity checks for the CAD drawing
amc1.baseChecks()
# Process boundary and geometries including traverse cours
amc1.boundaryProcessing()
# Generate legal description properties for geometries
amc1.createLegalDescription()
# Write geometries to excel table
amc1.boundaryToTable()
# Finalize the report and get the JSON response string
jsonResponse = amc1.finalizeReport()




#============================================================#
# PART 2: AUTOMATED LEGAL DESCRIPTION                        #
#============================================================#


# Import the ALD function
from amc14.ald import ald

# Get the json path (created during Part 1, so, the output path is known)
jsonpath = os.path.join(outpath, cadname, "jsonResponse.json")
# The document template path
template = os.path.join(prjpath, "LDTemplate.docx")
# The surveyor's seal path
seal = os.path.join(prjpath, "SealKH.png")

# Run the ALD function and obtain the response doument
ldResponse = ald(jsonpath, prjpath, template, seal, scale="ground", fontName="Arial", fontSize=10, exhibitNo="A", poid=1)

# Open the word file
os.system("Start {}".format(ldResponse))




#========================= END OF PROGRAM =========================#

