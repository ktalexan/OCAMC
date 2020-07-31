##############################################################
# PYTHON AUTOMATED LEGAL DESCRIPTION DOCUMENT                #
# Geoprocessing Script Tool for ArcGIS Pro                   #
# Version: 1.4                                               #
# Author: Dr. Kostas Alexandridis, GISP                      #
# Organization: OC Survey Geospatial Services                #
# Date: February 2020                                        #
##############################################################


# Importing the required libraries into the project
import arcpy, os



# Declaring input parameters for the geoprocessing tool
jsonpath = arcpy.GetParameterAsText(0) # The path to the JSON response output file from AMC processing
prjpath = arcpy.GetParameterAsText(1) # The path to the project
template = arcpy.GetParameterAsText(2) # The word document template
seal = arcpy.GetParameterAsText(3) # the surveyor's seal image to be imported into the legal description
scale = arcpy.GetParameterAsText(4)
fontName = arcpy.GetParameterAsText(5)
fontSize = arcpy.GetParameter(6)
exhibitNo = arcpy.GetParameterAsText(7)
poid = arcpy.GetParameter(8)

if template == "":
    template = None
if seal == "":
    seal = None


os.chdir(prjpath)
from ald import ald



docald = ald(jsonpath, prjpath, template, seal, scale, fontName, fontSize, exhibitNo, poid)

arcpy.SetParameter(9, docald)