##############################################################
# PYTHON AUTOMATED MAP CHECKING ANALYSIS                     #
# AMC Class Definition                                       #
# Version: 1.5                                               #
# Author: Dr. Kostas Alexandridis, GISP                      #
# Organization: OC Survey Geospatial Services                #
# Date: February 2020                                        #
##############################################################


# Importing the required libraries into the project
import arcpy, os, sys, math, json, datetime, socket, pandas




#============================================================#
#  MAIN CLASS: amc                                           #
#============================================================#


class amc(object):
    """
    Class AMC: This class contains a number of functions, methods and processes for Automated Map Checking analysis using CAD drawings.


    INPUT
        cadname: the name of the CAD drawing (without the file extension).
        scale: the scale used for the drawing. It can be 'grid' or 'ground'
        scalefactor: the single scale conversion factor (from ground to grid and vice versa)
        cadpath: the path to the CAD drawing (.dwg)
        prjpath: the path to the project directory
        tpob: (optional) user input that overrides the TPOB point layer in the CAD drawing, or if it does not exist in the CAD drawing (default = None).
        direction: (optional) user input defining the direction (clockwise or counter-clockwise) for the boundary course path (default = None). When default, the program uses clockwise direction.
        tolerance: (optional) the decimal accuracy to check geometry coordinates and against County database (default = 2). When default, then the accuracy is 1/100th of a foot.

    OUTPUT
        Reference.gdb: geodatabase conatining all the separate, checked, and corrected layers of the CAD drawing's geometry. These include boundaries (with correct directional geometries); geodetic horizontal control points (checked and verified with corrected geometry if needed); lot lines, centerlines, geodetic ties, etc.
        jsonResponse.json: a JSON-formatted string, containing four sessions:
            (a) jsonResponse['Checks']: containing the results of the validation/verification tests performed during execution of script with Pass/Fail (Layer Checks, Boundary Checks and Corrections, Boundary Line Checks, Boundary Closure Checks, Geometry Correction Checks, Geodetic Control Point Checks, TPOB Check, Location Check, Map Geometry Check).
            (b) jsonResponse['Boundaries']: containing the key geometric, mathematical, and descriptive attributes for each of the lines in the boundary course. These include start, mid, and end points, chords and chordal attributes, radial centers (for arcs), bearing and distances (for lines and arcs), curves, and the description to be used in the legal description document.
            (c) jsonResponse['Controls']: containing key map attributes for the CAD drawing. These include the map calculated location, city, county, state, the verified geodetic GPS control points, the TPOB coordinates, the boundary areas, and the parcels/lots.
            (d) jsonResponse['LegalDescription']: containing the three-part strings of the legal description document: the map description, the preamp (from commencement point to the point of beginning of the traverse course), and the main traverse course (from point of beginning or TPOB and back to start).
        Reference.docx: a correctly formatted legal description document corresponding to the validated and checked geometry of the CAD drawing. The legal description provided in this document passes the checks performed during the execution of the script.
    """


    #========================= PART I: CLASS INITIALIZATION =========================#

    def __init__(self, cadpath, prjpath, outpath, cadname, scale, scalefactor, tpob=None, direction=None, tolerance=2):
        """
        Function Class Initalization (AMC): Returns an amc class object for further processing.

        INPUT
            cadname: the name of the CAD drawing (without the file extension).
            scale: the scale used for the drawing. It can be 'grid' or 'ground'
            scalefactor: the single scale conversion factor (from ground to grid and vice versa)
            cadpath: the path to the CAD drawing (.dwg)
            prjpath: the path to the project directory
            tpob: (optional) user input that overrides the TPOB point layer in the CAD drawing, or if it does not exist in the CAD drawing (default = None).
            direction: (optional) user input defining the direction (clockwise or counter-clockwise) for the boundary course path (default = None). When default, the program uses clockwise direction.
            tolerance: (optional) the decimal accuracy to check geometry coordinates and against County database (default = 2). When default, then the accuracy is 1/100th of a foot.
        OUTPUT
            client: an amc class object
        NOTES
            This function runs on instantiation of class.
        """

        # Class Version and Author
        self.__version__ = "1.5.dev1"
        self.__author__ = "Dr. Kostas Alexandridis"
        arcpy.AddMessage("Automated Map Checking (AMC) Python Class")
        arcpy.AddMessage(self.__version__)
        arcpy.AddMessage(self.__author__)

        # Python Class and Version
        self.pyclass = "AMC"
        self.computer = os.environ["COMPUTERNAME"]
        self.domain = os.environ["USERDOMAIN"]
        self.condaenv = os.environ["CONDA_DEFAULT_ENV"]
        self.sysver = sys.version

        # Initiate global class variables from definitions
        self.cadname = cadname
        self.scale = scale
        self.scalefactor = scalefactor
        self.cadpath = cadpath
        self.prjpath = prjpath
        self.tpob = tpob
        self.direction = direction
        self.tolerance = tolerance
        self.warnings = []

        # The output path of the project
        self.outpath = os.path.join(outpath, self.cadname)
        # Check if the folder exist. If not, create new directory
        if not os.path.exists(self.outpath):
            os.makedirs(self.outpath)
        # Change the project's directory to the output path defined above
        os.chdir(self.outpath)

        # Define the project's geodatabase path
        self.gdbpath = os.path.join(self.outpath, 'Reference.gdb')

        # Create a new execution report:
        self.report = "ExecutionReport.txt"
        f = open(self.report, "w+", encoding = "utf8")
        f.write("{:^80s}\n".format("EXECUTION REPORT"))
        f.write("{:^80s}\n".format("County of Orange, OC Survey Geospatial Services"))
        self.now = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        f.write("{:^80s}\n\n".format("Python Class {} {}, {} Execution Date and Time: {}".format(self.pyclass, self.__version__, self.__author__, self.now)))
        f.close()

        return




    #========================= PART II: MAIN CLASS FUNCTIONS =========================#


    #-------------------- AMC Class Function: Base Checks --------------------#
    def baseChecks(self):
        """
        AMC Class Function: Import CAD Drawing and perform basic Checks
        Imports the CAD drawing and performs basic layer and geometry checks
        """

        self.appendReport("\n{:-^80s}\n".format(" PART 1: AMC BASE CHECKS EXECUTION "))
        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("Script started on: {}\n".format(stime))

        # Define new json to hold code execution data:
        self.jsonExecution = {}
        self.jsonExecution["Class"] = self.pyclass
        self.jsonExecution["Version"] = self.__version__
        self.jsonExecution["Author"] = self.__author__
        self.jsonExecution["DateTime"] = self.now
        self.jsonExecution["Workstation"] = self.computer
        self.jsonExecution["Domain"] = self.domain
        self.jsonExecution["CondaEnv"] = self.condaenv
        self.jsonExecution["PythonVer"] = self.sysver

        #Define new json to hold record checks:
        self.jsonChecks = {} # JSON Part 1 - checks
        self.jsonChecks["LayerChecks"] = {}
        self.jsonChecks["BoundaryChecks"] = {}
        self.jsonChecks["BoundaryCorrections"] = {}
        self.jsonChecks["BoundaryLines"] = {}
        self.jsonChecks["BoundaryClosure"] = {}
        self.jsonChecks["GeometryCorrections"] = {}
        self.jsonChecks["GPSChecks"] = {}
        self.jsonChecks["GeodeticControlPoints"] = {}
        self.jsonChecks["TPOB"] = {}
        self.jsonChecks["Location"] = {}
        self.jsonChecks["MapGeometry"] = {}

        self.jsonControls = {} # JSON Part 2 - controls
        self.jsonControls["Title"] = self.cadname
        self.jsonControls["ScaleFactor"] = self.scalefactor
        self.jsonControls["MapType"] = {}
        self.jsonControls["MapID"] = {}
        self.jsonControls["MapBookType"] = {}
        self.jsonControls["Book"] = {}
        self.jsonControls["Book"]["No"] = "<Book No.>"
        self.jsonControls["Book"]["Pages"] = "<Pages>"
        self.jsonControls["Registration"] = {}
        self.jsonControls["Registration"]["EngCo"] = {}
        self.jsonControls["Registration"]["EngSurveyorName"] = {}
        self.jsonControls["Registration"]["EngSurveyorNumber"] = {}
        self.jsonControls["Location"] = {}
        self.jsonControls["Location"]["Type"] = {}
        self.jsonControls["Location"]["Name"] = {}
        self.jsonControls["Location"]["County"] = {}
        self.jsonControls["Location"]["State"] = "California"
        self.jsonControls["GPS"] = {}
        self.jsonControls["Centroid"] = {}
        self.jsonControls["Areas"] = {}
        self.jsonControls["TPOB"] = {}

        self.jsonBoundary = {} # JSON Part 3 - boundaries
        self.jsonLegalDescription = {} # JSON Part 4 - legal description

        # Tract Map, Parcel Map or Record of Survey Map
        if "TR" in self.cadname:
            self.maptype = "Tract"
            self.mapid = self.cadname.split("TR")[1]
            self.mapbooktype = "Miscellaneous Maps"
        elif "PM" in self.cadname:
            self.maptype = "Parcel"
            self.mapid = self.cadname.split("PM")[1]
            self.mapbooktype = "Parcel Maps"
        elif "RS" in self.cadname:
            self.maptype = "Record of Survey"
            self.mapid = self.cadname.split("RS")[1]
            self.mapbooktype = "Records of Survey"
        else:
            self.maptype = None
            self.mapid = None
            self.mapbooktype = None

        # Populate the JSON Controls with the map information data for the project
        self.jsonControls["MapType"] = self.maptype
        self.jsonControls["MapID"] = self.mapid
        self.jsonControls["MapBookType"] = self.mapbooktype

        # Append the report with the map information data.
        self.appendReport("Identifying Map Characteristics from CAD drawing: \n\tMap Type: {}\n\tMap ID: {}\n\tMap Book Type: {}\n".format(self.jsonControls["MapType"], self.jsonControls["MapID"], self.jsonControls["MapBookType"]))

        # Define the project"s spatial reference: NAD83 State Plane California Zone 6
        self.sr = arcpy.SpatialReference(102646)
        self.appendReport("Setting Spatial Reference: NAD83 State Plane California Zone 6 (ArcGIS ID: 102646)\n")

        # Set the initial workspace for the project"s folder
        arcpy.env.workspace = self.outpath
        arcpy.env.OverwriteOutput = True

        # Determine if the computer is on the PFRDNET domain:
        if "PFRDNET" in socket.getfqdn():
            # Create a server geodatabase connection (for checks)
            self.appendReport("Creating a server geodatabase connection:")
            if os.path.exists("SPOCDSQL1205.sde"):
                os.remove("SPOCDSQL1205.sde")
                self.appendReport("\tConnection already exists: removing")
            self.ocserver = arcpy.CreateDatabaseConnection_management(self.outpath, "SPOCDSQL1205.sde", "SQL_SERVER", "10.108.9.5", "DATABASE_AUTH", "OCDataViewer", "geospatial12!", "SAVE_USERNAME")[0]
            self.appendReport("\tConnection successfully created: SPOCDSQL1205.sde\n")
        else:
            self.appendReport("Geodatabase connection SPOCDSQL1205.sde not found. Script outside OCPW Domain.\n")
            self.ocserver = None

        # Check 1: Create new geodatabase
        self.checkGDB()

        # Change the arcpy workspace to the project"s geodatabase
        arcpy.env.workspace = self.gdbpath
        arcpy.env.OverwriteOutput = True

        # Import the CAD drawing into the project geodatabase
        self.appendReport("Added CAD drawing to geodatabase.")
        arcpy.CADToGeodatabase_conversion(self.cadpath, self.gdbpath, "CAD", "1000", self.sr)
        self.appendReport(self.getAgpMsg(1))
        self.appendReport(self.getAgpMsg(1))

        # Check 2: Check for the presence of all the layers in CAD drawing
        self.checkLayers()

        # For the layers that passed the check, create new feature classes (also runs check 6 - checkClosureCentroid for boundary processing)
        self.createFeatureClasses()

        # Check 3: Check for the GPS Control Points in CAD drawing
        self.checkGPS()

        # Check 3a: Check for geodetic control geometries
        self.checkGeodeticControls()

        # Check 4: Check for the (True) Point of Beginning
        self.checkPOB()

        # Check 5: Checking boundary layers
        self.checkEBL()

        # Check 6: Checks for closure
        # Runs as part of the check 2 now.

        # Check 7: Checks for locations
        self.checkLocation()

        # Check 8: Check Maps
        if self.maptype == "Tract":
            self.checkServerTractMaps()
        elif self.maptype == "Parcel":
            self.checkServerParcelMaps()
        elif self.maptype == "Record of Survey":
            self.checkServerRecordsOfSurvey()

        # Get the number of boundary parcels
        self.nParcels = self.jsonControls["Parcels"] = int(arcpy.GetCount_management("PARCELS")[0])
        self.appendReport("Number of parcels in boundary area: {}\n".format(self.nParcels))

        # Get the course data
        self.traverseCourse()

        # Check the boundary geometry and correct if needed
        self.correctBoundaryGeometry()

        etime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("Script completed on: {}\n\n".format(etime))

        return 








    #---------- AMC Class Function: Boundary Processing ----------#

    def boundaryProcessing(self):
        """
        AMC Class Function: Processing CAD Boundaries
        This function processes the Boundaries of the CAD drawing and performs basic checks. It also processes the boundary multiline features, create fields in the geodatabase's feature class, mathematically computes bearing, distances, radial angles, etc, for annotation labels and legal descriptions.
        """
        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("\n{:-^80s}\n".format(" PART 2: AMC BOUNDARY FEATURE PROCESSING "))
        self.appendReport("Script Started on: {}\n".format(stime))

        self.appendReport("Processing Boundary Features for {}".format(self.cadname))

        # Create fields in boundary feature class to hold types and coordinates
        boundaryFields = [["loid", "LONG", "", "Line ID"],
                          ["coid", "LONG", "", "Course ID"], 
                          ["poid", "LONG", "", "Parcel ID"],
                          ["tpob", "TEXT", "", "TPOB Present"],
                          ["shapetype", "TEXT", "", "Shape Type"], 
                          ["wkt", "TEXT", "3000", "Well Known Text (WKT) Geometry"],
                          ["nwkt", "LONG", "", "Points in WKT Geometry"],
                          ["startx", "DOUBLE", "", "Startpoint X"], 
                          ["starty", "DOUBLE", "", "Startpoint Y"], 
                          ["midx", "DOUBLE", "", "Midpoint X"], 
                          ["midy", "DOUBLE", "", "Midpoint Y"], 
                          ["endx", "DOUBLE", "", "Endpoint X"], 
                          ["endy", "DOUBLE", "", "Endpoint Y"], 
                          ["midchordx", "DOUBLE", "", "Mid-chord X"],
                          ["midchordy", "DOUBLE", "", "Mid-chord Y"],
                          ["centerx", "DOUBLE", "", "Radial Center X"],
                          ["centery", "DOUBLE", "", "Radial Center Y"],
                          ["bearing", "DOUBLE", "", "Line Bearing or Chord Bearing"],
                          ["distance", "DOUBLE", "", "Line Distance or Chord Length"],
                          ["height", "DOUBLE", "", "Height of Line/Arc"],
                          ["arclength", "DOUBLE", "", "Arc Length"],
                          ["radius", "DOUBLE", "", "Arc Radius"],
                          ["midbearing", "DOUBLE", "", "Mid-chord Bearing to Center"],
                          ["delta", "DOUBLE", "", "Radial Curve Angle"],
                          ["radbearing_cs", "DOUBLE", "", "Radial Bearing: Center to Start"],
                          ["radbearing_sc", "DOUBLE", "", "Radial Bearing: Start to Center"],
                          ["radbearing_ce", "DOUBLE", "", "Radial Bearing: Center to End"],
                          ["radbearing_st", "DOUBLE", "", "Radial Tangent Angle at Start"],
                          ["radtangent", "TEXT", "", "Radial Tangent Description"],
                          ["desc_grid", "TEXT", "3000", "Legal Description (Grid)"],
                          ["desc_ground", "TEXT", "3000", "Legal Description (Ground)"],
                          ["ann_grid", "TEXT", "", "Annotation (Grid)"],
                          ["ann_ground", "TEXT", "", "Annotation (Ground)"],
                          ["annweb_grid", "TEXT", "", "Web Annotation (Grid)"],
                          ["annweb_ground", "TEXT", "", "Web Annotation (Ground)"]]

        # Add fields to Boundary feature class table
        for field in boundaryFields:
            arcpy.AddField_management("PIQ", field_name = field[0], field_type = field[1], field_length = field[2], field_alias = field[3])

        self.appendReport("\tAdded {} new fields to boundary feature class".format(len(boundaryFields)))

        # Check boundary closure and populate types and coordinates
        with arcpy.da.UpdateCursor("PIQ", ["OID@", "SHAPE@"] + [field[0] for field in boundaryFields]) as cursor:

            # Create empty JSON string to hold results of the loop
            self.jsonBoundary = {}
            # Define fields for JSON data string structure
            jsonFields = ["coid", "poid", "tpob", "shapetype", "wkt", "nwkt", "wktpoints", "startx", "starty", "midx", "midy", "endx", "endy", "midchordx", "midchordy", "centerx", "centery", "bearing", "distance", "height", "arclength", "radius", "midbearing", "delta", "radbearing_cs", "radbearing_sc", "radbearing_ce", "radbearing_st", "radtangent", "desc_grid", "desc_ground", "ann_grid", "ann_ground", "annweb_grid", "annweb_ground"]

            # Loop through lines in feature"s multilines
            for row in cursor:
                oid = row[0]
                coid = row[2]
                self.jsonBoundary[oid] = {} # Indexing from OBJECTID
            
                # Create empty JSON structure for each oid
                for field in jsonFields:
                    self.jsonBoundary[oid][field] = {}

                # Loop all fields and create an empty JSON data structure for each OID
                self.jsonBoundary[oid]["coid"] = coid

                #----------Current Feature----------

                # Start point coordinates
                start = startx, starty = row[1].firstPoint.X, row[1].firstPoint.Y
                row[8], row[9] = self.jsonBoundary[oid]["startx"], self.jsonBoundary[oid]["starty"] = start

                # Mid point coordinates
                mid = midx, midy = row[1].positionAlongLine(0.5, True).firstPoint.X, row[1].positionAlongLine(0.5, True).firstPoint.Y
                row[10], row[11] = self.jsonBoundary[oid]["midx"], self.jsonBoundary[oid]["midy"] = mid

                # End point coordinates
                end = endx, endy = row[1].lastPoint.X, row[1].lastPoint.Y
                row[12], row[13] = self.jsonBoundary[oid]["endx"], self.jsonBoundary[oid]["endy"] = end

                # Mid-chord coordinates
                midchord = midchordx, midchordy = (startx + endx)/2, (starty + endy)/2
                row[14], row[15] = self.jsonBoundary[oid]["midchordx"], self.jsonBoundary[oid]["midchordy"] = midchord

                # Line bearing or chord bearing
                bearing = math.degrees(math.atan2(endx - startx, endy - starty)) % 360
                row[18] = self.jsonBoundary[oid]["bearing"] = bearing

                # Line distance or chord length
                distance = math.hypot(endx - startx, endy - starty)
                row[19] = self.jsonBoundary[oid]["distance"] = distance


                # Mid-chord bearing
                midbearing = math.degrees(math.atan2(midchordx - midx, midchordy - midy)) % 360
                row[23] = self.jsonBoundary[oid]["midbearing"] = midbearing

                # Height of Line/Arc
                height = math.hypot(midchordx - midx, midchordy - midy)
                row[20] = self.jsonBoundary[oid]["height"] = height


                # Determine shape type and compute variables for lines and curves

                if height == 0: 
                    # This is a line
                    shapetype = "Line"
                    row[5] = self.jsonBoundary[oid]["shapetype"] = shapetype

                elif height > 0: 
                    # This is a curve
                    shapetype = "Curve"
                    row[5] = self.jsonBoundary[oid]["shapetype"] = shapetype

                    # Arc radius length
                    radius = (height / 2) + ((distance ** 2) / (8 * height))
                    row[22] = self.jsonBoundary[oid]["radius"] = radius

                    # Curve angle (delta)
                    if height > (distance / 2): # below the diameter (more than half circle, e.g., cul-de-sac)
                        delta = (360 - math.degrees(2 * math.asin(distance / (2 * radius)))) % 360
                    else: # above or at the diamerer (less or equal of half  circle)
                        delta = math.degrees( 2 * math.asin(distance / (2 * radius))) % 360
                    row[24] = self.jsonBoundary[oid]["delta"] = delta

                    # The coordinates of the center of the arc/curve
                    center = centerx, centery = midx + (math.sin(math.radians(float(bearing))) * float(radius)), midy + (math.cos(math.radians(float(bearing))) * float(radius))
                    row[16], row[17] = self.jsonBoundary[oid]["centerx"], self.jsonBoundary[oid]["centery"] = center

                    # Tangent Check:
                    radbearing_cs = math.degrees(math.atan2(startx - centerx, starty - centery)) % 360 # Radial bearing: center to start
                    row[25] = self.jsonBoundary[oid]["radbearing_cs"] = radbearing_cs
                    radbearing_sc = math.degrees(math.atan2(centerx - startx, centery - starty)) % 360 # Radial bearing: start to center
                    row[26] = self.jsonBoundary[oid]["radbearing_sc"] = radbearing_sc
                    radbearing_ce = math.degrees(math.atan2(endx - centerx, endy - centery)) % 360 # Radial bearing: center to end
                    row[27] = self.jsonBoundary[oid]["radbearing_ce"] = radbearing_ce
                    radbearing_st = (90 + radbearing_cs) % 360 # Radial Tangent Angle at start
                    row[28] = self.jsonBoundary[oid]["radbearing_st"] = radbearing_st

                    # Calculate arc length:
                    arclength = (2 * math.pi * radius) * (delta / 360) # Arc Length
                    row[21] = self.jsonBoundary[oid]["arclength"] = arclength



                # Match the TPOB with the boundary files:

                # Single TPOB
                if self.jsonControls["TPOB"]["count"] == 1:
                    coortpob = self.truncate(self.jsonControls["TPOB"]["points"][1]["x"], self.tolerance), self.truncate(self.jsonControls["TPOB"]["points"][1]["y"], self.tolerance)
                    coorstart = self.truncate(startx, self.tolerance), self.truncate(starty, self.tolerance)
                    if coortpob == coorstart:
                        row[4] = self.jsonBoundary[oid]["tpob"] = True
                    else:
                        row[4] = self.jsonBoundary[oid]["tpob"] = False

                # Multiple TPOB
                elif self.jsonControls["TPOB"]["count"] > 1:
                    for i in self.jsonControls["TPOB"]["points"]:
                        coortpob = self.truncate(self.jsonControls["TPOB"]["points"][i]["x"], self.tolerance), self.truncate(self.jsonControls["TPOB"]["points"][i]["y"], self.tolerance)
                        coorstart = self.truncate(startx, self.tolerance), self.truncate(starty, self.tolerance)
                        if coortpob == coorstart:
                            row[4] = self.jsonBoundary[oid]["tpob"] = True
                        else:
                            row[4] = self.jsonBoundary[oid]["tpob"] = False


                # Well Known Text (WKT) from object"s geometry
                wkt = row[1].WKT
                row[6] = self.jsonBoundary[oid]["wkt"] = wkt

                # Convert WKT to array format
                wktpoints = [i.split(" ") for i in wkt.split("((")[1].split("))")[0].split(", ")]
                # if float needed (to be tested use the code below)
                wktpoints = [[float(j) for j in i] for i in wktpoints]
                self.jsonBoundary[oid]["wktpoints"] = wktpoints
            
                # List and number of points in WKT
                wktlist = wkt.split("((")[1].split("))")[0].replace(" 0, ",",").replace(" 0", "").split(",")
                nwkt = len(wktlist) # Number of points in WKT geometry
                row[7] = self.jsonBoundary[oid]["wktcount"] = nwkt

                cursor.updateRow(row)


        self.appendReport("\tCalculated and populated new fields in boundary feature class")


        # Repeat the same loop after writing all the previous fields and variables
        with arcpy.da.UpdateCursor("PIQ", ["OID@", "SHAPE@"] + [field[0] for field in boundaryFields]) as cursor:
            for row in cursor:
                oid = row[0]
                coid = row[2]
                # Total number of features in feature class:
                nrows = int(arcpy.GetCount_management("PIQ")[0])

                # Get the last feature from the current one looping:
                if coid == 1:
                    lcoid = nrows # Last coid
                elif coid > 1:
                    lcoid = coid - 1

                #---------- Current Feature ----------

                # Get shapetype, start, mid, end, chordlength, midchord and height from feature attributes
                shapetype = row[5]
                start = startx, starty = row[8], row[9]
                mid = midx, midy = row[10], row[11]
                end = endx, endy = row[12], row[13]
                midchord = midchordx, midchordy = row[14], row[15]
                center = centerx, centery = row[16], row[17]
                bearing = row[18]
                distance = row[19]            
                height = row[20]
                arclength = row[21]
                radius = row[22]
                midbearing = row[23]
                delta = row[24]
                radbearing_cs = row[25]
                radbearing_sc = row[26]
                radbearing_ce = row[27]
                radbearing_st = row[28]



                # Get the preamp for the description
                if self.jsonBoundary[oid]["tpob"] is True:
                    preamp = "Thence from said {}".format(self.tpobstring)
                else:
                    preamp = " Thence"

                # Get the closing for the description
                if coid == nrows:
                    closing = " to the {}".format(self.tpobstring)
                else:
                    closing = ""


                # If current feature is a line:
                if shapetype == "Line":

                    # Get the line description string depending on the bearing direction
                    if 0 <= bearing <= 90:
                        dbearing = "North {} East".format(self.dd2dms(bearing))
                        abearing = "N {} E".format(self.dd2dms(bearing))
                    elif 90 < bearing <= 180:
                        dbearing = "South {} East".format(self.dd2dms(180 - bearing))
                        abearing = "S {} E".format(self.dd2dms(180 - bearing))
                    elif 180 < bearing <= 270:
                        dbearing = "South {} West".format(self.dd2dms(bearing - 180))
                        abearing = "S {} W".format(self.dd2dms(bearing - 180))
                    elif 270 < bearing <= 360:
                        dbearing = "North {} West".format(self.dd2dms(360 - bearing))
                        abearing = "N {} W".format(self.dd2dms(360 - bearing))

                    # Legal description (line)
                    desc_grid = "{} {}, {:.2f} feet;{}".format(preamp, dbearing, self.truncate(distance, self.tolerance), closing)
                    desc_ground = "{} {} {:.2f} feet;{}".format(preamp, dbearing, self.truncate(distance/self.scalefactor, self.tolerance), closing)
                    row[30] = self.jsonBoundary[oid]["desc_grid"] = desc_grid
                    row[31] = self.jsonBoundary[oid]["desc_ground"] = desc_ground

                    # Annotation (line) for labels and web use
                    ann_grid = "{}  {:.2f}".format(abearing, self.truncate(distance, self.tolerance))
                    ann_ground = "{}  {:.2f}".format(abearing, self.truncate(distance/self.scalefactor, self.tolerance))
                    row[32] = self.jsonBoundary[oid]["ann_grid"] = ann_grid
                    row[33] = self.jsonBoundary[oid]["ann_ground"] = ann_ground
                    annweb_grid = "{}\n{:.2f}".format(abearing, self.truncate(distance, self.tolerance))
                    annweb_ground = "{}\n{:.2f}".format(abearing, self.truncate(distance/self.scalefactor, self.tolerance))
                    row[34] = self.jsonBoundary[oid]["annweb_grid"] = annweb_grid
                    row[35] = self.jsonBoundary[oid]["annweb_ground"] = annweb_ground


                # Else, if current feature is a curve:
                elif shapetype == "Curve":

                    # Premp for description
                    if self.jsonBoundary[oid]["tpob"] is False:
                        preamp = ""

                    # Get the characteristics of the previous (last) feature
                    with arcpy.da.SearchCursor("PIQ", ["OID@", "SHAPE@"] + [field[0] for field in boundaryFields]) as lcursor:
                        for lrow in lcursor:
                            if lrow[2] == lcoid:
                                loid = lrow[0]
                                ltpob = lrow[4]
                                lshapetype = lrow[5]
                                lstart = lstartx, lstarty = lrow[8], lrow[9]
                                lmid = lmidx, lmidy = lrow[10], lrow[11]
                                lend = lendx, lendy = lrow[12], lrow[13]
                                lmidchord = lmidchordx, lmidchordy = lrow[14], lrow[15]
                                lcenter = lcenterx, lcentery = lrow[16], lrow[17]
                                lbearing = lrow[18]
                                ldistance = lrow[19]
                                lheight = lrow[20]
                                larclength = lrow[21]
                                lradius = lrow[22]
                                lmidbearing = lrow[23]
                                ldelta = lrow[24]
                                lradbearing_cs = lrow[25]
                                lradbearing_sc = lrow[26]
                                lradbearing_ce = lrow[27]
                                lradbearing_st = lrow[28]


                    # Determine the last shape:
                    if lshapetype == "Line":
                        # if the line bearing equals to the tangent bearing of the center-to-startpoint angle
                        if self.truncate(radbearing_st, self.tolerance) == self.truncate(lbearing, self.tolerance):
                            radtangent = "Tangent"
                        else:
                            radtangent = "Non-Tangent"

                    elif lshapetype == "Curve":
                        if self.truncate(radbearing_cs, self.tolerance) == self.truncate(lradbearing_ce, self.tolerance):
                            radtangent = "Compound"
                        elif self.truncate(radbearing_cs, self.tolerance) == self.truncate(180 + lradbearing_ce, self.tolerance):
                            radtangent = "Reverse"
                        else:
                            radtangent = "Non-Tangent"

                    row[29] = self.jsonBoundary[oid]["radtangent"] = radtangent

                    # Curve Description:

                    if radtangent == "Tangent":
                        desc_grid = "{} to the beginning of a curve, concave {}, and having a radius of {:.2f} feet; Thence {} along said curve {:.2f} feet through a central angle of {};{}".format(preamp, self.bearingLabel(midbearing), self.truncate(radius, self.tolerance), self.bearingLabel(bearing), self.truncate(arclength, self.tolerance), self.dd2dms(delta), closing)
                        desc_ground = "{} to the beginning of a curve, concave {}, and having a radius of {:.2f} feet; Thence {} along said curve {:.2f} feet through a central angle of {};{}".format(preamp, self.bearingLabel(midbearing), self.truncate(radius/self.scalefactor, self.tolerance), self.bearingLabel(bearing), self.truncate(arclength/self.scalefactor, self.tolerance), self.dd2dms(delta), closing)
                        ann_grid = "{}={}  R={:.2f}  L={:.2f}".format("\N{GREEK CAPITAL LETTER DELTA}", self.dd2dms(delta), self.truncate(radius, self.tolerance), self.truncate(arclength, self.tolerance))
                        ann_ground = "{}={}  R={:.2f}  L={:.2f}".format("\N{GREEK CAPITAL LETTER DELTA}", self.dd2dms(delta), self.truncate(radius/self.scalefactor, self.tolerance), self.truncate(arclength/self.scalefactor, self.tolerance))
                        annweb_grid = "{}={}\nR={:.2f}\nL={:.2f}".format("\u0394", self.dd2dms(delta), self.truncate(radius, self.tolerance), self.truncate(arclength, self.tolerance))
                        annweb_ground = "{}={}\nR={:.2f}\nL={:.2f}".format("\u0394", self.dd2dms(delta), self.truncate(radius/self.scalefactor, self.tolerance), self.truncate(arclength/self.scalefactor, self.tolerance))

                    elif radtangent == "Compound":
                        desc_grid = "{} to the beginning of a compound curve concave {} and having a radius of {:.2f} feet; Thence {} along said curve {:.2f} feet through a central angle of {};{}".format(preamp, self.bearingLabel(midbearing), self.truncate(radius, self.tolerance), self.bearingLabel(bearing), self.truncate(arclength, self.tolerance), self.dd2dms(delta), closing)
                        desc_ground = "{} to the beginning of a compound curve {} and having a radius of {:.2f} feet; Thence {} along said curve {:.2f} feet through a central angle of {};{}".format(preamp, self.bearingLabel(midbearing), self.truncate(radius/self.scalefactor, self.tolerance), self.bearingLabel(bearing), self.truncate(arclength/self.scalefactor, self.tolerance), self.dd2dms(delta), closing)
                        ann_grid = "{}={}  R={:.2f}  L={:.2f}".format("\N{GREEK CAPITAL LETTER DELTA}", self.dd2dms(delta), self.truncate(radius, self.tolerance), self.truncate(arclength, self.tolerance))
                        ann_ground = "{}={}  R={:.2f}  L={:.2f}".format("\N{GREEK CAPITAL LETTER DELTA}", self.dd2dms(delta), self.truncate(radius/self.scalefactor, self.tolerance), self.truncate(arclength/self.scalefactor, self.tolerance))
                        annweb_grid = "{}={}\nR={:.2f}\nL={:.2f}".format("\u0394", self.dd2dms(delta), self.truncate(radius, self.tolerance), self.truncate(arclength, self.tolerance))
                        annweb_ground = "{}={}\nR={:.2f}\nL={:.2f}".format("\u0394", self.dd2dms(delta), self.truncate(radius/self.scalefactor, self.tolerance), self.truncate(arclength/self.scalefactor, self.tolerance))

                    elif radtangent == "Reverse":
                        desc_grid = "{} to the beginning of a reverse curve concave {} and having a radius of {:.2f} feet; Thence {} along said curve {:.2f} feet through a central angle of {};{}".format(preamp, self.bearingLabel(midbearing), self.truncate(radius, self.tolerance), self.bearingLabel(bearing), self.truncate(arclength, self.tolerance), self.dd2dms(delta), closing)
                        desc_ground = "{} to the beginning of a reverse curve concave {} and having a radius of {:.2f} feet; Thence {} along said curve {:.2f} feet through a central angle of {};{}".format(preamp, self.bearingLabel(midbearing), self.truncate(radius/self.scalefactor, self.tolerance), self.bearingLabel(bearing), self.truncate(arclength/self.scalefactor, self.tolerance), self.dd2dms(delta), closing)
                        ann_grid = "{}={}  R={:.2f}  L={:.2f}".format("\N{GREEK CAPITAL LETTER DELTA}", self.dd2dms(delta), self.truncate(radius, self.tolerance), self.truncate(arclength, self.tolerance))
                        ann_ground = "{}={}  R={:.2f}  L={:.2f}".format("\N{GREEK CAPITAL LETTER DELTA}", self.dd2dms(delta), self.truncate(radius/self.scalefactor, self.tolerance), self.truncate(arclength/self.scalefactor, self.tolerance))
                        annweb_grid = "{}={}\nR={:.2f}\nL={:.2f}".format("\u0394", self.dd2dms(delta), self.truncate(radius, self.tolerance), self.truncate(arclength, self.tolerance))
                        annweb_ground = "{}={}\nR={:.2f}\nL={:.2f}".format("\u0394", self.dd2dms(delta), self.truncate(radius/self.scalefactor, self.tolerance), self.truncate(arclength/self.scalefactor, self.tolerance))

                    elif radtangent == "Non-Tangent":
                        # Get the tangent description string depending on the bearing direction
                        if 0 <= radbearing_cs <= 90:
                            dbearing = "North {} East".format(self.dd2dms(radbearing_cs))
                        elif 90 < radbearing_cs <= 180:
                            dbearing = "South {} East".format(self.dd2dms(180 - radbearing_cs))
                        elif 180 < radbearing_cs <= 270:
                            dbearing = "South {} West".format(self.dd2dms(radbearing_cs - 180))
                        elif 270 < radbearing_cs <= 360:
                            dbearing = "North {} West".format(self.dd2dms(360 - radbearing_cs))

                        desc_grid = "{} to the beginning of a non-tangent curve, concave {}, and having a radius of {:.2f} feet, a radial line to said beginning of curve bears {}; Thence {} along said curve {:.2f} feet through a central angle of {};{}".format(preamp, self.bearingLabel(midbearing), self.truncate(radius, self.tolerance), dbearing, self.bearingLabel(bearing), self.truncate(arclength, self.tolerance), self.dd2dms(delta), closing)
                        desc_ground = "{} to the beginning of a non-tangent curve, concave {}, and having a radius of {:.2f} feet, a radial line to said beginning of curve bears {}; Thence {} along said curve {:.2f} feet through a central angle of {};{}".format(preamp, self.bearingLabel(midbearing), self.truncate(radius/self.scalefactor, self.tolerance), dbearing, self.bearingLabel(bearing), self.truncate(arclength/self.scalefactor, self.tolerance), self.dd2dms(delta), closing)
                        ann_grid = "{}={}  R={:.2f}  L={:.2f}".format("\N{GREEK CAPITAL LETTER DELTA}", self.dd2dms(delta), self.truncate(radius, self.tolerance), self.truncate(arclength, self.tolerance))
                        ann_ground = "{}={}  R={:.2f}  L={:.2f}".format("\N{GREEK CAPITAL LETTER DELTA}", self.dd2dms(delta), self.truncate(radius/self.scalefactor, self.tolerance), self.truncate(arclength/self.scalefactor, self.tolerance))
                        annweb_grid = "{}={}\nR={:.2f}\nL={:.2f}".format("\u0394", self.dd2dms(delta), self.truncate(radius, self.tolerance), self.truncate(arclength, self.tolerance))
                        annweb_ground = "{}={}\nR={:.2f}\nL={:.2f}".format("\u0394", self.dd2dms(delta), self.truncate(radius/self.scalefactor, self.tolerance), self.truncate(arclength/self.scalefactor, self.tolerance))

                    # Adding the curve description to feature attributes and JSON data string
                    row[30] = self.jsonBoundary[oid]["desc_grid"] = desc_grid
                    row[31] = self.jsonBoundary[oid]["desc_ground"] = desc_ground
                    row[32] = self.jsonBoundary[oid]["ann_grid"] = ann_grid
                    row[33] = self.jsonBoundary[oid]["ann_ground"] = ann_ground
                    row[34] = self.jsonBoundary[oid]["annweb_grid"] = annweb_grid
                    row[35] = self.jsonBoundary[oid]["annweb_ground"] = annweb_ground

                cursor.updateRow(row)


        self.appendReport("\tGenerated line and curve descriptions for boundary features")



    
        # Make updates and corrections
        with arcpy.da.UpdateCursor("PIQ", ["OID@", "SHAPE@"] + ["coid"] + [field[0] for field in boundaryFields]) as cursor:

            # Loop through lines in multilines
            for row in cursor:
                oid = row[0]
                coid = row[2]
                nrows = int(arcpy.GetCount_management("PIQ")[0]) # Total number of multilines
                shapetype = row[5]
                radtangent = row[29]
                desc_grid = row[30]
                desc_ground = row[31]


                # Get the previous and next multilines:
                if coid == 1:
                    lcoid = nrows # Last COID
                    ncoid = coid + 1 # Next COID
                elif coid > 1 and coid < nrows:
                    lcoid = coid - 1
                    ncoid = coid + 1
                elif coid > 1 and coid == nrows:
                    lcoid = coid - 1
                    ncoid = 1

                # Get the characteristics of the previous feature
                with arcpy.da.SearchCursor("PIQ", ["OID@", "SHAPE@"] + ["coid"] + [field[0] for field in boundaryFields]) as lcursor:
                    for lrow in lcursor:
                        if lrow[2] == lcoid:
                            lshapetype = lrow[5]
                            lradtangent = lrow[29]
                            lradbearing_cs = lrow[25]



                # If current feature is a Line or a Non-Tangent curve and the previous is a tangent Curve:
                if shapetype == "Line" or radtangent == "Non-Tangent":
                    if lshapetype == "Curve" and lradtangent == "Tangent":
                        desc_grid = desc_grid.replace("Thence", "Thence non-tangent to said curve")
                        desc_ground = desc_ground.replace("Thence", "Thence non-tangent to said curve")
                        row[30] = desc_grid
                        row[31] = desc_ground
                        self.jsonBoundary[oid]["desc_grid"] = desc_grid
                        self.jsonBoundary[oid]["desc_ground"] = desc_ground

                # If the first feature is a curve:
                if coid == 1 and shapetype == "Curve":
                    #newdesc1 = f"Thence from said {tpobstring} " + desc1.split(";")[1].replace("Thence ", "")
                    desc_grid = desc_grid.split(";")[1]
                    desc_ground = desc_ground.split(";")[1]
                    row[30] = desc_grid
                    row[31] = desc_ground
                    self.jsonBoundary[oid]["desc_grid"] = desc_grid
                    self.jsonBoundary[oid]["desc_ground"] = desc_ground

                # if current feature is a line coming from a curve (radial)
                if shapetype == "Line" and lshapetype == "Curve":
                    if bearing == lradbearing_cs or bearing == (180 + lradbearing_cs) % 360:
                        desc_grid = desc_grid.replace("Thence", "Thence radial to said curve")
                        desc_ground = desc_ground.replace("Thence", "Thence radial to said curve")
                        row[30] = desc_grid
                        row[31] = desc_ground
                        self.jsonBoundary[oid]["desc_grid"] = desc_grid
                        self.jsonBoundary[oid]["desc_ground"] = desc_ground

                cursor.updateRow(row)
    
        self.appendReport("\tCorrected descriptions for Legal Description formatting")
        self.appendReport("\tMultiline Descriptions added to JSON data string")

        if self.jsonBoundary is not None:
            self.appendReport("\tBoundary Features Processing Complete: Passed\n")
        else:
            self.appendReport("\tBoundary Features Processing Complete: Failed\n")

        # Write the derived annotation labels for the boundary geometry
        self.appendReport("Annotation Labels (Grid)")
        for i in range(len(self.jsonBoundary)):
            jrow = [self.jsonBoundary[j] for j in self.jsonBoundary if self.jsonBoundary[j]["coid"] == i+1][0]
            self.appendReport("\tCOID {} ({}): {}".format(i+1, jrow["shapetype"], jrow["ann_grid"].replace("Δ", "D")))

        self.appendReport("\nAnnotation Labels (Ground)")
        for i in range(len(self.jsonBoundary)):
            jrow = [self.jsonBoundary[j] for j in self.jsonBoundary if self.jsonBoundary[j]["coid"] == i+1][0]
            self.appendReport("\tCOID {} ({}): {}".format(i+1, jrow["shapetype"], jrow["ann_ground"].replace("Δ", "D")))

        etime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("\nScript Completed on {}\n\n".format(etime))

        return






    #---------- AMC Class Function: Create Legal Description ----------#

    def createLegalDescription(self):
        """AMC Class Function: Create Legal Description
        Generates a legal description document after boundary processing data
        """

        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("\n{:-^80s}\n".format(" PART 3: AMC LEGAL DESCRIPTION PROCESSING "))
        self.appendReport("Script Started on: {}\n".format(stime))


        # Create a map description
        self.describeMapDocument()

        # Create a Preamp (for Grid and Ground versions) from Horizontal Controls
        self.describeHorizontalControls()

        # Create the legal description
        ldtext = []
        gldtext = []
        for i in self.course:
            oid = self.course[i]["oid"]
            desc = self.jsonBoundary[oid]["desc_grid"]
            gdesc = self.jsonBoundary[oid]["desc_ground"]
            ldtext.append(desc)
            gldtext.append(gdesc)
        self.ld = "".join(ldtext)
        self.gld = "".join(gldtext)
        self.ld.replace("; to the", ", to the")
        self.gld.replace("; to the", ", to the")

        # Write Legal Description to Report (grid)
        self.appendReport("\n\nLEGAL DESCRIPTION (GRID)\n")
        self.appendReport("\t{}".format(self.mapdesc))
        self.appendReport("\t{}".format(self.preamp))
        self.appendReport("\t{}\n".format(self.ld))

        # Write Legal Description to Report (ground)
        self.appendReport("\n\nLEGAL DESCRIPTION (GROUND)\n")
        self.appendReport("\t{}".format(self.mapdesc))
        self.appendReport("\t{}".format(self.gpreamp))
        self.appendReport("\t{}\n".format(self.gld))

        # Compile the JSON data for the legal description
        self.jsonLegalDescription["Map"] = self.mapdesc
        self.jsonLegalDescription["Grid"] = {}
        self.jsonLegalDescription["Grid"]["Preamp"] = self.preamp
        self.jsonLegalDescription["Grid"]["Course"] = self.ld
        self.jsonLegalDescription["Ground"] = {}
        self.jsonLegalDescription["Ground"]["Preamp"] = self.gpreamp
        self.jsonLegalDescription["Ground"]["Course"] = self.gld
        
        etime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("\nScript Completed on {}\n\n".format(etime))

        return


    


    #---------- AMC Class Function: Finalize Report ----------#

    def finalizeReport(self):
        """AMC Class Function: Finalize Report and Execution
        Compiles and exports all data and reports and finishes up the execution
        """
        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("\n{:-^80s}\n".format(" PART 4: AMC PROCESS FINALIZATION "))
        self.appendReport("Script Started on: {}\n".format(stime))

        # Compile the final JSON data
        response = {}
        response["Execution"] = self.jsonExecution
        response["Checks"] = self.jsonChecks
        response["Boundaries"] = self.jsonBoundary
        response["Controls"] = self.jsonControls
        response["LegalDescription"] = self.jsonLegalDescription

        os.chdir(self.outpath)
        with open("jsonResponse.json", "w") as jsonfile:
            json.dump(response, jsonfile)

        self.appendReport("JSON Data String Output Written to Disk: jsonResponse.json\n")

        etime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("\nScript Completed on {}\n\n".format(etime))


        self.appendReport("\n{:^80s}\n".format("END OF EXECUTION REPORT"))

        return response






    #========================= PART III: SECONDARY CLASS FUNCTIONS =========================#



    #---------- AMC Class Function: Append Report ----------#

    def appendReport(self, string):
        """AMC Class Function: Append Execution Report"""
        # Open the file for appending
        fa = open(self.report, "a+")
        # Append to the end of the file
        fa.write("{}\n".format(string))
        # Close the file after appending
        fa.close()
        #print(string)
        arcpy.AddMessage(string)
        return

    


    #---------- AMC Class Function: Arcpy Message ----------#

    def getAgpMsg(self, ntabs=1):
        """AMC Class Function: Arcpy Message"""
        # Get tge number of tabs defined in the input
        tabs = "\t"*ntabs
        # Add the tabs at the beginning of the message
        msg = tabs + arcpy.GetMessages().replace("\n", "\n{}".format(tabs)) + "\n\n"
        return msg




    #---------- AMC Class Function: Check Project Geodatabase ----------#

    def checkGDB(self):
        """AMC Class Function: Check Project Geodatabase
        Checks if the reference geodatabase exists. If it does, it deletes it and creates a new one.
        """
        self.appendReport("Project Geodatabase")
        self.gdbname = os.path.split(self.gdbpath)[1]
        self.appendReport("\tChecking for geodatabase: {}".format(self.gdbname))

        # Check if the geodatabase exists
        if arcpy.Exists(self.gdbpath):
            self.appendReport("\t...geodatabase exists.")
            # Delete the geodatabase if it exists
            arcpy.Delete_management(self.gdbpath)
            self.appendReport("\t...existing geodatabase removed.")

        # Creates new geodatabase
        arcpy.CreateFileGDB_management(self.outpath, self.gdbname)
        self.appendReport("\t...new geodatabase created.\n")

        return




    #---------- AMC Class Function: Check Layers in CAD ----------#

    def checkLayers(self):
        """AMC Class Function: Check Layers in CAD
        Checks for the presence of all the layers in CAD Drawing. Records Pass/Fail in JSON Checks
        """

        # List of all the default layer types to be checked
        self.layerChecks = {
            "V-ANNO": {"Desc": "Annotation", "Name": "ANNO", "FeatureClass": False, "Type": "Annotation"},
            "V-LINE": {"Desc": "Misc Lines", "Name": "LINE", "FeatureClass": False, "Type": "Polyline"},
            "V-LINE-CALC": {"Desc": "Line Calc/Ties to POB", "Name": "CALC", "FeatureClass": True, "Type": "Polyline"},
            "V-LINE-CNTR": {"Desc": "Street Centerline", "Name": "CNTR", "FeatureClass": True, "Type": "Polyline"},
            "V-LINE-ESMT": {"Desc": "Easement", "Name": "ESMT", "FeatureClass": True, "Type": "Polyline"},
            "V-LINE-LOTS": {"Desc": "Property Line Lots", "Name": "LOTS", "FeatureClass": True, "Type": "Polyline"},
            "V-LINE-PCLS": {"Desc": "C3D Parcel Lines and Parcel Annotation", "Name": "PCLS", "FeatureClass": False, "Type": "Polyline"},
            "V-LINE-PIQ": {"Desc": "Property Line Boundary", "Name": "PIQ", "FeatureClass": True, "Type": "Polyline"},
            "V-LINE-REF": {"Desc": "Line Reference", "Name": "REF", "FeatureClass": False, "Type": "Polyline"},
            "V-LINE-RTWY": {"Desc": "Street Right of Way, ROW", "Name": "RTWY", "FeatureClass": True, "Type": "Polyline"},
            "V-LINE-TIE": {"Desc": "Ties to Basis of Bearings", "Name": "TIE", "FeatureClass": True, "Type": "Polyline"},
            "V-MISC": {"Desc": "Misc and North Arrow", "Name": "MISC", "FeatureClass": False, "Type": "Polygon"},
            "V-NODE-MON": {"Desc": "Mon", "Name": "MON", "FeatureClass": False, "Type": None},
            "V-NODE-TABL": {"Desc": "Table Data", "Name": "TABL", "FeatureClass": False, "Type": None},
            "V-NODE-TPOB": {"Desc": "True Point of Beginning", "Name": "TPOB", "FeatureClass": True, "Type": "Point"},
            "V-SHEET": {"Desc": "Sheet Details", "Name": "SHEET", "FeatureClass": False, "Type": None},
            "V-VPORT": {"Desc": "VPORT 1", "Name": "VPORT1", "FeatureClass": False, "Type": None},
            "V-VPORT FREEZES": {"Desc": "VPORT 2", "Name": "VPORT2", "FeatureClass": False, "Type": None}
            }

        # Empty dictionary to hold the layers present in CAD drawing
        self.gdbLayers = {"All": []}
        for f in arcpy.ListFeatureClasses(feature_dataset = "CAD"):
            self.gdbLayers[f] = []


        cadLayers = [lyr for lyr in self.gdbLayers if lyr is not "All"] # Types of geometries: Annotation, Point, Polyline, MultiPatch, or Polygon

        # For each type of CAD geometry in geodatabase
        for lyrType in cadLayers:
            # Check to see if the geometry layer is imported and exists
            if arcpy.Exists(os.path.join("CAD", lyrType)):
                with arcpy.da.SearchCursor(os.path.join("CAD", lyrType), ["Layer"]) as cursor:
                    for row in cursor:

                        # If the layer is not already imported, and it is part of the list of default layers to be checked:
                        if row[0] not in self.gdbLayers[lyrType] and row[0] in list(self.layerChecks.keys()):
                            # add them to the geometry type list of layers
                            self.gdbLayers[lyrType].append(row[0])
                            # sort the list
                            self.gdbLayers[lyrType].sort()

                        # Add also the layer to the master layers list
                        if row[0] not in self.gdbLayers["All"] and row[0] in list(self.layerChecks.keys()):
                            self.gdbLayers["All"].append(row[0])
                            self.gdbLayers["All"].sort()

        # Expand the default layer dicrionary by whether each of the layers is present in which geometry
        for lyr in self.layerChecks: # layers
            for group in cadLayers: # geometries
                if lyr in self.gdbLayers[group]:
                    self.layerChecks[lyr][group] = True
                else:
                    self.layerChecks[lyr][group] = False


        # Final checks for all layers
        self.appendReport("Layer Checks")
        for i, lyr in enumerate(list(self.layerChecks.keys()), start=1):
            if lyr in self.gdbLayers["All"]:
                self.appendReport("\tCheck {} of {}: {} ({}) in CAD Drawing: Passed".format(i, len(list(self.layerChecks.keys())), lyr, self.layerChecks[lyr]["Desc"]))
                self.jsonChecks["LayerChecks"][lyr] = "Pass"
            elif lyr not in self.gdbLayers["All"]:
                self.appendReport("\tCheck {} of {}: {} ({}) not in CAD Drawing: Failed".format(i, len(list(self.layerChecks.keys())), lyr, self.layerChecks[lyr]["Desc"]))
                self.jsonChecks["LayerChecks"][lyr] = "Fail"


        # If all the checks passed
        if all([self.jsonChecks["LayerChecks"][i] == "Pass" for i in self.jsonChecks["LayerChecks"]]):
            self.appendReport("\tAll layers passed their checks. \n")
        else:
            self.appendReport("\tOne or more layers failed their checks, above. Please make sure all layers exist in the CAD drawing.\n")

        return



    #---------- AMC Class Function: Create Feature Classes from Original CAD Drawing Layers ----------#

    def createFeatureClasses(self):
        """AMC Class Function: Create Feature Classes from Original CAD Drawing Layers
        Uses specific and verified layers from the imported CAD Drawing Features to generate feature classes in the geodatabase
        """
        self.appendReport("\nCreating New Feature Classes in Geodatabase")
        layers = [key for key in self.layerChecks if self.layerChecks[key]["FeatureClass"] is True]
        for lyr in layers:
            if self.jsonChecks["LayerChecks"][lyr] == "Pass":
                fc = self.layerChecks[lyr]["Name"]
                if arcpy.Exists(fc):
                    arcpy.Delete_management(fc)
                where_clause = """Layer = '{}'""".format(lyr)
                desc = self.layerChecks[lyr]["Desc"]
                lyrtype = self.layerChecks[lyr]["Type"]
                arcpy.Select_analysis(os.path.join("CAD", lyrtype), fc, where_clause)
                arcpy.AlterAliasName(fc, desc)
                self.appendReport("\tCreating {} Feature Class {} ({}) in geodatabase".format(lyrtype, fc, desc))
        self.appendReport("\tNew feature classes created and added to the geodatabase.\n")

        # Creating and checking the closure of the boundary polygons
        self.nparcels = self.checkClosureCentroid()

        return



    #---------- AMC Class Function: Check GPS Control Points ----------#

    def checkGPS(self):
        """AMC Class Function: Check GPS Control Points
        Checks and verifies the presence of the GPS Control Points in the CAD drawing
        """

        # List all of GPS points in CAD drawing and checks to make sure there are at least two of them present
        self.appendReport("GPS Control Point Check")
        self.gpspoints = []
        with arcpy.da.SearchCursor(os.path.join("CAD", "Annotation"), ["RefName", "SHAPE@XY"]) as cursor:
            n = 0
            for row in cursor:
                if "GPS" in row[0]:
                    n += 1
                    self.gpspoints.append(row[0])
                    self.jsonControls["GPS"][str(n)] = {}
                    self.jsonControls["GPS"][str(n)]["id"] = row[0]
                    self.jsonControls["GPS"][str(n)]["x"] = row[1][0]
                    self.jsonControls["GPS"][str(n)]["y"] = row[1][1]

        if len(self.gpspoints) == 2:
            self.appendReport("\tGPS Points Check: Passed (2 points)")
            arcpy.Select_analysis("Annotation", "GPS", """RefName LIKE '%GPS%'""")
            self.appendReport("\tAdding points to geodatabase:\n {}".format(self.getAgpMsg(2)))
            self.jsonChecks["GPSChecks"] = "Pass"
        elif len(self.gpspoints) < 2:
            self.appendReport("\tGPS Points Check: Failed (less than 2 points)\n")
            self.jsonChecks["GPSChecks"] = "Fail"
        elif len(self.gpspoints) > 2:
            self.appendReport("\tGPS Points Check: Failed (more than 2 points)\n")
            self.jsonChecks["GPSChecks"] = "Fail"

        return




    #---------- AMC Class Function: Check Geodetic Control Point Geometries ----------#

    def checkGeodeticControls(self):
        """AMC Class Function: Check Geodetic Controls
        Checks for geodetic control point geometries in server geodatabase
        """

        self.appendReport("Geodetic Control Geometry Check")

        if self.ocserver:
            self.serverGC = os.path.join(self.ocserver, "OCSurvey.DBO.GEODETIC_HORIZONTAL")
            self.appendReport("\tChecking Geodetic Control Server Features: OCSurvey.DBO.GEODETIC_HORIZONTAL")
    
            # Creating a new feature layer
            arcpy.MakeFeatureLayer_management(self.serverGC, "geodetics_lyr")

            # Updating feature class GPSPoints
            with arcpy.da.UpdateCursor("GPS", ["OID@", "SHAPE@", "RefName"]) as cursor:
                for row in cursor:
                    oid = row[0]
                    gpsid = row[2].split("GPS NO. ")[1]

                    # Searching the geodetics control layer for the GPS point geometry
                    with arcpy.da.SearchCursor("geodetics_lyr", ["OID@", "SHAPE@", "GPS", "Easting2017", "Northing2017"]) as cursor1:
                        for row1 in cursor1:
                            if gpsid == row1[2]:
                                self.appendReport("\tGeodetic control point no. {} located in server database".format(gpsid))
                                # Get the geometry from the server point
                                realgeometry = row1[1].WKT
                                # Transplant the geometry of the server to the geometry of the CAD layer
                                row[1] = arcpy.FromWKT(realgeometry)
                                self.appendReport("\t\tTransplanted geometry to CAD annotation layer from server points WKT attributes")
                                # Write the coordinates to the JSON data string
                                self.appendReport("\t\tPoint coordinates written to JSON data string")
                                self.jsonControls["GPS"][str(oid)]["id"] = gpsid
                                self.jsonControls["GPS"][str(oid)]["x"] = row1[1][0].X
                                self.jsonControls["GPS"][str(oid)]["y"] = row1[1][0].Y
                                cursor.updateRow(row)

            self.appendReport("\tGeodetic Control Point Geometry Check: Passed\n")
            self.jsonChecks["GeodeticControlPoints"] = "Pass"

        else:
            self.appendReport("\tChecking Geodetic Control Server Features: Failed. Script outside OCPW Domain\n")
            serverGC = None
            self.jsonChecks["GeodeticControlPoints"] = "Fail"

        return




    #---------- AMC Class Function: Check for the presence of the (True) Point of Beginning ----------#

    def checkPOB(self):
        """AMC Class Function: Check for point of beginning
        Checks for the presence of the (True) Point of Beginning
        """

        # Dictionary to hold the coordinates of the TPOB points
        self.tpobdict = {}
        self.tpobdict["source"] = "none"
        self.tpobdict["count"] = 0
        self.tpobdict["points"] = {}

        # True Point of Beginning
        self.appendReport("True Point of Beginning (TPOB) Check")

        # if TPOB coordinates are provided by user
        if self.tpob:
            self.appendReport("\tUser-provided TPOB detected. Verifying...")

            # This is a single point set of coordinates (hence, tuple)
            if type(self.tpob) is tuple:
                self.appendReport("\t...Single-point provided by user.")
                # Checking to make sure that all provided coordinates are floating point numbers
                if all(type(coor) is float for coor in self.tpob):
                    self.appendReport("\t...all provided coordinates are floating point numbers")
                    self.tpobdict["source"] = "user"
                    self.tpobdict["count"] = 1
                    self.tpobdict["points"] = {1: {"x": self.tpob[0], "y": self.tpob[1]}}
                    self.jsonChecks["TPOB"] = "Pass"
                    self.tpobstring = "TRUE POINT OF BEGINNING"
                    self.appendReport("\tSingle-point TPOB Provided by User: Passed. \n")

            # This is a multi-point set of coordinates (hence, list)
            elif type(self.tpob) is list:
                self.appendReport("\t...Multi-point provided by user.")
                # Verifying format - first, all sets must be tuples
                if all(types(t) is tuple for t in self.tpob):
                    self.tpobdict["source"] = "user"
                    self.tpobdict["count"] = len(self.tpob)
                    # secondly, for each pair of coordinates, verifying floating point format
                    for i, pt in enumerate(self.tpob):
                        if all(type(coor) is float for coor in pt):
                            self.appendReport("\t... Point {}: all coordinates are floating point numbers".format(i+1))
                            self.tpobdict["points"][i+1] = {"x": pt[0], "y": pt[1]}
                            self.jsonChecks["TPOB"] = "Pass"
                            self.tpobstring = "POINT OF BEGINNING"
                            self.appendReport["\tMulti-point TPOB Provided by User: Passed. \n"]

        # If TPOB coordinates are not provided by user - checking CAD drawing layers
        elif self.tpob is None:
            # Check the geodatabase
            if arcpy.ListFeatureClasses("TPOB")[0] == "TPOB":
                # Get the number of points (how many rows) in feature class:
                self.tpobdict["source"] = "cad"
                self.tpobdict["count"] = int(arcpy.GetCount_management("TPOB")[0])

                # This is a single or multi-point point detected in the geodatabase
                if self.tpobdict["count"] >= 1:
                    if self.tpobdict["count"] == 1:
                        self.appendReport("\t...Single-point detected in the drawing.")                        
                    elif self.tpobdict["count"] > 1:
                        self.appendReport("\t...Multi-point detected in the drawing.")
                    # Get the point coordinates
                    with arcpy.da.SearchCursor("TPOB", ["OID@", "SHAPE@"]) as cursor:
                        for row in cursor:
                            self.tpobdict["points"][row[0]] = {"x": row[1][0].X, "y": row[1][0].Y}
                    self.jsonChecks["TPOB"] = "Pass"
                    self.appendReport("\tTPOB point layer exist in CAD drawing: Passed. \n")
                elif self.tpobdict["count"] == 0:
                    self.jsonChecks["TPOB"] = "Fail"
                    self.appendReport("\tTPOB point(s) not found in CAD drawing layer: Failed. \n")

                # Update the set of coordinates:
                if self.tpobdict["count"] == 1:
                    # Tuple
                    self.tpob = self.tpobdict["points"][1]["x"], self.tpobdict["points"][1]["y"]
                    self.tpobstring = "TRUE POINT OF BEGINNING"
                elif self.tpobdict["count"] > 1:
                    # List of tuples
                    self.tpob = [(self.tpobdict["points"][i]["x"], self.tpobdict["points"][i]["y"]) for i in self.tpobdict["points"]]
                    # Check to see if all the points have the same coordinates:
                    if len(self.tpob) == self.tpob.count(self.tpob[0]):
                        self.appendReport("\tWARNING: Multiple TPOB points detected in CAD Drawing. All points have the same coordinates. Using the first point in layer and ignoring the rest.")
                        self.tpob = self.tpob[0]
                        self.tpobstring = "TRUE POINT OF BEGINNING"
                    else:
                        self.tbostring = "POINT OF BEGINNING"


        # If TPOB is not found
        if self.tpobdict["source"] == "none":
            self.appendReport("\tTPOB is missing: Failed\n")

        # Populate the JSON Controls
        self.jsonControls["TPOB"] = self.tpobdict

        return




    #---------- AMC Class Function: Checking for expanded boundary layers ----------#

    def checkEBL(self):
        """AMC Class Function: Check for expanded boundary layers
        Checking for expanded boundary layers in CAD drawing and corrects geometry if necessary
        """

        # Checking for expanded boundary layer
        self.appendReport("Expanded Boundary Layer Check:")
        nr = int(arcpy.GetCount_management("PIQ")[0])

        # if a single row in boundary layer
        if nr == 1:
            self.appendReport("\tSingle boundary line detected: correcting...")
            arcpy.Rename_management("PIQ", "PIQSingle")
            arcpy.SplitLine_management("PIQSingle", "PIQ")
            arcpy.Delete_management("PIQSingle")
            self.appendReport("\tMulti-boundary lines corrected: Passed\n")
            self.jsonChecks["BoundaryCorrections"] = "Corrected"
            self.jsonChecks["BoundaryChecks"] = "Pass"
        elif nr > 1:
            self.appendReport("\tMulti-boundary lines detected: Passed\n")
            self.jsonChecks["BoundaryCorrections"] = "Original"
            self.jsonChecks["BoundaryChecks"] = "Pass"
        else:
            self.appendReport("\tMulti-boundary lines not detected: Failed\n")
            self.jsonChecks["BoundaryCorrections"] = "None"
            self.jsonChecks["BoundaryChecks"] = "Fail"

        return




    #---------- AMC Class Function: Checks for closure ----------#

    def checkClosureCentroid(self):
        """AMC Class Function: Checks for closure
        Checks for closure: creating boundary polygon and returns it's centroid coordinates
        """

        if arcpy.Exists("PARCELS"):
            arcpy.Delete_management("PARCELS")

        arcpy.FeatureToPolygon_management("PIQ", "PARCELS")
        arcpy.AlterAliasName("PARCELS", "Property Line Boundary Area")
        self.appendReport("Creating Property Line Boundary Area (PARCELS) Polygon Feature Class.\n")

        self.appendReport("Boundary Polygon/Centroid Closure Check:")

        # Adding fields
        newFields = ["CentroidX", "CentroidY", "AreaSqFeet", "AreaAcres"]
        for field in newFields:
            arcpy.AddField_management("PARCELS", field, "FLOAT")

        # If boundary parcels exist
        boundaryparcels = int(arcpy.GetCount_management("PARCELS")[0])
        self.appendReport("\tNumber of Boundary Parcels: {}".format(boundaryparcels))

        if boundaryparcels == 1:
            self.boundaryCase = "Single"
            areas = []

            # Getting the centroid coordinates for a given polygon
            self.appendReport("\tObtaining the centroid coordinates for each boundary polygon")
            with arcpy.da.UpdateCursor("PARCELS", ["OID@", "SHAPE@", "CentroidX", "CentroidY", "AreaSqFeet", "AreaAcres"]) as cursor:
                for row in cursor:
                    oid = row[0]
                    centroidx = row[2] = row[1].centroid.X
                    centroidy = row[3] = row[1].centroid.Y
                    self.centroid = centroidx, centroidy # returns the centroid coordinates of that parcel
                    areaSqFeet = row[4] = row[1].getArea("GEODESIC", "SQUAREFEET")
                    areaAcres = row[5] = row[1].getArea("GEODESIC", "ACRES")
                    areas = (areaSqFeet, areaAcres)
                    cursor.updateRow(row)
                    self.jsonControls["Centroid"][oid] = self.centroid
                    self.jsonControls["Areas"][oid] = {}
                    self.jsonControls["Areas"][oid]["SquareFeet"] = areaSqFeet
                    self.jsonControls["Areas"][oid]["Acres"] = areaAcres
                    self.jsonChecks["BoundaryClosure"][oid] = "Pass"
                    self.appendReport("\tBoundary area closure: Passed\n")

        elif boundaryparcels > 1:

            # Find which case it is
            # Create Polygon Neighbors Table
            arcpy.PolygonNeighbors_analysis("PARCELS", "NEIGHBORS", "OBJECTID;Shape_Area", "AREA_OVERLAP", "BOTH_SIDES", None, "FEET", "SQUARE_FEET")

            # Search how many rows the table has. If it has no rows, then this is the case of Separate Boundaries
            if int(arcpy.GetCount_management("NEIGHBORS")[0]) == 0:
                self.boundaryCase = "Separate"
                areas = []

                # Getting the centroid coordinates for each polygon
                self.appendReport("\tObtaining the centroid coordinates for each boundary polygon")
                with arcpy.da.UpdateCursor("PARCELS", ["OID@", "SHAPE@", "CentroidX", "CentroidY", "AreaSqFeet", "AreaAcres"]) as cursor:
                    for row in cursor:
                        oid = row[0]
                        centroidx = row[2] = row[1].centroid.X
                        centroidy = row[3] = row[1].centroid.Y
                        self.centroid = centroidx, centroidy # returns the centroid coordinates of that parcel
                        areaSqFeet = row[4] = row[1].getArea("GEODESIC", "SQUAREFEET")
                        areaAcres = row[5] = row[1].getArea("GEODESIC", "ACRES")
                        areas = (areaSqFeet, areaAcres)
                        cursor.updateRow(row)
                        self.jsonControls["Centroid"][oid] = self.centroid
                        self.jsonControls["Areas"][oid] = {}
                        self.jsonControls["Areas"][oid]["SquareFeet"] = areaSqFeet
                        self.jsonControls["Areas"][oid]["Acres"] = areaAcres
                        self.jsonChecks["BoundaryClosure"][oid] = "Pass"
                        self.appendReport("\tBoundary area for polygon {} closure: Passed\n".format(oid))


            # otherwise, if there are rows in the table, we investigate further
            elif int(arcpy.GetCount_management("NEIGHBORS")[0]) > 0:
                # dictionary to get the query results
                tableData = {}
                # loop through table rows, and write the results to the dictionary
                with arcpy.da.SearchCursor("NEIGHBORS", ["OID@", "src_OBJECTID", "nbr_OBJECTID", "src_Shape_Area", "nbr_Shape_Area", "AREA", "LENGTH", "NODE_COUNT"]) as cursor:
                    for row in cursor:
                        oid = row[0]
                        if row[3] > row[4]: parentID = True
                        elif row[3] < row[4]: parentID = False
                        tableData[oid] = {"Source": row[1], "Neighbor": row[2], "Source Area": row[3], "Neighbor Area": row[4], "Overlap Area": row[5], "Overlap Length": row[6], "Node Count": row[7], "parent ID": parentID}

                # Now check the data in the dictionary. There are two possibilities:
                # if all the Lengths are equal to 0.0 then this is a case for Ajdacent Boundaries
                if all(tableData[i]["Overlap Length"] == 0.0 for i in tableData):
                    self.boundaryCase = "Adjacent"
                    areas = []
                # else, if all the Lengths are > 0 and are equal to each other, then there is the case of Not a Part Boundaries
                elif all(tableData[i]["Overlap Length"] > 0.0 for i in tableData) and all(tableData[i]["Overlap Length"] == tableData[1]["Overlap Length"] for i in tableData):
                    self.boundaryCase = "Not a Part"
                    areas = []

                    # Select the OID of the boundary with the larger area (parent)
                    parents = [i for i in tableData if tableData[i]["Parent ID"]]
                    if len(parents) == 1:
                        self.parentBoundary = parents[0]


        else:
            self.centroid = None
            self.jsonChecks["BoundaryClosure"][poid] == "Fail"
            self.appendReport("\tBoundary area closure: Failed\n")

        return boundaryparcels




    #---------- AMC Class Function: Checks for location ----------#

    def checkLocation(self):
        """AMC Class Function: Checks for location
        Checking county server geodatabase for location data on tract/parcel
        """
        
        self.appendReport("Map Server Location Checks")

        # If PFRDNET domain (and server) exists:
        if self.ocserver:
            self.serverCities = os.path.join(self.ocserver, "OCSurvey.DBO.Boundaries\OCSurvey.DBO.CityBoundaries")
            self.appendReport("\tChecking City Boundaries Server Features: OCSurvey.DBO.CityBoundaries")

            # Create temporary Cities layer from server
            arcpy.MakeFeatureLayer_management(self.serverCities, "cities_lyr")
            self.appendReport("\tFiniding locations in server that intersect with CAD boundary layer (within 0.01 feet)")

            # Select cities polygons that intersect within 0.01 feet from the CAD Boundaries layer
            arcpy.SelectLayerByLocation_management("cities_lyr", "INTERSECT", "PIQ", "0.01 Feet", "NEW_SELECTION", "NOT_INVERT")

            # How many cities intersect
            citiesNo = int(arcpy.GetCount_management("cities_lyr")[0])

            # Loop the selected cities
            with arcpy.da.SearchCursor ("cities_lyr", "CITY") as cursor:
                citiesList = []
                for row in cursor:
                    citiesList.append(row[0])

            if len(citiesList) == 1: # if only one city
                cities = citiesList[0]
                self.jsonChecks["Location"] = "Pass"
                self.appendReport("\tLocation found: {}".format(cities))
            elif len(citiesList) > 1: # if more than one city
                cities = citiesList
                self.jsonChecks["Location"] = "Pass"
                self.appendReport("\tMultiple locations found: {}".format(cities))
            else: # if no cities
                self.jsonChecks["Location"] = "Fail"
                self.appendReport("\tNo locations found: Failed")


            # Areas within or outside unincorporated territory
            if citiesNo == 1 and citiesList is not "UNINCORPORATED":
                cityString = "CITY of {}".format(cities)
                self.jsonControls["Location"]["Type"] = "City"
                self.appendReport("\tLocation type: City")
            elif citiesNo ==1 and citiesList is "UNINCORPORATED":
                cityString = "UNINCORPORATED TERRITORY"
                self.jsonControls["Location"]["Type"] = "Unincorporated Territory"
                self.appendReport("\tLocation type: Unincorporated Territory")
            elif citiesNo > 1 and "UNINCORPORATED" not in citiesList:
                cityString = "CITIES OF {} AND {}".format((", ").join(citiesList[:-1]).upper(), citiesList[-1].upper())
                self.jsonControls["Location"]["type"] = "Cities"
                self.appendReport("\tLocation type: Cities (multiple)")
            elif citiesNo > 1 and "UNINCORPORATED" in citiesList:
                cityString = "CITIES AND UNINCORPORATED TERRITORY OF {} AND {}".format((", ").join(citiesList[:-1]).upper(), citiesList[-1].upper())
                self.jsonControls["Location"]["type"] = "Both"
                self.appendReport("\tLocation type: Both City and Unincorporated Territory")

            self.jsonControls["Location"]["Name"] = cityString.title().replace("Of", "of")
            if citiesNo >= 1:
                self.jsonControls["Location"]["County"] = "Orange"
                countyString = "County of Orange"
                self.appendReport("\tCounty: {}".format(countyString))

            self.appendReport("\tFull Location Identified: {}, {}, State of California".format(cityString.title(), countyString))
            if self.jsonChecks["Location"] == "Pass":
                self.appendReport("\tLocation Check: Pass\n")
            elif self.jsonChecks["Location"] == "Fail":
                self.appendReport("\tLocation Check: Fail\n")

            self.citiesList, self.cityString = citiesList, cityString

        else:
            self.appendReport("\tChecking City Boundaries from Server Features Failed: Script outside OCPW Domain.")
            self.citiesList, self.cityString = None, None

        return




    #---------- AMC Class Function: Checks for Tract Information ----------#

    def checkServerTractMaps(self):
        """AMC Class Function: Tract Map Checking Information
        Checks for Tract Information from Server Geodatabase
        """
        self.appendReport(f"Tract Map Server Location Checks")

        if self.ocserver:
            self.serverTM = os.path.join(self.ocserver, "OCSurvey.DBO.TRACT_MAPS")
            self.appendReport("\tChecking Tract Maps Server Features: OCSurvey.DBO.TRACT_MAPS")
            self.appendReport("\tSearching Tract Map Geometry for information")

            # Create a copy of the map layer in the geodatabase:
            arcpy.MakeFeatureLayer_management(self.serverTM, "trackmaps_lyr")

            jsonTR = self.jsonControls["Title"]
            with arcpy.da.SearchCursor("trackmaps_lyr", ["OID@", "SHAPE@", "TRACTNUM", "BPNUM", "EngCo", "EngSvyName", "EngSvyNum"]) as cursor:
                for row in cursor:
                    oid = row[0]
                    if " " in row[2]:
                        serverTR = row[2].replace(" ", "")
                    else:
                        serverTR = None
                    if jsonTR == serverTR:
                        self.appendReport("\tServer tract lot exists in server: {}".format(jsonTR))
                        self.jsonChecks["MapGeometry"] = "Pass"
                        if "/" in row[3]:
                            # if Tract then MM else if Parcel then PMB or Record of Survey then RSB
                            bb = row[3]
                            if "MM" in bb:
                                bookNo = row[3].split("/")[0].split("MM ")[1]
                            elif "PMB" in bb:
                                bookNo = row[3].split("/")[0].split("PMB ")[1]
                            elif "RSB" in bb:
                                bookNo = row[3].split("/")[0].split("PMB ")[1]
                            self.appendReport("\tMap book number: {}".format(bookNo))
                            # if dash exists, split and replace dash with through, else do nothing. add inclussive at the end of string.
                            pp = row[3].split("/")[1]
                            if "-" in pp:
                                pagesNo = pp.replace("-", " through ") + " inclusive"
                            else:
                                pagesNo = row[3].split("/")[1]
                            self.appendReport("\tMap book pages: {}".format(pagesNo))
                            engCo = row[4]
                            self.appendReport("\tEngineering Company: {}".format(engCo))
                            engSvyName = row[5]
                            self.appendReport("\tSurveying Company Name: {}".format(engSvyName))
                            engSvyNum = row[6]
                            self.appendReport("\tSurveying Company Number: {}".format(engSvyNum))
                            self.jsonControls["Book"]["No"] = bookNo
                            self.jsonControls["Book"]["Pages"] = pagesNo
                            self.jsonControls["Registration"]["EngCo"] = engCo
                            self.jsonControls["Registration"]["EngSurveyorName"] = engSvyName
                            self.jsonControls["Registration"]["EngSurveyorNumber"] = engSvyNum
                            self.appendReport("\tInformation Match Found, Book No. {}, pages {}: Passed\n".format(bookNo, pagesNo))
            if self.jsonChecks["MapGeometry"] is not "Pass":
                self.appendReport("\tTract map information not found in server: Failed\n")

        else:
            self.appendReport("\tChecking Tract Maps Server Features Failed: Script outside OCPW Domain.")

        return




    #---------- AMC Class Function: Checks for Parcel Information ----------#

    def checkServerParcelMaps(self):
        """AMC Class Function: Parcel Map Checking Information
        Checks for Parcel Information from Server Geodatabase
        """
        self.appendReport(f"Parcel Map Server Location Checks")

        # If PFRDNET domain (and server) exists:
        if self.ocserver:
            self.serverPM = os.path.join(self.ocserver, "OCSurvey.DBO.PARCEL_MAPS") # Check with server for name
            self.appendReport("\tChecking Parcel Maps Server Features: OCSurvey.DBO.PARCEL_MAPS")
            self.appendReport("\tSearching Parcel Map Geometry for information")

            # Create a copy of the map layer in the geodatabase:
            arcpy.MakeFeatureLayer_management(self.serverPM, "parcelmaps_lyr")

            # Not Fully Implemented

        else:
            self.appendReport("\tChecking Parcel Maps Server Features Failed: Script outside OCPW Domain.")

        return




    #---------- AMC Class Function: Checks for Record of Survey Information ----------#

    def checkServerRecordsOfSurvey(self):
        """AMC Class Function: Record of Survey Map Checking Information
        Checks for Record of Survey Information from Server Geodatabase
        """
        self.appendReport(f"Tract Map Server Location Checks")

        # If PFRDNET domain (and server) exists:
        if self.ocserver:
            self.serverRSM = os.path.join(self.ocserver, "OCSurvey.DBO.RECORD_OF_SURVEY") # Check with server for name
            self.appendReport("\tChecking Record of Survey Maps Server Features: OCSurvey.DBO.RECORD_OF_SURVEY_MAPS")
            self.appendReport("\tSearching Record of Survey Map Geometry for information")

            # Create a copy of the map layer in the geodatabase:
            arcpy.MakeFeatureLayer_management(self.serverRSM, "recordofsurveymaps_lyr")

            # Not Fully implemented

        else:
            self.appendReport("\tChecking Record of Survey Maps Server Features Failed: Script outside OCPW Domain.")

        return




    #---------- AMC Class Function: Truncating Values ----------#

    def truncate(self, v, n):
        """AMC Class Function: Truncating values
        Truncates coordinates at the n-th decimal places, for the value v (double)
        """
        return math.floor(v * 10 ** n) / 10 ** n




    #---------- AMC Class Function: Get the Boundary Course Traverse Path ----------#

    def traverseCourse(self):
        """AMC Class Function: Boundary Course Traverse Path
        Obtains the course for the boundary traverse path
        """
        # Create empty directionaries for the pair of lines (either direction from the point of beginning or TPOB) to be selected, and the segments of multiline coordinates and OIDs from the boundary feature class in the geodatabase
        pair = {}
        segments = {}
        
        self.appendReport("Traverse Course Report")

        # Rounding TPOB coordinates
        if type(self.tpob) is tuple:
            rtpob = tuple(self.truncate(t, self.tolerance) for t in self.tpob)
        elif type(self.tpob) is list:
            rtpob = list(tuple(self.truncate(t, self.tolerance) for t in pair) for pair in self.tpob)


        # If this is a single boundary polygon, then loop through boundary multilines and get OIDs and coordinates
        if self.boundaryCase == "Single":

            segments[1]={}
            with arcpy.da.SearchCursor("PIQ", ["OID@", "SHAPE@"]) as cursor:
                for row in cursor:
                    oid = row[0] # the multiline segment OID
                    start = row[1].firstPoint.X, row[1].firstPoint.Y # the initial start coordinates
                    end = row[1].lastPoint.X, row[1].lastPoint.Y # the initial end coordinates

                    # Update the segments dictionary to hold the segment data for each OID
                    segments[1][oid] = {"oid": oid, "start": start, "end": end, "reversed": False}

                    # Will check later in the code if there are results populated
                    coor = None

                    # Rounding start and end coordinates
                    rstart = tuple(self.truncate(s, self.tolerance) for s in start)
                    rend = tuple(self.truncate(e, self.tolerance) for e in end)

                    # Check to see if the true point of beginning is in one of these coordinates
                    if rstart == rtpob:
                        coor = start, end
                        reversed = False
                    elif rend == rtpob:
                        coor = end, start
                        reversed = True

                    if coor is not None:
                        pair["{}".format(oid)] = {}
                        pair["{}".format(oid)]["coor"] = coor
                        pair["{}".format(oid)]["reversed"] = reversed

            # Outside the arcpy row loop - choose which of the two coordinates is moving clockwise or counter-clockwise
            pts = []
            for i in pair:
                ptA = pair[i]["coor"][0]
                ptB = pair[i]["coor"][1]

                # Finds the angle degree difference from the centroid
                deg = math.degrees(math.atan2(ptA[1] - self.centroid[1], ptA[0] - self.centroid[0])) - math.degrees(math.atan2(ptB[1] - self.centroid[1], ptB[0] - self.centroid[0]))
                pts.append((i, deg))

            # Check the direction provided by the user, or if none, use clockwise direction (default)
            if self.direction is None or self.direction == "clockwise":
                self.appendReport("\tCourse Direction: clockwise")
                # Selects the largest angle (clockwise)
                seloid = int([i[0] for i in pts if max([j[1] for j in pts]) == i[1]][0])
                selrow = pair[str(seloid)]
            elif direction == "counter-clockwise":
                self.appendReport("\tDirection: counter-clockwise")
                # Selects the smallest angle (counter-clockwise)
                seloid = int([i[0] for i in pts if min([j[1] for j in pts]) == i[1]][0])
                selrow = pair[str(seloid)]

            # Once we select the right start line segment, we can populate the first entry of the course (with orderID = 1)
            self.course = {}
            self.course[1] = {}
            self.course[1]["oid"] = seloid
            self.course[1]["start"] = selrow["coor"][0]
            self.course[1]["end"] = selrow["coor"][1]
            self.course[1]["reversed"] = selrow["reversed"]

            # Now, given the first segment, we will run the loop for all the segments of the lines, and try to find the next start of the line (correcting at the same time the start/end coordinates of the initial feature class to make sure that start --> end follows a clockwise direction).
            while len(self.course) < len(segments[1]): # runs until the course includes all the line segment
                nextLine = self.nextCourseSegment(self.course, segments[1]) # calls the getnext function above and obtains the data of the next line
                nextKey = [key for key in nextLine.keys()][0] # get the OID of the next line
                order = len(self.course) + 1 # update the orderID
                # Populate the next entry in the course JSON.
                self.course[order] = {}
                self.course[order]["oid"] = nextKey
                self.course[order]["start"] = nextLine[nextKey]["start"]
                self.course[order]["end"] = nextLine[nextKey]["end"]
                self.course[order]["reversed"] = nextLine[nextKey]["reversed"]

            # Finally, create an course order ID field (COID) in the boundary feature class and populate it with the values of the course
            arcpy.AddField_management("PIQ", "coid", "LONG", field_alias="Course Order ID")
            with arcpy.da.UpdateCursor("PIQ", ["OID@", "SHAPE@", "coid"]) as cursor:
                for row in cursor:
                    oid = row[0]
                    row[2] = [i for i in self.course if self.course[i]["oid"] == oid][0]
                    cursor.updateRow(row)

            # Write out the course to the report
            for i in self.course:
                self.appendReport("\tCourse Order: {}".format(i))
                self.appendReport("\t\tCourse OID: {}".format(self.course[i]["oid"]))
                self.appendReport("\t\tCourse start point: {}".format(self.course[i]["start"]))
                self.appendReport("\t\tCourse end point: {}".format(self.course[i]["end"]))
                self.appendReport("\t\tCourse reversal: {}".format(self.course[i]["reversed"]))

            # Check the size of the course
            if len(self.course) == len(segments):
                self.appendReport("\tTraverse Course Complete: Passed\n")
            else:
                self.appendReport("\tTraverse Course Incomplete: Failed\n")


        # If this is a separate boundary polygon, then loop through boundary multilines and get OIDs and coordinates
        elif self.boundaryCase == "Separate":
            
            # Create empty directionaries for the pair of lines (either direction from the point of beginning or TPOB) to be selected, and the segments of multiline coordinates and OIDs from the boundary feature class in the geodatabase
            self.course = {}

            # Loop through the parcels layer
            with arcpy.da.SearchCursor("PARCELS", ["OID@"]) as cursor1:
                for row1 in cursor1:
                    # Get the object ID for each of the parcels
                    oid1 = row1[0]
                    segments[oid1]={}
                    
                    # Select the layer with this OBJECTID
                    layer1 = arcpy.SelectLayerByAttribute_management("PARCELS", "NEW_SELECTION", "OBJECTID = {}".format(oid1))

                    # Select all the multiline segment whose boundary touches the selected parcel area
                    layer2 = arcpy.SelectLayerByLocation_management("PIQ", "BOUNDARY_TOUCHES", layer1, None, "NEW_SELECTION", "NOT_INVERT")
                    
                    # Loop through the selected muiltiline segments and get the line OBJECTIDs and properties
                    with arcpy.da.SearchCursor(layer2, ["OID@", "SHAPE@"]) as cursor2:
                        for row2 in cursor2:
                            oid2 = row2[0]
                            start = row2[1].firstPoint.X, row2[1].firstPoint.Y # the initial start coordinates
                            end = row2[1].lastPoint.X, row2[1].lastPoint.Y # the initial end coordinates
                            # update the segments dictionary to hold the segment data for each OID and parcel
                            segments[oid1][oid2] = {"oid": oid2, "start": start, "end":end, "reversed": False}

                            # Will check later in the code if there are results populated
                            coor = None

                            # Rounding start and end coordinates
                            rstart = tuple(self.truncate(s, self.tolerance) for s in start)
                            rend = tuple(self.truncate(e, self.tolerance) for e in end)

                            # Check to see if the true point of beginning is in one of these coordinates

                            if type(self.tpob) is list:
                                for t in rtpob:
                                    if rstart == t:
                                        coor = start, end
                                        reversed = False
                                    elif rend == t:
                                        coor = end, start
                                        reversed = True

                            if coor is not None:
                                pair["{}".format(oid2)] = {}
                                pair["{}".format(oid2)]["coor"] = coor
                                pair["{}".format(oid2)]["reversed"] = reversed

                    # Outside the arcpy row loop - choose which of the two coordinates is moving clockwise or counter-clockwise
                    pts = []
                    for i in pair:
                        ptA = pair[i]["coor"][0]
                        ptB = pair[i]["coor"][1]

                        # Finds the angle degree difference from the centroid
                        deg = math.degrees(math.atan2(ptA[1] - self.jsonControls["Centroid"][oid1][1], ptA[0] - self.jsonControls["Centroid"][oid1][0])) - math.degrees(math.atan2(ptB[1] -self.jsonControls["Centroid"][oid1][1], ptB[0] - self.jsonControls["Centroid"][oid1][0]))
                        pts.append((i, deg))

                    # Check the direction provided by the user, or if none, use clockwise direction (default)
                    if self.direction is None or self.direction == "clockwise":
                        self.appendReport("\tCourse Direction: clockwise")
                        # Selects the largest angle (clockwise)
                        seloid = int([i[0] for i in pts if max([j[1] for j in pts]) == i[1]][0])
                        selrow = pair[str(seloid)]
                    elif direction == "counter-clockwise":
                        self.appendReport("\tDirection: counter-clockwise")
                        # Selects the smallest angle (counter-clockwise)
                        seloid = int([i[0] for i in pts if min([j[1] for j in pts]) == i[1]][0])
                        selrow = pair[str(seloid)]

                    # Once we select the right start line segment, we can populate the first entry of the course (with orderID = oid1)
                    self.course[oid1]={}                    
                    self.course[oid1][1] = {}
                    self.course[oid1][1]["oid"] = seloid
                    self.course[oid1][1]["start"] = selrow["coor"][0]
                    self.course[oid1][1]["end"] = selrow["coor"][1]
                    self.course[oid1][1]["reversed"] = selrow["reversed"]

                    # Now, given the first segment, we will run the loop for all the segments of the lines, and try to find the next start of the line (correcting at the same time the start/end coordinates of the initial feature class to make sure that start --> end follows a clockwise direction).
                    while len(self.course[oid1]) < len(segments[oid1][1]): # runs until the course includes all the line segment
                        nextLine = self.nextCourseSegment(self.course[oid1], segments[oid1][1]) # calls the getnext function above and obtains the data of the next line
                        nextKey = [key for key in nextLine.keys()][0] # get the OID of the next line
                        order = len(self.course[oid1]) + 1 # update the orderID
                        # Populate the next entry in the course JSON.
                        self.course[oid1][order] = {}
                        self.course[oid1][order]["oid"] = nextKey
                        self.course[oid1][order]["start"] = nextLine[nextKey]["start"]
                        self.course[oid1][order]["end"] = nextLine[nextKey]["end"]
                        self.course[oid1][order]["reversed"] = nextLine[nextKey]["reversed"]

                    # Create a parcel ID field (POID) in the boundary lines feature class and populate it with the values of the parcel
                    arcpy.AddField_management("PIQ", "poid", "LONG", field_alias="Parcel ID")
                    with arcpy.da.UpdateCursor("PIQ", ["OID@", "SHAPE@", "poid"]) as cursor:
                        for row in cursor:
                            oid = row[0]
                            row[2] = oid1
                            cursor.updateRow(row)

                    # Finally, create an course order ID field (COID) in the boundary feature class and populate it with the values of the course
                    arcpy.AddField_management("PIQ", "coid", "LONG", field_alias="Course Order ID")
                    with arcpy.da.UpdateCursor("PIQ", ["OID@", "SHAPE@", "coid"]) as cursor:
                        for row in cursor:
                            oid = row[0]
                            if self.course[oid1]["oid"] == oid:
                                row[2] = self.course[oid1]["oid"]
                            cursor.updateRow(row)

                    # Write out the course to the report
                    for i in self.course[oid1]:
                        self.appendReport("\tCourse Order: {}".format(i))
                        self.appendReport("\t\tCourse OID: {}".format(self.course[oid1][i]["oid"]))
                        self.appendReport("\t\tCourse start point: {}".format(self.course[oid1][i]["start"]))
                        self.appendReport("\t\tCourse end point: {}".format(self.course[oid1][i]["end"]))
                        self.appendReport("\t\tCourse reversal: {}".format(self.course[oid1][i]["reversed"]))

                    # Check the size of the course
                    if len(self.course[oid1]) == len(segments[oid1]):
                        self.appendReport("\tTraverse Course for Parcel {} Complete: Passed\n".format(oid1))
                    else:
                        self.appendReport("\tTraverse Course for Parcel {} Incomplete: Failed\n".format(oid1))

        elif self.boundaryCase == "Adjacent":
            None
        elif self.boundaryCase == "Not a Part":
            None

        return




    #---------- AMC Class Function: Obtain the Next Course Segment ----------#

    def nextCourseSegment(self, course, segments):
        """AMC Class Function: Get next segment in boundary course
        Gets the next course coordinate based on the initial line (course[1]), and the line segment coordinates from ArcGIS Boundary Feature class. Returns a JSON string indexed by the order ID (the order to which the lines are added to the course), and for each item, the Boundary feature class OBJECTID, its true start and end coordinates (reversed from the feature class line direction if needed - always clockwise).
        """
        # This is the existing (initial) OID
        existing = [course[i]["oid"] for i in course.keys()]
        # Get the endpoint of the existing feature segment
        lastend = course[len(course)]["end"]
        result = {}
        # Search all segments to find the one whose startpoint or endpoint is the same with the last endpoint.
        for key in segments:
            if key not in existing:
                if lastend == segments[key]["start"]:
                    result[key] = {}
                    result[key]["start"] = segments[key]["start"]
                    result[key]["end"] = segments[key]["end"]
                    result[key]["reversed"] = False
                elif lastend == segments[key]["end"]:
                    result[key] = {}
                    result[key]["start"] = segments[key]["end"]
                    result[key]["end"] = segments[key]["start"]
                    result[key]["reversed"] = True
        if len(result) == 1:
            return result




    #---------- AMC Class Function: Correct Boundary Geometry ----------#

    def correctBoundaryGeometry(self):
        """AMC Class Function: Correct Boundary Geometry
        Checks and corrects (if needed) the boundary course geometry given a course and a direction (clockwise or counter-clockwise). The function checks the start and endpoints and if need reversing it updating the feature class's multiline geometry in the geodatabase.
        """
        self.appendReport("Boundary Multiline Geometry Correction Check")

        # Update loop of the features in the geodatabase
        with arcpy.da.UpdateCursor("PIQ", ["OID@", "SHAPE@"]) as cursor:
            for row in cursor:
                oid = row[0]
                wkt = row[1].WKT
                start = row[1].firstPoint.X, row[1].firstPoint.Y
                end = row[1].lastPoint.X, row[1].lastPoint.Y
                cid = [self.course[i] for i in self.course if self.course[i]["oid"] == oid][0]
                if cid["start"] == start and cid["end"] == end:
                    self.appendReport("\tOID {}: keeping original direction".format(oid))
                    rwkt = wkt
                elif cid["start"] == end and cid["end"] == start:
                    self.appendReport("\tOID {}: reversing direction".format(oid))
                    split = wkt.split("((")[1].split("))")[0].split(", ")
                    split.reverse()
                    rwkt = wkt.split("((")[0] + "((" + (", ").join(split) + "))"
                geom = arcpy.FromWKT(rwkt, self.sr)
                row[1] = geom
                cursor.updateRow(row)

        self.jsonChecks["GeometryCorrections"] = "Pass"
        self.appendReport("\tGeometry Corrections Completed: Pass\n\n")

        return




    #---------- AMC Class Function: Decimal Degrees to Degrees-Minutes-Seconds ----------#

    def dd2dms(self, dd):
        """AMC Class Function: Decimal Degrees to Degrees-Minutes-Seconds.
        Returns formatted coordinates of the Degrees:Minutes:Seconds format. This secondary function restructures decimal degree coordinates into degree/minutes/seconds coordinates. It is called from the main module function.
        """
        decimaldegree = dd
        minutes = decimaldegree%1.0*60
        seconds = minutes%1.0*60
        dms = u'{0:02}\xb0{1:02}\'{2:02}"'.format(int(math.floor(decimaldegree)), int(math.floor(minutes)), int(seconds))
        arcpy.AddMessage(dms)
        return dms




    #---------- AMC Class Function: Bearing to Word ----------#

    def bearingLabel(self, bearing):
        """AMC Class Function: Bearing to Word
        Returns the corresponding direction word based on radial bearing values
        """
        if 0 < bearing <= 22.5:
            bWord = "northerly"
        elif 22.5 < bearing <= 67.5:
            bWord = "northeasterly"
        elif 67.5 < bearing <= 112.5:
            bWord = "easterly"
        elif 112.5 < bearing <= 157.5:
            bWord = "southeasterly"
        elif 157.5 < bearing <= 202.5:
            bWord = "southerly"
        elif 202.5 < bearing <= 247.5:
            bWord = "southwesterly"
        elif 247.5 < bearing <= 292.5:
            bWord = "westerly"
        elif 292.5 < bearing <= 337.5:
            bWord = "northwesterly"
        else:
            bWord = "northerly"

        return bWord





    #---------- AMC Class Function: Map Document Description ----------#
    
    def describeMapDocument(self):
        """AMC Class Function: Map Document Description
        Generates a description of the map document
        """
        
        # Number of parcels in the boundary feature class
        nparcels = self.jsonControls["Parcels"]
        # Map type
        maptype = self.jsonControls["MapType"]
        if maptype == "Tract":
            kind = "Lot"
        elif maptype == "Parcel" or maptype == "Record of Survey":
            kind = "Parcel"

        if nparcels == 1:
            # If portion of lot, then use "That", else if All, use "All"
            # Need to determine if it is all or portion of a lot/parcel (TBD later)
            pre = "That portion of {} 1".format(kind)
        elif nparcels > 1:
            temp = []
            for i in range(nparcels):
                if i+1 < nparcels:
                    temp.append(str(i+1))
                elif i+1 == nparcels:
                    temp.append("and {}".format(i+1))
            temp2 = ", ".join(temp)

            pre = "These portions of {} {}".format(kind, temp2)

        # Optain the map information from the JSON Controls dataset
        loctype = self.jsonControls["Location"]["Type"]
        locname = self.jsonControls["Location"]["Name"]
        loccounty = self.jsonControls["Location"]["County"]
        mapid = self.jsonControls["MapID"]
        mapbooktype = self.jsonControls["MapBookType"]
        bookInfo = self.jsonControls["Book"]
        bookNo = bookInfo["No"]
        pagesNo = bookInfo["Pages"]

        # Generate a map description
        self.mapdesc = "{} of {} No. {}, in the {}, County of {}, State of California, as per map filed in Book {}, pages {} of {} in the Office of the County Recorder of said County, more particularly described as follows:".format(pre, maptype, mapid, locname, loccounty, bookNo, pagesNo, mapbooktype)

        return




    #---------- AMC Class Function: Describe Horizontal Controls ----------#

    def describeHorizontalControls(self):
        """AMC Class Function: Describe Horizontal Controls
        Obtains and generates the Preamp description from horizontal geodetic controls to the point of beginning
        """

        tpobx, tpoby = self.tpob
        gpspoints = self.jsonControls["GPS"]

        if len(gpspoints) == 2:
            # Calculate distances to the parcel"s centroid for each GPS point
            dist1 = math.hypot((gpspoints["1"]["x"] - self.centroid[0]), (gpspoints["1"]["y"] - self.centroid[1]))
            dist2 = math.hypot((gpspoints["2"]["x"] - self.centroid[0]), (gpspoints["2"]["y"] - self.centroid[1]))
            # Order from the most distant to the closest to the parcel points
            gpsorder = {}
            if dist1 >= dist2:
                gpsorder["HC1"] = gpspoints["1"]
                gpsorder["HC2"] = gpspoints["2"]
            elif dist1 < dist2:
                gpsorder["HC1"] = gpspoints["2"]
                gpsorder["HC2"] = gpspoints["1"]

        # GPS ID for horizontal control points
        hc1id, hc2id = gpsorder["HC1"]["id"], gpsorder["HC2"]["id"]

        # GPS coordinates for first control point (grid and ground)
        hc1x, hc1y = self.truncate(gpsorder["HC1"]["x"], self.tolerance), self.truncate(gpsorder["HC1"]["y"], self.tolerance)
        ghc1x, ghc1y = self.truncate(gpsorder["HC1"]["x"]/self.scalefactor, self.tolerance), self.truncate(gpsorder["HC1"]["y"]/self.scalefactor, self.tolerance)

        # GPS coordinates for second control point (grid and ground)
        hc2x, hc2y = self.truncate(gpsorder["HC2"]["x"], self.tolerance), self.truncate(gpsorder["HC2"]["y"], self.tolerance)
        ghc2x, ghc2y = self.truncate(gpsorder["HC2"]["x"]/self.scalefactor, self.tolerance), self.truncate(gpsorder["HC2"]["y"]/self.scalefactor, self.tolerance)
        
        # Bearing and distances (distances for both grid and ground)
        hc1bearing = math.degrees(math.atan2((hc2x - hc1x), (hc2y - hc1y))) % 360
        hc1distance = math.hypot((hc2x - hc1x), (hc2y - hc1y))
        ghc1distance = hc1distance / self.scalefactor
        hc2bearing = math.degrees(math.atan2((tpobx - hc2x), (tpoby - hc2y))) % 360
        hc2distance = math.hypot((tpobx - hc2x), (tpoby - hc2y))
        ghc2distance = hc2distance/ self.scalefactor
        annotation2 = self.labelBearingDistance(hc2bearing, hc2distance)
        gannotation2 = self.labelBearingDistance(hc2bearing, ghc2distance)

        # Get the first feature in the boundary course
        firstjson = [self.jsonBoundary[i] for i in self.jsonBoundary if self.jsonBoundary[i]["coid"] == 1][0]

        # if the first feature is a curve
        if firstjson["shapetype"] == "Curve":
            midbearing = firstjson["midbearing"]
            radius = firstjson["radius"]
            startx, starty = firstjson["startx"], firstjson["starty"]
            centerx, centery = firstjson["centerx"], firstjson["centery"]
            radbearing_cs = firstjson["radbearing_cs"]

            if 0 <= radbearing_cs <= 90:
                dbearing = "North {} East".format(self.dd2dms(radbearing_cs))
            elif 90 < radbearing_cs <= 180:
                dbearing = "South {} East".format(self.dd2dms(180 - radbearing_cs))
            elif 180 < radbearing_cs <= 270:
                dbearing = "South {} West".format(self.dd2dms(radbearing_cs - 180))
            elif 270 < radbearing_cs <= 360:
                dbearing = "North {} West".format(self.dd2dms(360 - radbearing_cs))

            if firstjson["radtangent"] == "Tangent":
                predesc = ", to the beginning of a curve, concave {}, and having a radius of {:.2f} feet, a radial bearing to said beginning of curve bears {}".format(self.bearingLabel(midbearing), self.truncate(radius, self.tolerance), dbearing)
                gpredesc = ", to the beginning of a curve, concave {}, and having a radius of {:.2f} feet, a radial bearing to said beginning of curve bears {}".format(self.bearingLabel(midbearing), self.truncate(radius/self.scalefactor, self.tolerance), dbearing)

            elif firstjson["radtangent"] == "Reverse":
                predesc = ", to the beginning of a reverse curve {}, and having a radius of {:.2f} feet, a radial bearing to said beginning of curve bears {}".format(self.bearingLabel(midbearing), self.truncate(radius, self.tolerance), dbearing)
                gpredesc = ", to the beginning of a reverse curve {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}".format()

            elif firstjson["radtangent"] == "Compound":
                predesc = ", to the beginning of a compound curve {}, and having a radius of {:.2f} feet, a radial bearing to said beginning of curve bears {}".format(self.bearingLabel(midbearing), self.truncate(radius, self.tolerance), dbearing)
                gpredesc = ", to the beginning of a compound curve {}, and having a radius of {:.2f} feet, a radial bearing to said beginning of curve bears {}".format(self.bearingLabel(midbearing), self.truncate(radius/self.scalefactor, self.tolerance), dbearing)

            else:
                predesc = ", to the beginning of a non-tangent curve, concave {}, and having a radius of {:.2f} feet, a radial bearing to said beginning of curve bears {}".format(self.bearingLabel(midbearing), self.truncate(radius, self.tolerance), dbearing)
                gpredesc = ", to the beginning of a non-tangent curve, concave {}, and having a radius of {:.2f} feet, a radial bearing to said beginning of curve bears {}".format(self.bearingLabel(midbearing), self.truncate(radius/self.scalefactor, self.tolerance), dbearing)

        else:
            predesc = ""
            gpredesc = ""
    
    
        self.preamp = "COMMENCING at Orange County Horizontal Control Station \"{}\" having a State Plane Coordinate Value of Northing {} and Easting {}; Thence {} to Station \"{}\"; Thence {} to the TRUE POINT OF BEGINNING having a State Plane Coordinate Value of Northing {:.2f} and Easting {:.2f}{}.".format(hc1id, hc1x, hc1y, self.labelBearingDistance(hc1bearing, hc1distance), hc2id, annotation2, self.truncate(tpobx, self.tolerance), self.truncate(tpoby, self.tolerance), predesc)
        self.gpreamp = "COMMENCING at Orange County Horizontal Control Station \"{}\" having a State Plane Coordinate Value of Northing {} and Easting {}; Thence {} to Station \"{}\"; Thence {} to the TRUE POINT OF BEGINNING having a State Plane Coordinate Value of Northing {:.2f} and Easting {:.2f}{}.".format(hc1id, ghc1x, ghc1y, self.labelBearingDistance(hc1bearing, ghc1distance), hc2id, gannotation2, self.truncate(tpobx/self.scalefactor, self.tolerance), self.truncate(tpoby/self.scalefactor, self.tolerance), gpredesc)
        
        return




    #---------- AMC Class Function: Format Labels for Bearing and Distance ----------#

    def labelBearingDistance(self, bearing, distance):
        """AMC Class Function: Format Labels for Bearing and Distance
        Generates a formatted bearing and distance string from coordinates
        """
        if 0 <= bearing <= 90:
            label = "North {} East, {} feet".format(self.dd2dms(self.truncate(bearing, self.tolerance)), self.truncate(distance, self.tolerance))
        elif 90 < bearing <= 180:
            label = "South {} East, {} feet".format(self.dd2dms(self.truncate(180 - bearing, self.tolerance)), self.truncate(distance, self.tolerance))
        elif 180 < bearing <= 270:
            label = "South {} West, {} feet".format(self.dd2dms(self.truncate(bearing - 180, self.tolerance)), self.truncate(distance, self.tolerance))
        elif 270 < bearing <= 360:
            label = "North {}, West, {} feet".format(self.dd2dms(self.truncate(360 - bearing, self.tolerance)), self.truncate(distance, self.tolerance))

        return label



    
    #---------- AMC Class Function: Generate CSV Boundary Table ----------#

    def boundaryToTable(self):
        """AMC Class Function: Generate Boundary Table to CSV data
        Creates a csv-formatted boundary table containing the course data
        """

        if arcpy.Exists("PIQ"):

            # Search fields for the Boundary Featur Class
            searchFields = ["OID@", "SHAPE@", "coid", "shapetype", "nwkt", "startx", "starty", "midx", "midy", "endx", "endy", "midchordx", "midchordy", "centerx", "centery", "bearing", "distance", "height", "arclength", "radius", "midbearing", "delta", "radbearing_cs", "radbearing_sc", "radbearing_ce", "radbearing_st", "radtangent", "desc_grid", "desc_ground", "ann_grid", "ann_ground", "annweb_grid", "annweb_ground"]

            # Field headers (columns) to be written out in the CSV file
            csvFields = ["Segment ID", "Object ID", "Map Type", "Map ID", "Map Book Type", "Tract/Parcel/Map No", "Lot/Parcel No", "Shape Type", "Number of Features in Shape", "Startpoint X","Startpoint Y", "Midpoint X", "Midpoint Y", "Endpoint X", "Endpoint Y", "Mid-chord X", "Mid-chord Y", "Radial Center X", "Radial Center Y", "Line or Chord Bearing", "Line Distance or Chord Length", "Height of Line/Arc", "Arc Length", "Arc Radius", "Mid-chord Bearing to Center", "Radial Curve Angle", "Radial Bearing Center to Start", "Radial Bearing Start to Center", "Radial Bearing Center to End", "Radial Tangent Angle at Start", "Radial Tangent Description", "Legal Description Grid", "Legal Description Ground", "Annotation Grid", "Annotation Ground", "Web Annotation Grid", "Web Annotation Ground"]

            # Create an empty pandas dataframe using the field headers as column labels
            dfb = pandas.DataFrame(columns = csvFields)

            with arcpy.da.SearchCursor("PIQ", searchFields) as cursor:
                for row in cursor:
                    dfb = dfb.append({
                        "Object ID": row[0],
                        "Segment ID": row[2],
                        "Map Type": self.maptype,
                        "Map ID": self.mapid,
                        "Map Book Type": self.mapbooktype,
                        "Tract/Parcel/Map No": self.cadname,
                        "Lot/Parcel No": "Boundary",
                        "Shape Type": row[3],
                        "Number of Features in Shape": row[4],
                        "Startpoint X": row[5],
                        "Startpoint Y": row[6],
                        "Midpoint X": row[7],
                        "Midpoint Y": row[8],
                        "Endpoint X": row[9],
                        "Endpoint Y": row[10],
                        "Mid-chord X": row[11],
                        "Mid-chord Y": row[12],
                        "Radial Center X": row[13],
                        "Radial Center Y": row[14],
                        "Line or Chord Bearing": row[15],
                        "Line Distance or Chord Length": row[16],
                        "Height of Line/Arc": row[17],
                        "Arc Length": row[18],
                        "Arc Radius": row[19],
                        "Mid-chord Bearing to Center": row[20],
                        "Radial Curve Angle": row[21],
                        "Radial Bearing Center to Start": row[22],
                        "Radial Bearing Start to Center": row[23],
                        "Radial Bearing Center to End": row[24],
                        "Radial Tangent Angle at Start": row[25],
                        "Radial Tangent Description": row[26],
                        "Legal Description Grid": row[27],
                        "Legal Description Ground": row[28],
                        "Annotation Grid": row[29],
                        "Annotation Ground": row[30],
                        "Web Annotation Grid": row[31],
                        "Web Annotation Ground": row[32]
                        }, ignore_index=True)

            
            # Sort the pandas data frame by course segment ID (COID)
            dfb = dfb.sort_values(by = "Segment ID")
            # Reset the index
            dfb = dfb.reset_index(drop=True)


            # Create a Pandas excel writer usin xlsxwriter as the engine
            writer = pandas.ExcelWriter("BoundaryData.xlsx", engine="xlsxwriter")

            # Convert results panda dataframe to an exlsxwriter excel object
            dfb.to_excel(writer, sheet_name = "Boundary", header=True, index=False)

            # Close the pandas excel writer and output the excel file
            writer.save()

            self.appendReport("\nBoundary Tabulation: Pass\n\n")


        else:

            self.appendReport("\nBoundary Tabulation: Failed\n\n")


 


#========================= END OF PROGRAM =========================#
