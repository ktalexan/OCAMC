# OCAMC <a name="title"></a>
### OC Automated Map Checking Python Development <a name="subtitle"></a>

# 

<br>

### Contents <a name="contents"></a>

>- **[AMC Class Documentation](#documentation)**
>   - [Class Contents](#classcontents)
>- **[Classes and Execution Code in Folders](#classes)**
>   - [Python Classes and Functions](#pyclasses)
>   - [Execution Code](#pyexecution)
>- **[Folders and Python Classes](#folders)**


<br><br>

## AMC Class Documentation <a name="documentation"></a>

### Class Contents <a name="classcontents"></a>

**[PART I: AMC CLASS AND INSTANTIATION](#p1)**

0. [AMC Class](#class)
1. [Class Instantiation (*init*)](#def01)

**[PART II: MAIN CLASS FUNCTIONS](#p2)**

2. [Base Checks (*baseChecks*)](#def02)
3. [Boundary Processing (*boundaryProcessing*)](#def03)
4. [Create Legal Description (*createLaegalDescription*)](#def04)
5. [Finalize Report (*finalizeReport*)](#def05)

**[PART III: SECONDARY CLASS FUNCTIONS](#p3)**

6. [Append Report (*appendReport*)](#def06)
7. [ArcPy Message (*getAgpMsg*)](#def07)
8. [Check Project Geodatabase (*checkGDB*)](#def08)
9. [Check Layers in CAD (*checkLayers*)](#def09)
10. [Create Feature Classes (*createFeatureClasses*)](#def10)
11. [Check GPS Control Points (*checkGPS*)](#def11)
12. [Check Geodetic Control Geometries (*checkGeodeticControls*)](#def12)
13. [Check for POB (*checkPOB*)](#def13)
14. [Check for Expanded Boundary Layers (*checkEBL*)](#def14)
15. [Check for Closure (*checkClosureCentroid*)](#def15)
16. [Check for Location (*checkLocation*)](#def16)
17. [Check for Tract Information (*checkServerTractMaps*)](#def17)
18. [Check for Parcel Information (*checkServerParcelMaps*)](#def18)
19. [Check for Records of Survey Information (*checkServerRecordsOfSurvey*)](#def19)
20. [Truncating Values (*truncate*)](#def20)
21. [Boundary Course Traverse Path (*traverseCourse*)](#def21)
22. [Obtain Next Course Segment (*nextCourseSegment*)](#def22)
23. [Correct Boundary Geometry (*correctBoundaryGeometry*)](#def23)
24. [Decimal Degrees to Degrees-Minutes-Seconds (*dd2dms*)](#def24)
25. [Bearing to Word (*bearingLabel*)](#def25)
26. [Map Document Description (*describeMapDocument*)](#def26)
27. [Describe Horizontal Controls (*describeHorizontalControls*)](#def27)
28. [Format Labels for Bearing and Distance (*labelBearingDistance*)](#def28)
29. [Generate CSV Boundary Table (*boundaryToTable*)](#def29)

<br><br>

### PART I: AMC CLASS AND INSTANTIATION <a name="p1"></a>

#### AMC CLASS <a name="class"></a>

>```python
>amc(object)
>```
>* This class contains a number of functions, methods, and processes for Automated Map Checking analysis using CAD drawings
>* INPUT/OUTPUT: 
>    * See class instantiation below.

<br>

#### Class Instantiation <a name="def01"></a>

>```python
>__init__(self, cadpath, prjpath, outpath, cadname, scale, scalefactor, tpob=None, direction=None, tolerance=2)
>```
>* Function class initialization (AMC) that returns an amc class object for further processing.
>* INPUT:
>    * *cadpath*: the file path to the CAD drawing (.dwg).
>    * *prjpath*: the file path to the project directory (that contains the class python code).
>    * *outpath*: the file path to the directory where the execution output and results will be stored.
>    * *cadname*: the name of the CAD drawing (without the file extension).
>    * *scale*: the scale used for the drawing. It can be 'grid' or 'ground'.
>    * *scalefactor*: the single scale conversion factor (from ground to grid and vice versa).
>    * *tpob (default=None)*: optional user input that overrides the TPOB point layer in the CAD drawing, or if it does not exist in the CAD drawing. 
>    * *direction (default=None)*: optional user input defining the direction (clockwise or counter-clockwise) for the boundary course path. When default, the program uses clockwise direction.
>    * *tolerance (default=2)*: optional decimal accuracy to check geometry coordinates and against County database. When default, then the accuracy is 1/100th of a foot.
>* OUTPUT:
>    * *client*: an amc class object.
>* NOTES:
>    * This function runs on instantiation of a class automatically.

<br><br>

### PART II: MAIN CLASS FUNCTIONS <a name="p2"></a>

#### Base Checks <a name="def02"></a>

>```python
>baseChecks(self)
>```
>* Imports the CAD drawing and performs basic layer and geometry checks.
>* Calls the following functions:
>    * *checkGDB()*
>    * *checkLayers()*
>    * *createFeatureClasses()*
>    * *checkGPS()*
>    * *checkGeodeticControls()*
>    * *checkPOB()*
>    * *checkEBL()*
>    * *checkLocation()*
>    * *checkServerTractMaps()* or *checkServerParcelMaps()* or *checkServerRecordsOfSurvey()*
>    * *traverseCourse()*
>    * *correctBoundaryGeometry()*

<br>

#### Boundary Processing <a name="def03"></a>

>```python
>boundaryProcessing(self)
>```
>* This function processes the boundaries of the CAD drawing and performs basic checks. It also processes the boundary multiline features, creates fields in the geodatabase's feature class, mathematically computes bearing, distances, radial angles, etc, for annotation labels and legal descriptions.

<br>

#### Create Legal Description <a name="def04"></a>

>```python
>createLegalDescription(self)
>```
>* This function generates a legal description document after boundary processing data.

<br>

#### Finalize Report <a name="def05"></a>

>```python
>finalizeReport(self)
>```
>* This function compiles and exports all data and reports, and finishes up the execution.
    
<br><br>

### PART III: SECONDARY CLASS FUNCTIONS <a name="p3"></a>

#### Append Report <a name="def06"></a>

>```python
>appendReport(self, string)
>```
>* Appends the execution report (opened by class instantiation process)
>* INPUT:
>    * *string*: the string text to be appended in the report.

<br>

#### Arcpy Message <a name="def07"></a>

>```python
>getAgpMsg(self, ntabs=1)
>```
>* Obtains and returns the message(s) generated by the execution of arcpy functions.
>* *ntabs*: how many tabs to insert at the beginning of the message (to be used in the execution report)

<br>

#### Check Project Geodatabase <a name="def08"></a>

>```python
>checkGDB(self)
>```
>* Checks if the reference geodatabase exists. If it does, it deletes it and creates a new one.

<br>

#### Check Layers in CAD <a name="def09"></a>

>```python
>checkLayers(self)
>```
>* Checks for the presence of all the layers in CAD drawing. Records Pass/Fail in JSON Checks.
>* Checking for layers:
>    * *V-ANNO*: Annotation layer to be used for all Text, Mtest, Leaders, Multileaders and Dimensions (continuous line type)
>    * *V-LINE*: Miscellaneous lines layer to be used for any lines do not fit in the template layer format (continous line type)
>    * *V-LINE-CALC*: Line Calc. Layer to be used for any line work shown for graphical purposes only (continous line type)
>    * *V-LINE-CNTR*: Street established centerline layer (CENTER2 line type)
>    * *V-LINE-ESMT*: Easement layer (DASHED2 line type)
>    * *V-LINE-LOTS*: Property line layer to be used for the established property in question line work (continuous line type)
>    * *V-LINE-PCLS*: GIS parcel lines and parcel annotation layer (DASHED line type)
>    * *V-LINE-PIQ-PARCEL*: PIQ parcel lines layer to be used only for the created parcels which represent the established property in question line work (continous line type)
>    * *V-LINE-REF*: Line reference layer to be used for the referenced lines (HIDDEN2 line type)
>    * *V-LINE-ROW-PARCEL*: ROW parcel lines layer to be used only for the created parcels which represent the established right-of-way line work (continuous line type)
>    * *V-LINE-RTWY*: Street ROW layer to be used only for the right-of-way line work (continuous line type)
>    * *V-LINE-TIE*: Ties to basis of bearing layer (DASHED2 line type)
>    * *V-MISC*: North arrow layer (continuous line type)
>    * *V-NODE-MON*: Monuments layer (continuous line type)
>    * *V-NODE-TABL*: Table data layer for points (continous line type)
>    * *V-NODE-TPOB*: True point of beginning layer to be used only for the point of beginning which was used to create the parcel of the property (continuous line type)
>    * *V-SHEET*: Sheet details layer to be used for the line and curve tables (continuous line type)
>    * *V-TBLE-LINE*:Table annotation layer to be used for the line and curve tables (continuous line type)
>    * *V-VPORT Freezes 1*: V-VPORT freezes 1 layer to be used to control viewport freeze (continuous line type)
>    * *V-VPORT Freezes 2*: V-VPORT freezes 2 layer to be used to control viewport freeze (DASHED2 line type)

<br>

#### Create Feature Classes <a name="def10"></a>

>```python
>createFeatureClasses(self)
>```
>* Creates feature classes from original CAD drawing layers. Uses specific and verified layers from the imported CAD drawing features to generate feature classes in the geodatabase.

<br>

#### Check GPS Control Points <a name="def11"></a>

>```python
>checkGPS(self)
>```
>* Checks and verifies the presence of the GPS control points in the CAD drawing

<br>

#### Check Geodetic Control Point Geometries <a name="def12"></a>

>```python
>checkGeodeticControls(self)
>```
>* Checks for geodetic control point geometries in server geodatabase.

<br>

#### Check for POB <a name="def13"></a>

>```python
>checkPOB(self)
>```
>* Checks for the presence of the (True) point of beginning, either by the user, or in the CAD drawing. 

<br>

#### Check for Expanded Boundary Layers <a name="def14"></a>

>```python 
>checkEBL(self)
>```
>* CHecking for expanded boundary layers in CAD drawing and corrects geometry if necessary.

<br>

#### Check for Closure <a name="def15"></a>

>```python
>checkClosureCentroid(self)
>```
>* Checks for closure: creating boundary polygon and returns it's centroid coordinates.

<br>

#### Check for Location <a name="def16"></a>

>```python
>checkLocation(self)
>```
> * Checking County server geodatabase for location data on tract/parcel.

<br>

#### Check for Tract Information <a name="def17"></a>

>```python
>checkServerTractMaps(self)
>```
> * Checks for Tract information from server geodatabase.

<br>

#### Check for Parcel Information <a name="def18"></a>

>```python
>checkServerParcelMaps(self)
>```
>* Checks for Parcel information from server geodatabase.

<br>

#### Check for Records of Survey Information <a name="def19"></a>

>```python
>checkServerRecordsOfSurvey(self)
>```
>* CHecks for Record of Survey information from server geodatabase.

<br>

#### Truncating Values <a name="def20"></a>

>```python
>truncate(self, v, n)
>```
>* Trybcates coordinates a the n-th decimal places, for the value v(double).

<br>

#### Boundary Course Traverse Path <a name="def21"></a>

>```python
>traverseCourse(self)
>```
>* Obtains the course and order for the boundary traverse path over multilines (PIQ).

<br>

#### Obtain Next Course Segment <a name="def22"></a>

>```python
>nextCourseSegment(self, course, segments)
>```
>* Gets the next course coordinate based on the initial line (*course[1]*), and the line segment coordinates from ArcGIS Boundary feature class (PIQ). Returns a JSON string indexed by the order ID (the order to which the lines are added to the course), and for each item, the Boundary feature class OBJECTID, its true start and end coordinates (reversed from the feature class line direction if needed - always clockwise).

<br>

#### Correct Boundary Geometry <a name="def23"></a>

>```python
>correctBoundaryGeometry(self)
>```
>* Checks and corrects (if needed) the boundary course geometry given a course and a direction (clockwise or counter-clockwise). The function checks the start and end endpoints and if need reversing it updating the featur class's multiline geometry in the geodatabase.

<br>

#### Decimal Degrees to Degrees-Minutes-Seconds <a name="def24"></a>

>```python
>dd2dms(self, dd)
>```
>* Returns formatted coordinates of the Degrees:Minutes:Seconds format. This secondary function restructures decimal degree coordinates into degree/minutes/seconds coordinats. It is called from the main module function.

<br>

#### Bearing to Word <a name="def25"></a>

>```python
>bearingLabel(self, bearing)
>```
> * Returns the corresponding direction word based on radial bearing values

<br>

#### Map Document Description <a name="def26"></a>

>```python
>describeMapDocument(self)
>```
> * Generates a description of the map document

<br>

#### Describe Horizontal Controls <a name="def27"></a>

>```python
>describeHorizontal Controls(self)
>```
> * Obtains and generates the Preamp description from horizontal geodetic controls to the point of beginning.

<br>

#### Format Labels for Bearing and Distance <a name="def28"></a>

>```python
>labelBearingDistance(self, bearing, distance)
>```
> * Generates a formatted bearing and distance string from coordinates

<br>

#### Generate CSV Boundary Table <a name="def29"></a>

>```python
>boundaryToTable(self)
>```
> * Creates a csv-formatted boundary table containing the course data

<br><br>

## Classes and Execution Code in Folders <a name="classes"></a>

### Python Classes and Functions <a name="pyclasses"></a>

* [AMC Class](amc/amc.py)
* [ALD Code](amc/ald.py)

#### Execution Code <a name="pyexecution"></a>

* [AMC and ALD Combined Execution on native Python Scirpt](amc/pyamcld.py)
* [CAD to AMC ArcGIS Pro Geoprocessing Tool Script](amc/gpamc.py)
* [JSON to Legal Description ArcGIS Pro Geoprocessing Tool Script](amc/gpald.py)
* [Automated Map Checking ArcGIS Toolbox](amc/Automated%20Map%20Checking.tbx)

<br><br>

## Folders and Python Classes <a name="folders"></a>

- [x] **[AMC python class, version 1.4](amc)**
  - [x] [Test Python Code Folder](amc/Test): Contains test python code for the AMC (v1.4) class (single boundary).
    - [x] [Test/Input Folder](amc/Test/input): Data input testing folder.
      - [x] [TR18141_REVISION2_MASTER.dwg](amc/Test/input/TR18141_REVISION2_MASTER.dwg): CAD drawing (single boundary) for testing AMC (v1.4) class.
    - [x] [Test/Output Folder](amc/Test/output): Data output testing folder.
      - [x] [TR18141 Folder](amc/Test/output/TR18141): Folder containing execution results of *amc* code.
        - [x] [Reference.gdb](amc/Test/output/TR18141/Reference.gdb): ArcGIS geodatabase containing the execution results feature datasets and classes.
        - [x] [BoundaryData.xlsx](amc/Test/output/TR18141/BoundaryData.xlsx): Excel spreadsheet containing results of the boundary course order multilines.
        - [x] [ExecutionReport.txt](amc/Test/output/TR18141/ExecutionReport.txt): Text output report of the code execution.
        - [x] [jsonResponse.json](amc/Test/output/TR18141/jsonResponse.json): JSON file containing the execution data of the AMC class.
        - [x] [Reference.docx](amc/Test/output/TR18141/Reference.docx): Legal description document automatically created by the execution of the *ald* class.
        - [x] [SPOCDSQL1205.sde](amc/Test/output/TR18141/SPOCDSQL1205.sde): Orange County ArcGIS server geodatabase connection containing reference databases (parcel fabric, horizontal control points, tract/survey/parcel maps, etc). Created automatically by the code execution (if in domain).
- [x] **[AMC python class, version 1.5](amc15)**
  - [x] [Test Python Code Folder](amc15/Test): Contains test python code for the AMC (v1.5) class (single and multiple boundaries).
    - [x] [Test/Input Folder](amc15/Test/Input): Data input testing folder.
    - [x] [Test/Output Folder](amc15/Test/Output): Data output testing folder.

