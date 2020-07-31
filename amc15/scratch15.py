# TR18141_REVISION2_SEPARATE_GPS.dwg
#point1 = 6118551.3820, 2197667.7252
#point2 = 6121592.6109, 2196552.2793
#tpob = [point1, point2]

#########################
# TEST CODE FOR AMC CLASS
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
prjpath = os.path.join(os.environ["GITREPOS"], "OCAMC", "amc15")
os.chdir(prjpath)
prjin = os.path.join(prjpath, "Test", "Input")
outpath = os.path.join(prjpath, "Test", "Output")
cadpath = os.path.join(prjin, "TR18141_REVISION3_MASTER.dwg")

warnings = []

from amc15 import amc

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






import arcpy, os, sys, math, json, datetime, socket, pandas

# Environmental variable should Exist: 'GITREPOS': 'C:\Users\ktale\source\repos\ktalexan'
prjpath = os.path.join(os.environ["GITREPOS"], "OCAMC", "amc15")
os.chdir(prjpath)
prjin = os.path.join(prjpath, "Test", "Input")
outpath = os.path.join(prjpath, "Test", "Output", "SEPARATE")
cadpath = os.path.join(prjin, "TR18141_REVISION3_SEPARATE.dwg")

gdb = os.path.join(outpath, "TR18141", "Reference.gdb")
arcpy.env.workspace = gdb
arcpy.env.OverwriteOutput = True

with arcpy.da.SearchCursor("PARCELS", ["OID@", "SHAPE@", "CentroidX", "CentroidY", "AreaSqFeet", "AreaAcres"]) as cursor1:
    for row1 in cursor1:
        oid1 = row1[0]
        print("Selected Parcel: {}".format(oid1))
        layer1 = arcpy.SelectLayerByAttribute_management("PARCELS", "NEW_SELECTION", "OBJECTID = {}".format(oid1))

        layer2 = arcpy.SelectLayerByLocation_management("PIQ", "BOUNDARY_TOUCHES", layer1, None, "NEW_SELECTION", "NOT_INVERT")

        with arcpy.da.SearchCursor(layer2, ["OID@", "SHAPE@"]) as cursor2:
            for row2 in cursor2:
                oid2 = row2[0]
                print("\t{}".format(oid2))



courselist = []
with arcpy.da.SearchCursor("PIQ", ["OID@"]) as cursor:
    for row in cursor:
        courselist.append(row[0])