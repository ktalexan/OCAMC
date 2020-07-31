# OC Survey
# Automated Map Checking Tool Development

This is a python package containing tools for Orange County's OC Survey ***Automated Map Checking*** processes and analytical framework.

## Index of Classes and Functions



## Class: amc
AMC main class. This class contains a number of functions, methods and processes for _Automated Map Checking_ analysis using CAD drawings.

* __Inputs:__ See function class initalization below.
* __Outputs:__
  * _Reference.gdb:_ geodatabase conatining all the separate, checked, and corrected layers of the CAD drawing's geometry. These include boundaries (with correct directional geometries); geodetic horizontal control points (checked and verified with corrected geometry if needed); lot lines, centerlines, geodetic ties, etc.
  * _jsonResponse.json:_ a JSON-formatted string, containing four sessions:
    1. _jsonResponse['Checks']:_ containing the results of the validation/verification tests performed during execution of script with Pass/Fail (Layer Checks, Boundary Checks and Corrections, Boundary Line Checks, Boundary Closure Checks, Geometry Correction Checks, Geodetic Control Point Checks, TPOB Check, Location Check, Map Geometry Check).
    2. _jsonResponse['Boundaries']:_ containing the key geometric, mathematical, and descriptive attributes for each of the lines in the boundary course. These include start, mid, and end points, chords and chordal attributes, radial centers (for arcs), bearing and distances (for lines and arcs), curves, and the description to be used in the legal description document.
    3. _jsonResponse['Controls']:_ containing key map attributes for the CAD drawing. These include the map calculated location, city, county, state, the verified geodetic GPS control points, the TPOB coordinates, the boundary areas, and the parcels/lots.
    4. _jsonResponse['LegalDescription']:_ containing the three-part strings of the legal description document: the map description, the preamp (from commencement point to the point of beginning of the traverse course), and the main traverse course (from point of beginning or TPOB and back to start).
  * _Reference.docx:_ a correctly formatted legal description document corresponding to the validated and checked geometry of the CAD drawing. The legal description provided in this document passes the checks performed during the execution of the script.


### Function Class Initialization (\_\_\_init\_\_\_): 
Returns an amc class object for further execution.

* __Inputs:__
  * _cadpath_: the path to the CAD drawing file (.dwg).
  * _prjpath_: the path to the project directory containing the executable scripts and supporting files.
  * _outpath_: the path to the output directory where the results will be stored. 
  * _cadname_: the name of the CAD drawing (without the file extension). This input is used to generate an output folder.
  * _scale_: the scale used for the drawing. It can take two values: 'grid' or 'ground'.
  * _scalefactor_: the single scale conversion factor (from ground to grid coordinates and vice versa).
  * _tpob_ (optional): user input that overrides the TPOB point layer in the CAD drawing, or if it does not exist in the drawing (default = None).
  * _direction_ (optional): user input defining the direction ('clockwise' or 'counter-clockwise') for the boundary course traverse path (default = None).
  * _tolerance_ (optional): the decimal accuracy to be used for checking geometry coordinates, and against checks in Orange County's geodatabases (default = 2). When default, then the accuracy is 1/100th of a foot.
* __Outputs:__
  * _client_: an amc class object instantiation.
* __Notes:__ this function runs on the instatiation of the class.



Function|Description
:---|:---
amc.baseChecks()|Main AMC class function (1 of 4). Imports CAD drawing data and performs basic layer and geometry checks.
amc.boundaryProcessing()|Main AMC class function (2 of 4). This function processes the boundaries layer of the CAD drawing and performs basic additional checks. It also processes the boundary multiline features, creates fields in the geodatabase's feature class, mathematically computes bearings, distances, radial angles, etc., for annotation labels and legal descriptions.
amc.createLegalDescription()|Main AMC class function (3 of 4). This function generates a set legal description descriptions and labels after boundary processing data.
amc.finalizeReport()|Main AMC class function (4 of 4). This function compiles and exports all data and reports by completing the execution stage.
amc.appendReport(string)|Secondary AMC class function. It appends strings to the main execution report, outputs console messages, and routes them when necessary to the ArcGIS execution window.
amc.getAgpMsg(ntabs=1)|Secondary AMC class function. It obtains and routes ArcGIS Pro (arcpy)-generated messages to the main python process flow.
amc.checkGDB()|Secondary AMC class function. This function checks if the reference geodatabase to host the results already exists. If it does, it deletes the geodatabase, and generates a new one in its place.
amc.checkLayers()|Secondary AMC class function. This function checks for the presence of all the layers (by protocol) in the CAD drawing. It also records "Pass"/"Fail" output in JSON checks dictionary.
amc.checkGPS()|Secondary AMC class function. This function checks and verifies the presence of the GPS control points in the CAD drawing. It also writes Pass/Fail output in the JSON checks dictionary.
amc.checkGeodeticControls()|Secondary AMC class function. This function performs checks for geodetic control point geometries in the OC server geodatabase containing all the County's geodetic control points and monuments.
amc.checkPOB()|Secondary AMC class function. The function performs checks for the presence of the (True) Point of Beginning either in the CAD drawing, or user-provided one. It ensures that the TPOB is within a tolerance from one of the start or end points of the boundary layer.
amc.checkEBL()|Secondary AMC class function. The function is performing checks for expanded (exploded) boundary layers in the CAD drawing. If necessary, it corrects the geometry and re-joins the multi-lines.
amc.checkClosureCentroid(poid=1)|Secondary AMC class function. This function performs closure checks, by creating boundary polygon feature classes and returnin the centroid coordinates.
amc.checkLocation()|Secondary AMC class function. This function performs checks against the Orange COunty's server geodatabase for location data on tract/parcel/records of survey (DBO_CityBoundaries).
amc.checkServerTractMaps()|Secondary AMC class function. This function performs checks for _tract_ information from the OC server geodatabase (DBO.TRACT_MAPS).
amc.checkServerParcelMaps()|Secondary AMC class function. This function performs checks for _parcel_ information from the OC server geodatabase (DBO.PARCEL_MAPS_).
amc.checkServerRecordOfSurvey()|Secondary AMC class function. This function performs checks for _record of survey_ information from the OC server geodatabase (DBO.RECORD_OF_SURVEY_MAPS).
amc.truncate(v,n)|Secondary AMC class function. It truncates coordinates ath the n-th decimal place, for any input value (double). Differs from rounding values, as it does not round-up or down.
amc.traverseCource()|Secondary AMC class function. It computes and obtains the course for the boundary traverse path to be used in the legal description.
amc.nextCourseSegment(course, segments)|Secondary AMC class function. The function obtains the next course coordinate based on the initial line (course[1]), and the line segment coordinates from the ArcGIS boundary feature class. It returns a JSON string indexed by the course order ID (the order to which the lines are added to the course sequentially), and for each item, the boundary feature class OBJECTID, its true start and end coordinates (reversed from the feature class line direction if needed - always clockwise).
amc.correctBoundaryGeometry()|Secondary AMC class function. This function performs checks and corrects (if needed) the boundary course traverse geometry given such a course and a traverse direction (clockwise or counter-clockwise). The function checks also the start and end points in case that they need reversing, and it updates the feature class's multiline geometry in the results geodatabase.
amc.dd2dms(dd)|Secondary AMC class function. The function returns formatted coordinates of the _Degrees:Minutes:Seconds_ format. This secondary function restructures decimal degree coordinates. It is called from multiple functions.
amc.bearingLabel(bearing)|Secondary AMC class function. It returns the corresponding direction word (of the cardinal direction), based on radial bearing values. E.g., if direction between 0&deg; and 22.5&deg; the result will be 'northerly'.
amc.describeMapDocument()|Secondary AMC class function. This function generates a description of the map document to be used in the initial section of the legal description.
amc.describeHorizontalControls()|Secondary AMC class function. This function obtains and generates the preamble section description from the horizontal geodetic controls to the point of beginning.
amc.labelBearingDistance(bearing, distance)|Secondary AMC class function. It generates a formatted bearing and distance string from coordinates and values to be used in the legal description generation.


The



