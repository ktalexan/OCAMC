##############################################################
# PYTHON AUTOMATED LEGAL DESCRIPTION DOCUMENT                #
# Python Stand-Alone Execution Script                        #
# Version: 1.2                                               #
# Variant: ArcGIS Pro Geoprocessing Tool                     #
# Date: January 2020                                         #
##############################################################


# Importing the required libraries
import os, arcpy, json
from tkinter import filedialog
from tkinter import *


prjpath = filedialog.askdirectory(title="Select Project Directory")
jsonpath = filedialog.askopenfilename(initialdir=os.path.split(prjpath)[0], title="Select JSON File", filetypes=(("JSON","*.json"), ("All files", "*.*")))
#template = filedialog.askopenfilename(initialdir=os.path.split(prjpath)[0], title="Select Word Template", filetypes=(("Word Template", "*.docx"), ("All files", "*.*")))
#seal = filedialog.askopenfilename(initialdir=os.path.split(prjpath)[0], title="Select Seal Image", filetypes=(("PNG image", "*.png"), ("All files", "*.*")))
scale = "ground"
fontName = "Arial"
fontSize = 10
exhibitNo = "A"
poid = 1

os.chdir(prjpath)
from amc.ald import json2ald

ldresponse = json2ald(jsonpath, prjpath, None, None, scale, fontName, fontSize, exhibitNo, poid)

os.system(f"start {ldresponse}")
