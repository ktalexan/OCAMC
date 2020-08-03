<h1 style="text-align:center; color:brown; background-color: Linen">OC Automated Map Checking</h1>
<p style="font-weight:bold; text-align:center; color:brown">OC Automated Map Checking Python Development</p>

<br>

>### Contents {#contents}
>- **[AMC Class Documentation](#documentation)**
>   - [Class Contents](#classcontents)
>- **[Classes and Execution Code in Folders](#classes)**
>   - [Python Classes and Functions](#pyclasses)
>   - [Execution Code](#pyexecution)
>- **[Folders and Python Classes](#folders)**


<br><br>

## AMC Class Documentation {#documentation, style="color: brown;"}

### Class Contents {#classcontents, style="color: darkgreen"}

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

### PART I: AMC CLASS AND INSTANTIATION {#p1, style="color: darkgreen"}

#### AMC CLASS {#class, style="color: purple"}

>```python
>amc(object)
>```
>* This class contains a number of functions, methods, and processes for Automated Map Checking analysis using CAD drawings
>* INPUT/OUTPUT: 
>    * See class instantiation below.

<br>

#### Class Instantiation {#def01, style="color: purple"}

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

### PART II: MAIN CLASS FUNCTIONS {#p2, style="color: darkgreen"}

#### Base Checks {#def02, style="color: purple"}

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

#### Boundary Processing {#def03, style="color: purple"}

>```python
>boundaryProcessing(self)
>```
>* This function processes the boundaries of the CAD drawing and performs basic checks. It also processes the boundary multiline features, creates fields in the geodatabase's feature class, mathematically computes bearing, distances, radial angles, etc, for annotation labels and legal descriptions.

<br>

#### Create Legal Description {#def04, style="color: purple"}

>```python
>createLegalDescription(self)
>```
>* This function generates a legal description document after boundary processing data.

<br>

#### Finalize Report {#def05, style="color: purple"}

>```python
>finalizeReport(self)
>```
>* This function compiles and exports all data and reports, and finishes up the execution.
    
<br><br>

### PART III: SECONDARY CLASS FUNCTIONS {#p3, style="color: darkgreen"}

#### Append Report {#def06, style="color: purple"}

>```python
>appendReport(self, string)
>```
>* Appends the execution report (opened by class instantiation process)
>* INPUT:
>    * *string*: the string text to be appended in the report.

<br>

#### Arcpy Message {#def07, style="color: purple"}

>```python
>getAgpMsg(self, ntabs=1)
>```
>* Obtains and returns the message(s) generated by the execution of arcpy functions.
>* *ntabs*: how many tabs to insert at the beginning of the message (to be used in the execution report)

<br>

#### Check Project Geodatabase {#def08, style="color: purple"}

>```python
>checkGDB(self)
>```
>* Checks if the reference geodatabase exists. If it does, it deletes it and creates a new one.

<br>

#### Check Layers in CAD {#def09, style="color: purple"}

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

#### Create Feature Classes {#def10, style="color: purple"}

>```python
>createFeatureClasses(self)
>```
>* Creates feature classes from original CAD drawing layers. Uses specific and verified layers from the imported CAD drawing features to generate feature classes in the geodatabase.

<br>

#### Check GPS Control Points {#def11, style="color: purple"}

>```python
>checkGPS(self)
>```
>* Checks and verifies the presence of the GPS control points in the CAD drawing

<br>

#### Check Geodetic Control Point Geometries {#def12, style="color: purple"}

>```python
>checkGeodeticControls(self)
>```
>* Checks for geodetic control point geometries in server geodatabase.

<br>

#### Check for POB {#def13, style="color: purple"}

>```python
>checkPOB(self)
>```
>* Checks for the presence of the (True) point of beginning, either by the user, or in the CAD drawing. 

<br>

#### Check for Expanded Boundary Layers {#def14, style="color: purple"}

>```python 
>checkEBL(self)
>```
>* CHecking for expanded boundary layers in CAD drawing and corrects geometry if necessary.

<br>

#### Check for Closure {#def15, style="color: purple"}

>```python
>checkClosureCentroid(self)
>```
>* Checks for closure: creating boundary polygon and returns it's centroid coordinates.

<br>

#### Check for Location {#def16, style="color: purple"}

>```python
>checkLocation(self)
>```
> * Checking County server geodatabase for location data on tract/parcel.

<br>

#### Check for Tract Information {#def17, style="color: purple"}

>```python
>checkServerTractMaps(self)
>```
> * Checks for Tract information from server geodatabase.

<br>

#### Check for Parcel Information {#def18, style="color: purple"}

>```python
>checkServerParcelMaps(self)
>```
>* Checks for Parcel information from server geodatabase.

<br>

#### Check for Records of Survey Information {#def19, style="color: purple"}

>```python
>checkServerRecordsOfSurvey(self)
>```
>* CHecks for Record of Survey information from server geodatabase.

<br>

#### Truncating Values {#def20, style="color: purple"}

>```python
>truncate(self, v, n)
>```
>* Trybcates coordinates a the n-th decimal places, for the value v(double).

<br>

#### Boundary Course Traverse Path {#def21, style="color: purple"}

>```python
>traverseCourse(self)
>```
>* Obtains the course and order for the boundary traverse path over multilines (PIQ).

<br>

#### Obtain Next Course Segment {#def22, style="color: purple"}

>```python
>nextCourseSegment(self, course, segments)
>```
>* Gets the next course coordinate based on the initial line (*course[1]*), and the line segment coordinates from ArcGIS Boundary feature class (PIQ). Returns a JSON string indexed by the order ID (the order to which the lines are added to the course), and for each item, the Boundary feature class OBJECTID, its true start and end coordinates (reversed from the feature class line direction if needed - always clockwise).

<br>

#### Correct Boundary Geometry {#def23, style="color: purple"}

>```python
>correctBoundaryGeometry(self)
>```
>* Checks and corrects (if needed) the boundary course geometry given a course and a direction (clockwise or counter-clockwise). The function checks the start and end endpoints and if need reversing it updating the featur class's multiline geometry in the geodatabase.

<br>

#### Decimal Degrees to Degrees-Minutes-Seconds {#def24, style="color: purple"}

>```python
>dd2dms(self, dd)
>```
>* Returns formatted coordinates of the Degrees:Minutes:Seconds format. This secondary function restructures decimal degree coordinates into degree/minutes/seconds coordinats. It is called from the main module function.

<br>

#### Bearing to Word {#def25, style="color: purple"}

>```python
>bearingLabel(self, bearing)
>```
> * Returns the corresponding direction word based on radial bearing values

<br>

#### Map Document Description {#def26, style="color: purple"}

>```python
>describeMapDocument(self)
>```
> * Generates a description of the map document

<br>

#### Describe Horizontal Controls {#def27, style="color: purple"}

>```python
>describeHorizontal Controls(self)
>```
> * Obtains and generates the Preamp description from horizontal geodetic controls to the point of beginning.

<br>

#### Format Labels for Bearing and Distance {#def28, style="color: purple"}

>```python
>labelBearingDistance(self, bearing, distance)
>```
> * Generates a formatted bearing and distance string from coordinates

<br>

#### Generate CSV Boundary Table {#def29, style="color: purple"}

>```python
>boundaryToTable(self)
>```
> * Creates a csv-formatted boundary table containing the course data

<br><br>

## Classes and Execution Code in Folders {#classes, style="color: brown"}

### Python Classes and Functions {#pyclasses, style="color: darkgreen"}

* [AMC Class](amc/amc.py)
* [ALD Code](amc/ald.py)

#### Execution Code {#pyexecution, style="color: purple"}

* [AMC and ALD Combined Execution on native Python Scirpt](amc/pyamcld.py)
* [CAD to AMC ArcGIS Pro Geoprocessing Tool Script](amc/gpamc.py)
* [JSON to Legal Description ArcGIS Pro Geoprocessing Tool Script](amc/gpald.py)
* [Automated Map Checking ArcGIS Toolbox](amc/Automated%20Map%20Checking.tbx)

<br><br>

## Folders and Python Classes {#folders, style="color: brown"}

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

