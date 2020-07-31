##############################################################
# PYTHON AUTOMATED MAP CHECKING ANALYSIS                     #
# AMC Class Definition                                       #
# Version: 1.2                                               #
# Author: Dr. Kostas Alexandridis, GISP                      #
# Organization: OC Survey Geospatial Services                #
# Date: January 2020                                         #
##############################################################

# Importing the required libraries into the project
import arcpy, os, math, json, datetime, socket


#============================================================#
#  MAIN CLASS: amc                                           #
#============================================================#

class cad2amc(object):
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
        f.write(f"{'EXECUTION REPORT':^80s}\n")
        f.write(f"{'County of Orange, OC Survey, Geospatial Services':^80s}\n")
        self.now = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        f.write(f"{f'Python Class Execution Date and Time: {self.now}':^80s}\n\n")
        f.close()

        return





    #========================= PART II: MAIN CLASS FUNCTIONS =========================#


    #-------------------- AMC Class Function: Base Checks --------------------#
    def baseChecks(self):
        """
        AMC Class Function: Import CAD Drawing and perform basic Checks
        Imports the CAD drawing and performs basic layer and geometry checks
        """

        self.appendReport(f"\n{' PART 1: AMC BASE CHECKS EXECUTION ':-^80s}\n")
        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport(f"Script started on: {stime}\n")

        #Define new json to hold record checks:
        jsonChecks = {}
        jsonChecks["LayerChecks"] = {}
        jsonChecks["BoundaryChecks"] = {}
        jsonChecks["BoundaryCorrections"] = {}
        jsonChecks["BoundaryLines"] = {}
        jsonChecks["BoundaryClosure"] = {}
        jsonChecks["GeometryCorrections"] = {}
        jsonChecks["GPSChecks"] = {}
        jsonChecks["GeodeticControlPoints"] = {}
        jsonChecks["TPOB"] = {}
        jsonChecks["Location"] = {}
        jsonChecks["MapGeometry"] = {}
        self.jsonChecks = jsonChecks

        jsonControls = {}
        jsonControls["Title"] = self.cadname
        jsonControls["ScaleFactor"] = self.scalefactor
        jsonControls["MapType"] = {}
        jsonControls["MapID"] = {}
        jsonControls["MapBookType"] = {}
        jsonControls["Book"] = {}
        jsonControls["Book"]["No"] = "<Book No.>"
        jsonControls["Book"]["Pages"] = "<Pages>"
        jsonControls["Registration"] = {}
        jsonControls["Registration"]["EngCo"] = {}
        jsonControls["Registration"]["EngSurveyorName"] = {}
        jsonControls["Registration"]["EngSurveyorNumber"] = {}
        jsonControls["Location"] = {}
        jsonControls["Location"]["Type"] = {}
        jsonControls["Location"]["Name"] = {}
        jsonControls["Location"]["County"] = {}
        jsonControls["Location"]["State"] = "California"
        jsonControls["GPS"] = {}
        jsonControls["Centroid"] = {}
        jsonControls["Areas"] = {}
        jsonControls["TPOB"] = {}
        self.jsonControls = jsonControls

        self.jsonBoundary = {}
        self.jsonLegalDescription = {}

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
        self.appendReport(f"Identifying Map Characteristics from CAD drawing:\n\tMap Type: {jsonControls['MapType']}\n\tMap ID: {jsonControls['MapID']}\n\tMap Book Type: {jsonControls['MapBookType']}\n")

        # Define the project"s spatial reference: NAD83 State Plane California Zone 6
        self.sr = arcpy.SpatialReference(102646)
        self.appendReport(f"Setting Spatial Reference: NAD83 State Plane California Zone 6 (ArcGIS ID: 102646)\n")

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
        arcpy.CADToGeodatabase_conversion(self.cadpath, self.gdbpath, self.cadname, "1000", self.sr)
        self.appendReport(self.getAgpMsg(1))
        self.appendReport(self.getAgpMsg(1))

        # Check 2: Check for the presence of all the layers in CAD drawing
        self.checkLayers()

        # Check 3: Check for the GPS Control Points in CAD drawing
        self.checkGPS()

        # Check 3a: Check for geodetic control geometries
        self.checkGeodeticControls()

        # Check 4: Check for the (True) Point of Beginning
        self.checkPOB()

        # Check 5: Checking boundary layers
        self.checkEBL()

        # Check 6: Checks for closure
        self.checkClosureCentroid()

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
        self.nParcels = self.jsonControls["Parcels"] = int(arcpy.GetCount_management("BoundaryArea")[0])
        self.appendReport(f"Number of parcels in boundary area: {self.nParcels}\n")

        # Get the course data
        self.traverseCourse()

        # Check the boundary geometry and correct if needed
        self.correctBoundaryGeometry()

        etime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport(f"Script completed on: {etime}\n\n")

        return 








    #---------- AMC Class Function: Boundary Processing ----------#

    def boundaryProcessing(self):
        """
        AMC Class Function: Processing CAD Boundaries
        This function processes the Boundaries of the CAD drawing and performs basic checks. It also processes the boundary multiline features, create fields in the geodatabase's feature class, mathematically computes bearing, distances, radial angles, etc, for annotation labels and legal descriptions.
        """
        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport(f"\n{' PART 2: AMC BOUNDARY FEATURE PROCESSING ':-^80s}\n")
        self.appendReport(f"Script Started on: {stime}\n")

        self.appendReport(f"Processing Boundary Features for {self.cadname}")

        # Create fields in boundary feature class to hold types and coordinates
        boundaryFields = [["tpob", "TEXT", "", "TPOB Present"],
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
            arcpy.AddField_management("Boundary", field_name = field[0], field_type = field[1], field_length = field[2], field_alias = field[3])

        self.appendReport(f"\tAdded {len(boundaryFields)} new fields to boundary feature class")

        # Check boundary closure and populate types and coordinates
        with arcpy.da.UpdateCursor("Boundary", ["OID@", "SHAPE@"] + ["coid"] + [field[0] for field in boundaryFields]) as cursor:

            # Create empty JSON string to hold results of the loop
            self.jsonBoundary = {}
            # Define fields for JSON data string structure
            jsonFields = ["coid", "tpob", "shapetype", "wkt", "nwkt", "startx", "starty", "midx", "midy", "endx", "endy", "midchordx", "midchordy", "centerx", "centery", "bearing", "distance", "height", "arclength", "radius", "midbearing", "delta", "radbearing_cs", "radbearing_sc", "radbearing_ce", "radbearing_st", "radtangent", "desc_grid", "desc_ground", "ann_grid", "ann_ground", "annweb_grid", "annweb_ground"]

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
                row[7], row[8] = self.jsonBoundary[oid]["startx"], self.jsonBoundary[oid]["starty"] = start

                # Mid point coordinates
                mid = midx, midy = row[1].positionAlongLine(0.5, True).firstPoint.X, row[1].positionAlongLine(0.5, True).firstPoint.Y
                row[9], row[10] = self.jsonBoundary[oid]["midx"], self.jsonBoundary[oid]["midy"] = mid

                # End point coordinates
                end = endx, endy = row[1].lastPoint.X, row[1].lastPoint.Y
                row[11], row[12] = self.jsonBoundary[oid]["endx"], self.jsonBoundary[oid]["endy"] = end

                # Mid-chord coordinates
                midchord = midchordx, midchordy = (startx + endx)/2, (starty + endy)/2
                row[13], row[14] = self.jsonBoundary[oid]["midchordx"], self.jsonBoundary[oid]["midchordy"] = midchord

                # Line bearing or chord bearing
                bearing = math.degrees(math.atan2(endx - startx, endy - starty)) % 360
                row[17] = self.jsonBoundary[oid]["bearing"] = bearing

                # Line distance or chord length
                distance = math.hypot(endx - startx, endy - starty)
                row[18] = self.jsonBoundary[oid]["distance"] = distance


                # Mid-chord bearing
                midbearing = math.degrees(math.atan2(midchordx - midx, midchordy - midy)) % 360
                row[22] = self.jsonBoundary[oid]["midbearing"] = midbearing

                # Height of Line/Arc
                height = math.hypot(midchordx - midx, midchordy - midy)
                row[19] = self.jsonBoundary[oid]["height"] = height


                # Determine shape type and compute variables for lines and curves

                if height == 0: 
                    # This is a line
                    shapetype = "Line"
                    row[4] = self.jsonBoundary[oid]["shapetype"] = shapetype

                elif height > 0: 
                    # This is a curve
                    shapetype = "Curve"
                    row[4] = self.jsonBoundary[oid]["shapetype"] = shapetype

                    # Arc radius length
                    radius = (height / 2) + ((distance ** 2) / (8 * height))
                    row[21] = self.jsonBoundary[oid]["radius"] = radius

                    # Curve angle (delta)
                    if height > (distance / 2): # below the diameter (more than half circle, e.g., cul-de-sac)
                        delta = (360 - math.degrees(2 * math.asin(distance / (2 * radius)))) % 360
                    else: # above or at the diamerer (less or equal of half  circle)
                        delta = math.degrees( 2 * math.asin(distance / (2 * radius))) % 360
                    row[23] = self.jsonBoundary[oid]["delta"] = delta

                    # The coordinates of the center of the arc/curve
                    center = centerx, centery = midx + (math.sin(math.radians(float(bearing))) * float(radius)), midy + (math.cos(math.radians(float(bearing))) * float(radius))
                    row[15], row[16] = self.jsonBoundary[oid]["centerx"], self.jsonBoundary[oid]["centery"] = center

                    # Tangent Check:
                    radbearing_cs = math.degrees(math.atan2(startx - centerx, starty - centery)) % 360 # Radial bearing: center to start
                    row[24] = self.jsonBoundary[oid]["radbearing_cs"] = radbearing_cs
                    radbearing_sc = math.degrees(math.atan2(centerx - startx, centery - starty)) % 360 # Radial bearing: start to center
                    row[25] = self.jsonBoundary[oid]["radbearing_sc"] = radbearing_sc
                    radbearing_ce = math.degrees(math.atan2(endx - centerx, endy - centery)) % 360 # Radial bearing: center to end
                    row[26] = self.jsonBoundary[oid]["radbearing_ce"] = radbearing_ce
                    radbearing_st = (90 + radbearing_cs) % 360 # Radial Tangent Angle at start
                    row[27] = self.jsonBoundary[oid]["radbearing_st"] = radbearing_st

                    # Calculate arc length:
                    arclength = (2 * math.pi * radius) * (delta / 360) # Arc Length
                    row[20] = self.jsonBoundary[oid]["arclength"] = arclength



                # Match the TPOB with the boundary files:
                coortpob = self.truncate(self.jsonControls["TPOB"]["x"], self.tolerance), self.truncate(self.jsonControls["TPOB"]["y"], self.tolerance)
                coorstart = self.truncate(startx, self.tolerance), self.truncate(starty, self.tolerance)
                if coortpob == coorstart:
                    row[3] = self.jsonBoundary[oid]["tpob"] = True
                else:
                    row[3] = self.jsonBoundary[oid]["tpob"] = False

                # Well Known Text (WKT) from object"s geometry
                wkt = row[1].WKT
                row[5] = self.jsonBoundary[oid]["wkt"] = wkt
            
                # List and number of points in WKT
                wktlist = wkt.split("((")[1].split("))")[0].replace(" 0, ",",").replace(" 0", "").split(",")
                nwkt = len(wktlist) # Number of points in WKT geometry
                row[6] = self.jsonBoundary[oid]["wktcount"] = nwkt

                cursor.updateRow(row)


        self.appendReport("\tCalculated and populated new fields in boundary feature class")


        # Repeat the same loop after writing all the previous fields and variables
        with arcpy.da.UpdateCursor("Boundary", ["OID@", "SHAPE@"] + ["coid"] + [field[0] for field in boundaryFields]) as cursor:
            for row in cursor:
                oid = row[0]
                coid = row[2]
                # Total number of features in feature class:
                nrows = int(arcpy.GetCount_management("Boundary")[0])

                # Get the last feature from the current one looping:
                if coid == 1:
                    lcoid = nrows # Last coid
                elif coid > 1:
                    lcoid = coid - 1

                #---------- Current Feature ----------

                # Get shapetype, start, mid, end, chordlength, midchord and height from feature attributes
                shapetype = row[4]
                start = startx, starty = row[7], row[8]
                mid = midx, midy = row[9], row[10]
                end = endx, endy = row[11], row[12]
                midchord = midchordx, midchordy = row[13], row[14]
                center = centerx, centery = row[15], row[16]
                bearing = row[17]
                distance = row[18]            
                height = row[19]
                arclength = row[20]
                radius = row[21]
                midbearing = row[22]
                delta = row[23]
                radbearing_cs = row[24]
                radbearing_sc = row[25]
                radbearing_ce = row[26]
                radbearing_st = row[27]



                # Get the preamp for the description
                if self.jsonBoundary[oid]["tpob"] is True:
                    preamp = f"Thence from said {self.tpobstring}"
                else:
                    preamp = " Thence"

                # Get the closing for the description
                if coid == nrows:
                    closing = f" to the {self.tpobstring}"
                else:
                    closing = ""


                # If current feature is a line:
                if shapetype == "Line":

                    # Get the line description string depending on the bearing direction
                    if 0 <= bearing <= 90:
                        dbearing = f"North {self.dd2dms(bearing)} East"
                        abearing = f"N {self.dd2dms(bearing)} E"
                    elif 90 < bearing <= 180:
                        dbearing = f"South {self.dd2dms(180 - bearing)} East"
                        abearing = f"S {self.dd2dms(180 - bearing)} E"
                    elif 180 < bearing <= 270:
                        dbearing = f"South {self.dd2dms(bearing - 180)} West"
                        abearing = f"S {self.dd2dms(bearing - 180)} W"
                    elif 270 < bearing <= 360:
                        dbearing = f"North {self.dd2dms(360 - bearing)} West"
                        abearing = f"N {self.dd2dms(360 - bearing)} W"

                    # Legal description (line)
                    desc_grid = f"{preamp} {dbearing}, {self.truncate(distance, self.tolerance):.2f} feet;{closing}"
                    desc_ground = f"{preamp} {dbearing} {self.truncate(distance/self.scalefactor, self.tolerance):.2f} feet;{closing}"
                    row[29] = self.jsonBoundary[oid]["desc_grid"] = desc_grid
                    row[30] = self.jsonBoundary[oid]["desc_ground"] = desc_ground

                    # Annotation (line) for labels and web use
                    ann_grid = f"{abearing}  {self.truncate(distance, self.tolerance):.2f}"
                    ann_ground = f"{abearing}  {self.truncate(distance/self.scalefactor, self.tolerance):.2f}"
                    row[31] = self.jsonBoundary[oid]["ann_grid"] = ann_grid
                    row[32] = self.jsonBoundary[oid]["ann_ground"] = ann_ground
                    annweb_grid = f"{abearing}\n{self.truncate(distance, self.tolerance):.2f}"
                    annweb_ground = f"{abearing}\n{self.truncate(distance/self.scalefactor, self.tolerance):.2f}"
                    row[33] = self.jsonBoundary[oid]["annweb_grid"] = annweb_grid
                    row[34] = self.jsonBoundary[oid]["annweb_ground"] = annweb_ground


                # Else, if current feature is a curve:
                elif shapetype == "Curve":

                    # Premp for description
                    if self.jsonBoundary[oid]["tpob"] is False:
                        preamp = ""

                    # Get the characteristics of the previous (last) feature
                    with arcpy.da.SearchCursor("Boundary", ["OID@", "SHAPE@"] + ["coid"] + [field[0] for field in boundaryFields]) as lcursor:
                        for lrow in lcursor:
                            if lrow[2] == lcoid:
                                loid = lrow[0]
                                ltpob = lrow[3]
                                lshapetype = lrow[4]
                                lstart = lstartx, lstarty = lrow[7], lrow[8]
                                lmid = lmidx, lmidy = lrow[9], lrow[10]
                                lend = lendx, lendy = lrow[11], lrow[12]
                                lmidchord = lmidchordx, lmidchordy = lrow[13], lrow[14]
                                lcenter = lcenterx, lcentery = lrow[15], lrow[16]
                                lbearing = lrow[17]
                                ldistance = lrow[18]
                                lheight = lrow[19]
                                larclength = lrow[20]
                                lradius = lrow[21]
                                lmidbearing = lrow[22]
                                ldelta = lrow[23]
                                lradbearing_cs = lrow[24]
                                lradbearing_sc = lrow[25]
                                lradbearing_ce = lrow[26]
                                lradbearing_st = lrow[27]


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

                    row[28] = self.jsonBoundary[oid]["radtangent"] = radtangent

                    # Curve Description:

                    if radtangent == "Tangent":
                        desc_grid = f"{preamp} to the beginning of a curve, concave {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius, self.tolerance):.2f} feet; Thence {self.bearingLabel(bearing)} along said curve {self.truncate(arclength, self.tolerance):.2f} feet through a central angle of {self.dd2dms(delta)};{closing}"
                        desc_ground = f"{preamp} to the beginning of a curve, concave {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet; Thence {self.bearingLabel(bearing)} along said curve {self.truncate(arclength/self.scalefactor, self.tolerance):.2f} feet through a central angle of {self.dd2dms(delta)};{closing}"
                        ann_grid = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}  R={self.truncate(radius, self.tolerance):.2f}  L={self.truncate(arclength, self.tolerance):.2f}"
                        ann_ground = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}  R={self.truncate(radius/self.scalefactor, self.tolerance):.2f}  L={self.truncate(arclength/self.scalefactor, self.tolerance):.2f}"
                        annweb_grid = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}\nR={self.truncate(radius, self.tolerance):.2f}\nL={self.truncate(arclength, self.tolerance):.2f}"
                        annweb_ground = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}\nR={self.truncate(radius/self.scalefactor, self.tolerance):.2f}\nL={self.truncate(arclength/self.scalefactor, self.tolerance):.2f}"

                    elif radtangent == "Compound":
                        desc_grid = f"{preamp} to the beginning of a compound curve concave {self.bearingLabel(midbearing)} and having a radius of {self.truncate(radius, self.tolerance):.2f} feet; Thence {self.bearingLabel(bearing)} along said curve {self.truncate(arclength, self.tolerance):.2f} feet through a central angle of {self.dd2dms(delta)};{closing}"
                        desc_ground = f"{preamp} to the beginning of a compound curve {self.bearingLabel(midbearing)} and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet; Thence {self.bearingLabel(bearing)} along said curve {self.truncate(arclength/self.scalefactor, self.tolerance):.2f} feet through a central angle of {self.dd2dms(delta)};{closing}"
                        ann_grid = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}  R={self.truncate(radius, self.tolerance):.2f}  L={self.truncate(arclength, self.tolerance):.2f}"
                        ann_ground = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}  R={self.truncate(radius/self.scalefactor, self.tolerance):.2f}  L={self.truncate(arclength/self.scalefactor, self.tolerance):.2f}"
                        annweb_grid = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}\nR={self.truncate(radius, self.tolerance):.2f}\nL={self.truncate(arclength, self.tolerance):.2f}"
                        annweb_ground = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}\nR={self.truncate(radius/self.scalefactor, self.tolerance):.2f}\nL={self.truncate(arclength/self.scalefactor, self.tolerance):.2f}"

                    elif radtangent == "Reverse":
                        desc_grid = f"{preamp} to the beginning of a reverse curve concave {self.bearingLabel(midbearing)} and having a radius of {self.truncate(radius, self.tolerance):.2f} feet; Thence {self.bearingLabel(bearing)} along said curve {self.truncate(arclength, self.tolerance):.2f} feet through a central angle of {self.dd2dms(delta)};{closing}"
                        desc_ground = f"{preamp} to the beginning of a reverse curve concave {self.bearingLabel(midbearing)} and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet; Thence {self.bearingLabel(bearing)} along said curve {self.truncate(arclength/self.scalefactor, self.tolerance):.2f} feet through a central angle of {self.dd2dms(delta)};{closing}"
                        ann_grid = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}  R={self.truncate(radius, self.tolerance):.2f}  L={self.truncate(arclength, self.tolerance):.2f}"
                        ann_ground = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}  R={self.truncate(radius/self.scalefactor, self.tolerance):.2f}  L={self.truncate(arclength/self.scalefactor, self.tolerance):.2f}"
                        annweb_grid = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}\nR={self.truncate(radius, self.tolerance):.2f}\nL={self.truncate(arclength, self.tolerance):.2f}"
                        annweb_ground = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}\nR={self.truncate(radius/self.scalefactor, self.tolerance):.2f}\nL={self.truncate(arclength/self.scalefactor, self.tolerance):.2f}"

                    elif radtangent == "Non-Tangent":
                        # Get the tangent description string depending on the bearing direction
                        if 0 <= radbearing_cs <= 90:
                            dbearing = f"North {self.dd2dms(radbearing_cs)} East"
                        elif 90 < radbearing_cs <= 180:
                            dbearing = f"South {self.dd2dms(180 - radbearing_cs)} East"
                        elif 180 < radbearing_cs <= 270:
                            dbearing = f"South {self.dd2dms(radbearing_cs - 180)} West"
                        elif 270 < radbearing_cs <= 360:
                            dbearing = f"North {self.dd2dms(360 - radbearing_cs)} West"

                        desc_grid = f"{preamp} to the beginning of a non-tangent curve, concave {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius, self.tolerance):.2f} feet, a radial line to said beginning of curve bears {dbearing}; Thence {self.bearingLabel(bearing)} along said curve {self.truncate(arclength, self.tolerance):.2f} feet through a central angle of {self.dd2dms(delta)};{closing}"
                        desc_ground = f"{preamp} to the beginning of a non-tangent curve, concave {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet, a radial line to said beginning of curve bears {dbearing}; Thence {self.bearingLabel(bearing)} along said curve {self.truncate(arclength/self.scalefactor, self.tolerance):.2f} feet through a central angle of {self.dd2dms(delta)};{closing}"
                        ann_grid = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}  R={self.truncate(radius, self.tolerance):.2f}  L={self.truncate(arclength, self.tolerance):.2f}"
                        ann_ground = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}  R={self.truncate(radius/self.scalefactor, self.tolerance):.2f}  L={self.truncate(arclength/self.scalefactor, self.tolerance):.2f}"
                        annweb_grid = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}\nR={self.truncate(radius, self.tolerance):.2f}\nL={self.truncate(arclength, self.tolerance):.2f}"
                        annweb_ground = f"\N{GREEK CAPITAL LETTER DELTA}={self.dd2dms(delta)}\nR={self.truncate(radius/self.scalefactor, self.tolerance):.2f}\nL={self.truncate(arclength/self.scalefactor, self.tolerance):.2f}"

                    # Adding the curve description to feature attributes and JSON data string
                    row[29] = self.jsonBoundary[oid]["desc_grid"] = desc_grid
                    row[30] = self.jsonBoundary[oid]["desc_ground"] = desc_ground
                    row[31] = self.jsonBoundary[oid]["ann_grid"] = ann_grid
                    row[32] = self.jsonBoundary[oid]["ann_ground"] = ann_ground
                    row[33] = self.jsonBoundary[oid]["annweb_grid"] = annweb_grid
                    row[34] = self.jsonBoundary[oid]["annweb_ground"] = annweb_ground

                cursor.updateRow(row)


        self.appendReport("\tGenerated line and curve descriptions for boundary features")



    
        # Make updates and corrections
        with arcpy.da.UpdateCursor("Boundary", ["OID@", "SHAPE@"] + ["coid"] + [field[0] for field in boundaryFields]) as cursor:

            # Loop through lines in multilines
            for row in cursor:
                oid = row[0]
                coid = row[2]
                nrows = int(arcpy.GetCount_management("Boundary")[0]) # Total number of multilines
                shapetype = row[4]
                radtangent = row[28]
                desc_grid = row[29]
                desc_ground = row[30]


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
                with arcpy.da.SearchCursor("Boundary", ["OID@", "SHAPE@"] + ["coid"] + [field[0] for field in boundaryFields]) as lcursor:
                    for lrow in lcursor:
                        if lrow[2] == lcoid:
                            lshapetype = lrow[4]
                            lradtangent = lrow[28]
                            lradbearing_cs = lrow[24]



                # If current feature is a Line or a Non-Tangent curve and the previous is a tangent Curve:
                if shapetype == "Line" or radtangent == "Non-Tangent":
                    if lshapetype == "Curve" and lradtangent == "Tangent":
                        desc_grid = desc_grid.replace("Thence", "Thence non-tangent to said curve")
                        desc_ground = desc_ground.replace("Thence", "Thence non-tangent to said curve")
                        row[29] = desc_grid
                        row[30] = desc_ground
                        self.jsonBoundary[oid]["desc_grid"] = desc_grid
                        self.jsonBoundary[oid]["desc_ground"] = desc_ground

                # If the first feature is a curve:
                if coid == 1 and shapetype == "Curve":
                    #newdesc1 = f"Thence from said {tpobstring} " + desc1.split(";")[1].replace("Thence ", "")
                    desc_grid = desc_grid.split(";")[1]
                    desc_ground = desc_ground.split(";")[1]
                    row[29] = desc_grid
                    row[30] = desc_ground
                    self.jsonBoundary[oid]["desc_grid"] = desc_grid
                    self.jsonBoundary[oid]["desc_ground"] = desc_ground

                # if current feature is a line coming from a curve (radial)
                if shapetype == "Line" and lshapetype == "Curve":
                    if bearing == lradbearing_cs or bearing == (180 + lradbearing_cs) % 360:
                        desc_grid = desc_grid.replace("Thence", "Thence radial to said curve")
                        desc_ground = desc_ground.replace("Thence", "Thence radial to said curve")
                        row[29] = desc_grid
                        row[30] = desc_ground
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
            self.appendReport(f"\tCOID {i+1} ({jrow['shapetype']}): {jrow['ann_grid'].replace('Δ', 'D')}")

        self.appendReport("\nAnnotation Labels (Ground)")
        for i in range(len(self.jsonBoundary)):
            jrow = [self.jsonBoundary[j] for j in self.jsonBoundary if self.jsonBoundary[j]["coid"] == i+1][0]
            self.appendReport(f"\tCOID {i+1} ({jrow['shapetype']}): {jrow['ann_ground'].replace('Δ', 'D')}")

        etime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport(f"\nScript Completed on {etime}\n\n")

        return






    #---------- AMC Class Function: Create Legal Description ----------#

    def createLegalDescription(self):
        """AMC Class Function: Create Legal Description
        Generates a legal description document after boundary processing data
        """

        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport(f"\n{' PART 3: AMC LEGAL DESCRIPTION PROCESSING ':-^80s}\n")
        self.appendReport(f"Script Started on: {stime}\n")


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
        self.appendReport(f"\t{self.mapdesc}")
        self.appendReport(f"\t{self.preamp}")
        self.appendReport(f"\t{self.ld}\n")

        # Write Legal Description to Report (ground)
        self.appendReport("\n\nLEGAL DESCRIPTION (GROUND)\n")
        self.appendReport(f"\t{self.mapdesc}")
        self.appendReport(f"\t{self.gpreamp}")
        self.appendReport(f"\t{self.gld}\n")

        # Compile the JSON data for the legal description
        self.jsonLegalDescription["Map"] = self.mapdesc
        self.jsonLegalDescription["Grid"] = {}
        self.jsonLegalDescription["Grid"]["Preamp"] = self.preamp
        self.jsonLegalDescription["Grid"]["Course"] = self.ld
        self.jsonLegalDescription["Ground"] = {}
        self.jsonLegalDescription["Ground"]["Preamp"] = self.gpreamp
        self.jsonLegalDescription["Ground"]["Course"] = self.gld
        
        etime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport(f"\nScript Completed on {etime}\n\n")

        return


    


    #---------- AMC Class Function: Finalize Report ----------#

    def finalizeReport(self):
        """AMC Class Function: Finalize Report and Execution
        Compiles and exports all data and reports and finishes up the execution
        """
        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport(f"\n{' PART 4: AMC PROCESS FINALIZATION ':-^80s}\n")
        self.appendReport(f"Script Started on: {stime}\n")

        # Compile the final JSON data
        response = {}
        response["Checks"] = self.jsonChecks
        response["Boundaries"] = self.jsonBoundary
        response["Controls"] = self.jsonControls
        response["LegalDescription"] = self.jsonLegalDescription

        os.chdir(self.outpath)
        with open("jsonResponse.json", "w") as jsonfile:
            json.dump(response, jsonfile)

        self.appendReport("JSON Data String Output Written to Disk: jsonResponse.json\n")

        etime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport(f"\nScript Completed on {etime}\n\n")


        self.appendReport(f"\n{'END OF EXECUTION REPORT':^80s}\n")

        return response






    #========================= PART III: SECONDARY CLASS FUNCTIONS =========================#



    #---------- AMC Class Function: Append Report ----------#

    def appendReport(self, string):
        """AMC Class Function: Append Execution Report"""
        # Open the file for appending
        fa = open(self.report, "a+")
        # Append to the end of the file
        fa.write(f"{string}\n")
        # Close the file after appending
        fa.close()
        print(string)
        arcpy.AddMessage(string)
        return

    


    #---------- AMC Class Function: Arcpy Message ----------#

    def getAgpMsg(self, ntabs=1):
        """AMC Class Function: Arcpy Message"""
        tabs = "\t"*ntabs
        msg = tabs + arcpy.GetMessages().replace("\n", f"\n{tabs}") + "\n\n"
        return msg




    #---------- AMC Class Function: Check Project Geodatabase ----------#

    def checkGDB(self):
        """AMC Class Function: Check Project Geodatabase
        Checks if the reference geodatabase exists. If it does, it deletes it and creates a new one.
        """
        self.appendReport("Project Geodatabase")
        self.gdbname = os.path.split(self.gdbpath)[1]
        self.appendReport(f"\tChecking for geodatabase: {self.gdbname}")

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
        # List of all the default layer types
        LayerChecks = ["BASIS OF BEARING GPS TIES", "BOUNDARY", "CENTERLINES", "EASEMENTS", "LOT LINES", "NORTH ARROW MISCELLANEOUS", "RIGHT OF WAY"]

        # List of all the layer types in imported CAD drawing
        layers = []
        with arcpy.da.SearchCursor("Polyline", ["Layer"]) as cursor:
            for row in cursor:
                if row[0] not in layers:
                    layers.append(row[0])
                    layers.sort()

        # Perform the checks of the layers in the drawing against the defaults
        self.appendReport("Layer Checks")
        checks = []

        for i, lyr in enumerate(LayerChecks, start = 1):
            if lyr in layers:
                self.appendReport(f"\tCheck {i} of {len(LayerChecks)}: {lyr} in CAD Drawing: Passed")
                self.jsonChecks["LayerChecks"] = "Pass"
                checks.append(True)
            elif lyr not in layers:
                self.appendReport(f"\tCheck {i} of {len(LayerChecks)}: {lyr} not in CAD Drawing: Failed")
                self.jsonChecks["LayerChecks"] = "Fail"
                checks.append(False)

        if all(checks):
            self.appendReport("\tAll layers passed their checks.\n")
            # Create feature classes for each of the layers in the CAD drawing in the geodatabase
            gdblayers = []
            for lyr in LayerChecks:
                if lyr is not "NORTH ARROW MISCELLANEOUS":
                    outfc = lyr.title().replace(" ", "")
                    if arcpy.Exists(outfc):
                        arcpy.Delete_management(outfc)
                    arcpy.Select_analysis("Polyline", outfc, f"""Layer = '{lyr}'""")
                    gdblayers.append(outfc)
                    gdblayers.sort()
        else:
            self.appendReport("\tOne or more layers failed their checks, above. Please make sure all layers exist in the CAD drawing.\n")
            return

        return




    #---------- AMC Class Function: Check GPS Control Points ----------#

    def checkGPS(self):
        """AMC Class Function: Check GPS Control Points
        Checks and verifies the presence of the GPS Control Points in the CAD drawing
        """

        # List all of GPS points in CAD drawing and checks to make sure there are at least two of them present
        self.appendReport("GPS Control Point Check")
        self.gpspoints = []
        with arcpy.da.SearchCursor("Annotation", ["RefName", "SHAPE@XY"]) as cursor:
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
            arcpy.Select_analysis("Annotation", "GPSPoints", f"""RefName LIKE '%GPS%'""")
            self.appendReport(f"\tAdding points to geodatabase:\n {self.getAgpMsg(2)}")
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
            with arcpy.da.UpdateCursor("GPSPoints", ["OID@", "SHAPE@", "RefName"]) as cursor:
                for row in cursor:
                    oid = row[0]
                    gpsid = row[2].split("GPS NO. ")[1]

                    # Searching the geodetics control layer for the GPS point geometry
                    with arcpy.da.SearchCursor("geodetics_lyr", ["OID@", "SHAPE@", "GPS", "Easting2017", "Northing2017"]) as cursor1:
                        for row1 in cursor1:
                            if gpsid == row1[2]:
                                self.appendReport(f"\tGeodetic control point no. {gpsid} located in server database")
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
        tpobsource = "none"
        tpobx = tpoby = 0

        # True Point of Beginning
        self.appendReport("True Point of Beginning (TPOB) Check")

        # if TPOB coordinates are provided by user
        if self.tpob:
            tpobsource = "user"
            tpobx = self.tpob[0]
            tpoby = self.tpob[1]
            self.tpob = tpobx, tpoby
            self.appendReport("\tTPOB provided by User: Passed\n")
            self.jsonChecks["TPOB"] = "Pass"
        
        # if TPOB coordinates are not provided
        elif self.tpob is None:
            with arcpy.da.SearchCursor("Point", ["Layer", "SHAPE@XY"]) as cursor:
                for row in cursor:
                    if "TRUE POINT OF BEGINNING" in row[0]:
                        if arcpy.Exists("TPOB") == False:
                            arcpy.Select_analysis("Point", "TPOB", f"""Layer LIKE '%TRUE POINT OF BEGINNING%'""")
                            self.appendReport("\tTPOB layer exists in CAD drawing: Passed\n")

            # If TPOB is found
            if arcpy.Exists("TPOB"):
                ntpob = int(arcpy.GetCount_management("TPOB")[0])
                if ntpob == 1:
                    with arcpy.da.SearchCursor("TPOB", ["OID@", "SHAPE@"]) as cursor:
                        for row in cursor:
                            tpobsource = "cad"
                            tpobx, tpoby = row[1][0].X, row[1][0].Y
                            self.tpob = tpobx, tpoby
                elif ntpob > 1:
                    tpobs = []
                    with arcpy.da.SearchCursor("TPOB", ["OID@", "SHAPE@"]) as cursor:
                        for row in cursor:
                            tpobs.append((row[1][0].X, row[1][0].Y))

                    # If all the points have the same coordinates:
                    if len(tpobs) == tpobs.count(tpobs[0]):
                        msg = "WARNING: Multiple TPOB points detected in CAD Drawing. All points have the same coordinates. Using the first point in layer and ignoring the rest."
                    else:
                        msg = "WARNING: Multiple TPOB points detected in CAD Drawing. These points have different coodrinates, thus selecting the correct point is untainable. This program will use the first point in the list, but you may want to re-examine the TPOB data in the original CAD drawing."

                    self.appendReport(f"\t{msg}")
                    tpobsource = "cad"
                    tpobx, tpoby = tpobs[0][0], tpobs[0][1]
                    self.tpob = tpobx, tpoby

            self.jsonChecks["TPOB"] = "Pass"
            self.tpobstring = "TRUE POINT OF BEGINNING"

        # If TPOB is not found
        if tpobsource == "none":
            self.appendReport("\tTPOB is missing: Failed\n")

        # Populate the JSON Controls
        self.jsonControls["TPOB"]["source"] = tpobsource
        self.jsonControls["TPOB"]["x"] = tpobx
        self.jsonControls["TPOB"]["y"] = tpoby

        return




    #---------- AMC Class Function: Checking for expanded boundary layers ----------#

    def checkEBL(self):
        """AMC Class Function: Check for expanded boundary layers
        Checking for expanded boundary layers in CAD drawing and corrects geometry if necessary
        """

        # Checking for expanded boundary layer
        self.appendReport("Expanded Boundary Layer Check:")
        nr = int(arcpy.GetCount_management("Boundary")[0])

        # if a single row in boundary layer
        if nr == 1:
            self.appendReport("\tSingle boundary line detected: correcting...")
            arcpy.Rename_management("Boundary", "BoundarySingle")
            arcpy.SplitLine_management("BoundarySingle", "Boundary")
            arcpy.Delete_management("BoundarySingle")
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

    def checkClosureCentroid(self, poid=1):
        """AMC Class Function: Checks for closure
        Checks for closure: creating boundary polygon and returns it's centroid coordinates
        """

        if arcpy.Exists("BoundaryArea"):
            arcpy.Delete_management("BoundaryArea")

        arcpy.FeatureToPolygon_management("Boundary", "BoundaryArea")
        self.appendReport("Boundary Polygon/Centroid Closure Check:")

        # Adding fields
        newFields = ["CentroidX", "CentroidY", "AreaSqFeet", "AreaAcres"]
        for field in newFields:
            arcpy.AddField_management("BoundaryArea", field, "FLOAT")


        if int(arcpy.GetCount_management("BoundaryArea")[0]) > 0:
            self.jsonChecks["BoundaryClosure"][poid] = "Pass"
            areas = []
            # Getting the centroid coordinates for a given polygon
            self.appendReport("\tObtaining the centroid coordinates for each boundary polygon")
            with arcpy.da.UpdateCursor("BoundaryArea", ["OID@", "SHAPE@", "CentroidX", "CentroidY", "AreaSqFeet", "AreaAcres"]) as cursor:
                for row in cursor:
                    oid = row[0]
                    if oid == poid: # finds the parcel OID (user provided)
                        centroidx = row[2] = row[1].centroid.X
                        centroidy = row[3] = row[1].centroid.Y
                        self.centroid = centroidx, centroidy # returns the centroid coordinates of that parcel
                        areaSqFeet = row[4] = row[1].getArea("GEODESIC", "SQUAREFEET")
                        areaAcres = row[5] = row[1].getArea("GEODESIC", "ACRES")
                        areas = (areaSqFeet, areaAcres)
                    cursor.updateRow(row)
            self.jsonControls["Centroid"][poid] = self.centroid
            self.jsonControls["Areas"][poid] = {}
            self.jsonControls["Areas"][poid]["SquareFeet"] = areaSqFeet
            self.jsonControls["Areas"][poid]["Acres"] = areaAcres
            self.appendReport("\tBoundary area closure: Passed\n")


        else:
            self.centroid = None
            self.jsonChecks["BoundaryClosure"][poid] = "Fail"
            self.appendReport("\tBoundary area closure: Failed\n")

        return




    #---------- AMC Class Function: Checks for location ----------#

    def checkLocation(self):
        """AMC Class Function: Checks for location
        Checking county server geodatabase for location data on tract/parcel
        """
        
        self.appendReport("Map Server Location Checks")
        if self.ocserver:
            self.serverCities = os.path.join(self.ocserver, "OCSurvey.DBO.Boundaries\OCSurvey.DBO.CityBoundaries")
            self.appendReport("\tChecking City Boundaries Server Features: OCSurvey.DBO.CityBoundaries")

            # Create temporary Cities layer from server
            arcpy.MakeFeatureLayer_management(self.serverCities, "cities_lyr")
            self.appendReport("\tFiniding locations in server that intersect with CAD boundary layer (within 0.01 feet)")

            # Select cities polygons that intersect within 0.01 feet from the CAD Boundaries layer
            arcpy.SelectLayerByLocation_management("cities_lyr", "INTERSECT", "Boundary", "0.01 Feet", "NEW_SELECTION", "NOT_INVERT")
            # How many cities intersect
            citiesNo = int(arcpy.GetCount_management("cities_lyr")[0])

            # Loop the selected cities
            with arcpy.da.SearchCursor ("cities_lyr", "CITY") as cursor:
                citiesList = []
                for row in cursor:
                    citiesList.append(row[0])
            if len(citiesList) == 1:
                cities = citiesList[0]
                self.jsonChecks["Location"] = "Pass"
                self.appendReport(f"\tLocation found: {cities}")
            elif len(citiesList) > 1:
                cities = citiesList
                self.jsonChecks["Location"] = "Pass"
                self.appendReport(f"\tMultiple locations found: {cities}")
            else:
                self.jsonChecks["Location"] = "Fail"
                self.appendReport("\tNo locations found: Failed")

            if citiesNo == 1 and citiesList is not "UNINCORPORATED":
                cityString = f"CITY of {cities}"
                self.jsonControls["Location"]["Type"] = "City"
                self.appendReport("\tLocation type: City")
            elif citiesNo ==1 and citiesList is "UNINCORPORATED":
                cityString = f"UNINCORPORATED TERRITORY"
                self.jsonControls["Location"]["Type"] = "Unincorporated Territory"
                self.appendReport("\tLocation type: Unincorporated Territory")
            elif citiesNo > 1 and "UNINCORPORATED" not in citiesList:
                cityString = f"CITIES OF  {(' , ').join(tst[:-1])} AND {tst[-1]}"
                self.jsonControls["Location"]["type"] = "Cities"
                self.appendReport("\tLocation type: Cities (multiple)")
            elif citiesNo > 1 and "UNINCORPORATED" in citiesList:
                cityString = f"CITIES AND UNINCORPORATED TERRITORY OF  {(' , ').join(tst[:-1])} AND {tst[-1]}"
                self.jsonControls["Location"]["type"] = "Both"
                self.appendReport("\tLocation type: Both City and Unincorporated Territory")

            self.jsonControls["Location"]["Name"] = cityString.title().replace("Of", "of")
            if citiesNo >= 1:
                self.jsonControls["Location"]["County"] = "Orange"
                countyString = "County of Orange"
                self.appendReport(f"\tCounty: {countyString}")

            self.appendReport(f"\tFull Location Identified: {cityString.title()}, {countyString}, State of California")
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
                        self.appendReport(f"\tServer tract lot exists in server: {jsonTR}")
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
                            self.appendReport(f"\tMap book number: {bookNo}")
                            # if dash exists, split and replace dash with through, else do nothing. add inclussive at the end of string.
                            pp = row[3].split("/")[1]
                            if "-" in pp:
                                pagesNo = pp.replace("-", " through ") + " inclusive"
                            else:
                                pagesNo = row[3].split("/")[1]
                            self.appendReport(f"\tMap book pages: {pagesNo}")
                            engCo = row[4]
                            self.appendReport(f"\tEngineering Company: {engCo}")
                            engSvyName = row[5]
                            self.appendReport(f"\tSurveying Company Name: {engSvyName}")
                            engSvyNum = row[6]
                            self.appendReport(f"\tSurveying Company Number: {engSvyNum}")
                            self.jsonControls["Book"]["No"] = bookNo
                            self.jsonControls["Book"]["Pages"] = pagesNo
                            self.jsonControls["Registration"]["EngCo"] = engCo
                            self.jsonControls["Registration"]["EngSurveyorName"] = engSvyName
                            self.jsonControls["Registration"]["EngSurveyorNumber"] = engSvyNum
                            self.appendReport(f"\tInformation Match Found, Book No. {bookNo}, pages {pagesNo}: Passed\n")
            if self.jsonChecks["MapGeometry"] is not "Pass":
                self.appendReport("\tTract map information not found in server: Failed\n")

        else:
            self.appendReport("\tChecking Tract Maps Server Features Failed: Script outside OCPW Domain.")

        return




    #---------- AMC Class Function: Checks for Tract Information ----------#

    def checkServerParcelMaps(self):
        """AMC Class Function: Parcel Map Checking Information
        Checks for Parcel Information from Server Geodatabase
        """
        self.appendReport(f"Parcel Map Server Location Checks")

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




    #---------- AMC Class Function: Checks for Tract Information ----------#

    def checkServerRecordsOfSurvey(self):
        """AMC Class Function: Record of Survey Map Checking Information
        Checks for Record of Survey Information from Server Geodatabase
        """
        self.appendReport(f"Tract Map Server Location Checks")

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
        rtpob = tuple([self.truncate(t, self.tolerance) for t in self.tpob])

        # Loop through the Boundary multilines and get OIDs and initial coordinates:
        with arcpy.da.SearchCursor("Boundary", ["OID@", "SHAPE@"]) as cursor:
            for row in cursor:
                oid = row[0] # the multiline segment OID
                start = row[1].firstPoint.X, row[1].firstPoint.Y # the initial start coordinates
                end = row[1].lastPoint.X, row[1].lastPoint.Y # the initial end coordinates

                # Update the segments dictionary to hold the segment data for each OID
                segments[oid] = {}
                segments[oid]["oid"] = oid
                segments[oid]["start"] = start
                segments[oid]["end"] = end
                segments[oid]["reversed"] = False

                # Will check later in the coe if there are results populated
                coor = None

                # Rounding start and end coordinates
                rstart = tuple([self.truncate(s, self.tolerance) for s in start])
                rend = tuple([self.truncate(e, self.tolerance) for e in end])

                # Check to see if the true point of beginning is in one of these coordinates
                if rstart == rtpob:
                    coor = start, end
                    reversed = False
                elif rend == rtpob:
                    coor = end, start
                    reversed = True

                if coor is not None:
                    pair[f"{oid}"] = {}
                    pair[f"{oid}"]["coor"] = coor
                    pair[f"{oid}"]["reversed"] = reversed

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
        while len(self.course) < len(segments): # runs until the course includes all the line segment
            nextLine = self.nextCourseSegment(self.course, segments) # calls the getnext function above and obtains the data of the next line
            nextKey = [key for key in nextLine.keys()][0] # get the OID of the next line
            order = len(self.course) + 1 # update the orderID
            # Populate the next entry in the course JSON.
            self.course[order] = {}
            self.course[order]["oid"] = nextKey
            self.course[order]["start"] = nextLine[nextKey]["start"]
            self.course[order]["end"] = nextLine[nextKey]["end"]
            self.course[order]["reversed"] = nextLine[nextKey]["reversed"]

        # Finally, create an course order ID field (COID) in the boundary feature class and populate it with the values of the course
        arcpy.AddField_management("Boundary", "coid", "LONG", field_alias="Course Order ID")
        with arcpy.da.UpdateCursor("Boundary", ["OID@", "SHAPE@", "coid"]) as cursor:
            for row in cursor:
                oid = row[0]
                row[2] = [i for i in self.course if self.course[i]["oid"] == oid][0]
                cursor.updateRow(row)

        # Write out the course to the report
        for i in self.course:
            self.appendReport(f"\tCourse Order: {i}")
            self.appendReport(f"\t\tCourse OID: {self.course[i]['oid']}")
            self.appendReport(f"\t\tCourse start point: {self.course[i]['start']}")
            self.appendReport(f"\t\tCourse end point: {self.course[i]['end']}")
            self.appendReport(f"\t\tCourse reversal: {self.course[i]['reversed']}")

        # Check the size of the course
        if len(self.course) == len(segments):
            self.appendReport("\tTraverse Course Complete: Passed\n")
        else:
            self.appendReport("\tTraverse Course Incomplete: Failed\n")

        return




    #---------- AMC Class Function: Truncating Values ----------#

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
        Checks and corrects (if needed) the boundary course geometry given a course and a direction (clockwise or counter-clockwise). The function checks the start and endpoints and if need reversing it updates the feature classe's multiline geometry in the geodatabase.
        """
        self.appendReport("Boundary Multiline Geometry Correction Check")

        # Update loop of the features in the geodatabase
        with arcpy.da.UpdateCursor("Boundary", ["OID@", "SHAPE@"]) as cursor:
            for row in cursor:
                oid = row[0]
                wkt = row[1].WKT
                start = row[1].firstPoint.X, row[1].firstPoint.Y
                end = row[1].lastPoint.X, row[1].lastPoint.Y
                cid = [self.course[i] for i in self.course if self.course[i]["oid"] == oid][0]
                if cid["start"] == start and cid["end"] == end:
                    self.appendReport(f"\tOID {oid}: keeping original direction")
                    rwkt = wkt
                elif cid["start"] == end and cid["end"] == start:
                    self.appendReport(f"\tOID {oid}: reversing direction")
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
            pre = f"That portion of {kind} 1"
        elif nparcels > 1:
            temp = []
            for i in range(nparcels):
                if i+1 < nparcels:
                    temp.append(str(i+1))
                elif i+1 == nparcels:
                    temp.append(f"and {i+1}")
            temp2 = ", ".join(temp)

            pre = f"These portions of {kind} {temp2}"

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
        self.mapdesc = f"{pre} of {maptype} No. {mapid}, in the {locname}, County of {loccounty}, State of California, as per map filed in Book {bookNo}, pages {pagesNo} of {mapbooktype} in the Office of the County Recorder of said County, more particularly described as follows:"

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
                dbearing = f"North {self.dd2dms(radbearing_cs)} East"
            elif 90 < radbearing_cs <= 180:
                dbearing = f"South {self.dd2dms(180 - radbearing_cs)} East"
            elif 180 < radbearing_cs <= 270:
                dbearing = f"South {self.dd2dms(radbearing_cs - 180)} West"
            elif 270 < radbearing_cs <= 360:
                dbearing = f"North {self.dd2dms(360 - radbearing_cs)} West"

            if firstjson["radtangent"] == "Tangent":
                predesc = f", to the beginning of a curve, concave {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}"
                gpredesc = f", to the beginning of a curve, concave {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}"

            elif firstjson["radtangent"] == "Reverse":
                predesc = f", to the beginning of a reverse curve {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}"
                gpredesc = f", to the beginning of a reverse curve {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}"

            elif firstjson["radtangent"] == "Compound":
                predesc = f", to the beginning of a compound curve {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}"
                gpredesc = f", to the beginning of a compound curve {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}"

            else:
                predesc = f", to the beginning of a non-tangent curve, concave {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}"
                gpredesc = f", to the beginning of a non-tangent curve, concave {self.bearingLabel(midbearing)}, and having a radius of {self.truncate(radius/self.scalefactor, self.tolerance):.2f} feet, a radial bearing to said beginning of curve bears {dbearing}"

        else:
            predesc = ""
            gpredesc = ""
    
    
        self.preamp = f"COMMENCING at Orange County Horizontal Control Station \"{hc1id}\" having a State Plane Coordinate Value of Northing {hc1x} and Easting {hc1y}; Thence {self.labelBearingDistance(hc1bearing, hc1distance)} to Station \"{hc2id}\"; Thence {annotation2} to the TRUE POINT OF BEGINNING having a State Plane Coordinate Value of Northing {self.truncate(tpobx, self.tolerance):.2f} and Easting {self.truncate(tpoby, self.tolerance):.2f}{predesc}."
        self.gpreamp = f"COMMENCING at Orange County Horizontal Control Station \"{hc1id}\" having a State Plane Coordinate Value of Northing {ghc1x} and Easting {ghc1y}; Thence {self.labelBearingDistance(hc1bearing, ghc1distance)} to Station \"{hc2id}\"; Thence {gannotation2} to the TRUE POINT OF BEGINNING having a State Plane Coordinate Value of Northing {self.truncate(tpobx/self.scalefactor, self.tolerance):.2f} and Easting {self.truncate(tpoby/self.scalefactor, self.tolerance):.2f}{gpredesc}."
        
        return




    #---------- AMC Class Function: Format Labels for Bearing and Distance ----------#

    def labelBearingDistance(self, bearing, distance):
        """AMC Class Function: Format Labels for Bearing and Distance
        Generates a formatted bearing and distance string from coordinates
        """
        if 0 <= bearing <= 90:
            label = f"North {self.dd2dms(self.truncate(bearing, self.tolerance))} East, {self.truncate(distance, self.tolerance)} feet"
        elif 90 < bearing <= 180:
            label = f"South {self.dd2dms(self.truncate(180 - bearing, self.tolerance))} East, {self.truncate(distance, self.tolerance)} feet"
        elif 180 < bearing <= 270:
            label = f"South {self.dd2dms(self.truncate(bearing - 180, self.tolerance))} West, {self.truncate(distance, self.tolerance)} feet"
        elif 270 < bearing <= 360:
            label = f"North {self.dd2dms(self.truncate(360 - bearing, self.tolerance))}, West, {self.truncate(distance, self.tolerance)} feet"

        return label



