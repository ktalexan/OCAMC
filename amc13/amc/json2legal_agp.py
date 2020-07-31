##############################################################
# PYTHON AUTOMATED LEGAL DESCRIPTION DOCUMENT                #
# Geoprocessing Tool for ArcGIS Pro                          #
# Version: 1.2                                               #
# Variant: ArcGIS Pro Geoprocessing Tool                     #
# Date: January 2020                                         #
##############################################################



# Importing the required libraries
import os, arcpy, json


# Declaring input parameters for the geoprocessing tool
jsonpath = arcpy.GetParameterAsText(0) # The path to the JSON Response from CAD to AMC Geoprocessing Tool
prjpath = arcpy.GetParameterAsText(1) # The path to the project
template = arcpy.GetParameterAsText(2) # The Word document template
seal = arcpy.GetParameterAsText(3) # The Surveyor's seal image to be imported into the legal description
scale = arcpy.GetParameterAsText(4) # The scale of the legal description document
fontName = arcpy.GetParameterAsText(5) # The font name to be used in the legal description
fontSize = arcpy.GetParameterAsText(6) # the font size to be used in the legal description
exhibitNo = arcpy.GetParameterAsText(7) # The exchibit label to be used in the titles
poid = arcpy.GetParameterAsText(8) # The parcel ID of the boundary

if template == "":
    template = None
if seal == "":
    seal = None
fontSize = int(fontSize)
poid = int(poid)

os.chdir(prjpath)
from ald import json2ald

ldresponse = json2ald(jsonpath, prjpath, template, seal, scale, fontName, fontSize, exhibitNo, poid)

arcpy.SetParameter(9, ldresponse)
