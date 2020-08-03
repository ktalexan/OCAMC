# OC Automated Map Checking (OCAMC)<br>Python Programming and Development


<br>

## AMC Versions

Name|Version|Date|Status|Notes
---|---|---|---|---
amc13|[1.3](/amc13)|2019|Stable|Pre-development version - basic functionality
amc14|[1.4](/amc14)|2019|Stable|Basic version - operates on single boundary parcels
amc15|[1.5](/amc15)|2020|Development|Adds additional parcel/map processing capabilities for multiple case studies
amc16|[1.6](/amc16)|2020|Development|Revised cumulative processing capabilities for multiple case studies


<br>

## Contents

>- **[AMC Class Documentation](#amc-class-documentation)**
>   - [Class Contents](#class-contents)
>- **[Classes and Execution Code in Folders](#classes-and-execution-code-in-folders)**
>   - [Python Classes and Functions](#python-classes-and-functions)
>   - [Execution Code](#execution-code)
>- **[Folders and Python Classes](#folders-and-python-classes)**


<br><br>

## AMC Class Documentation

### Class Contents

**[PART I: AMC CLASS AND INSTANTIATION](#part-i-amc-class-and-instantiation)**

0. [AMC Class](#amc-class)
1. [Class Instantiation (*init*)](#class-instantiation)

**[PART II: MAIN CLASS FUNCTIONS](#part-ii-main-class-functions)**

2. [Base Checks (*baseChecks*)](#base-checks)
3. [Boundary Processing (*boundaryProcessing*)](#boundary-processing)
4. [Create Legal Description (*createLaegalDescription*)](#create-legal-description)
5. [Finalize Report (*finalizeReport*)](#finalize-report)

**[PART III: SECONDARY CLASS FUNCTIONS](#part-iii-secondary-class-functions)**

6. [Append Report (*appendReport*)](#append-report)
7. [ArcPy Message (*getAgpMsg*)](#arcpy-message)
8. [Check Project Geodatabase (*checkGDB*)](#check-project-geodatabase)
9. [Check Layers in CAD (*checkLayers*)](#check-layers-in-cad)
10. [Create Feature Classes (*createFeatureClasses*)](#create-feature-layers)
11. [Check GPS Control Points (*checkGPS*)](#check-gps-control-points)
12. [Check Geodetic Control Geometries (*checkGeodeticControls*)](#check-geodetic-control-geometries)
13. [Check for POB (*checkPOB*)](#check-for-pob)
14. [Check for Expanded Boundary Layers (*checkEBL*)](#check-for-expanded-boundary-layers)
15. [Check for Closure (*checkClosureCentroid*)](#check-for-closure)
16. [Check for Location (*checkLocation*)](#check-for-location)
17. [Check for Tract Information (*checkServerTractMaps*)](#check-for-tract-information)
18. [Check for Parcel Information (*checkServerParcelMaps*)](#check-for-parcel-information)
19. [Check for Records of Survey Information (*checkServerRecordsOfSurvey*)](#check-for-records-of-survey-information)
20. [Truncating Values (*truncate*)](#truncating-values)
21. [Boundary Course Traverse Path (*traverseCourse*)](#boundary-course-traverse-path)
22. [Obtain Next Course Segment (*nextCourseSegment*)](#obtain-next-course-segment)
23. [Correct Boundary Geometry (*correctBoundaryGeometry*)](#correct-boundary-geometry)
24. [Decimal Degrees to Degrees-Minutes-Seconds (*dd2dms*)](#decimal-degrees-to-degrees-minutes-seconds)
25. [Bearing to Word (*bearingLabel*)](#bearing-to-word)
26. [Map Document Description (*describeMapDocument*)](#map-document-description)
27. [Describe Horizontal Controls (*describeHorizontalControls*)](#describe-horizontal-controls)
28. [Format Labels for Bearing and Distance (*labelBearingDistance*)](#format-labels-for-bearing-and-distance)
29. [Generate CSV Boundary Table (*boundaryToTable*)](#generate-csv-boundary-table)

<br><br>

### PART I: AMC CLASS AND INSTANTIATION

#### AMC CLASS

>```python
>amc(object)
>```
>* This class contains a number of functions, methods, and processes for Automated Map Checking analysis using CAD drawings
>* INPUT/OUTPUT: 
>    * See class instantiation below.

<br>

#### Class Instantiation

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

### PART II: MAIN CLASS FUNCTIONS

#### Base Checks

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

#### Boundary Processing

>```python
>boundaryProcessing(self)
>```
>* This function processes the boundaries of the CAD drawing and performs basic checks. It also processes the boundary multiline features, creates fields in the geodatabase's feature class, mathematically computes bearing, distances, radial angles, etc, for annotation labels and legal descriptions.

<br>

#### Create Legal Description

>```python
>createLegalDescription(self)
>```
>* This function generates a legal description document after boundary processing data.

<br>

#### Finalize Report

>```python
>finalizeReport(self)
>```
>* This function compiles and exports all data and reports, and finishes up the execution.
    
<br><br>

### PART III: SECONDARY CLASS FUNCTIONS

#### Append Report

>```python
>appendReport(self, string)
>```
>* Appends the execution report (opened by class instantiation process)
>* INPUT:
>    * *string*: the string text to be appended in the report.

<br>

#### Arcpy Message

>```python
>getAgpMsg(self, ntabs=1)
>```
>* Obtains and returns the message(s) generated by the execution of arcpy functions.
>* *ntabs*: how many tabs to insert at the beginning of the message (to be used in the execution report)

<br>

#### Check Project Geodatabase

>```python
>checkGDB(self)
>```
>* Checks if the reference geodatabase exists. If it does, it deletes it and creates a new one.

<br>

#### Check Layers in CAD

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

#### Create Feature Classes

>```python
>createFeatureClasses(self)
>```
>* Creates feature classes from original CAD drawing layers. Uses specific and verified layers from the imported CAD drawing features to generate feature classes in the geodatabase.

<br>

#### Check GPS Control Points

>```python
>checkGPS(self)
>```
>* Checks and verifies the presence of the GPS control points in the CAD drawing

<br>

#### Check Geodetic Control Point Geometries

>```python
>checkGeodeticControls(self)
>```
>* Checks for geodetic control point geometries in server geodatabase.

<br>

#### Check for POB

>```python
>checkPOB(self)
>```
>* Checks for the presence of the (True) point of beginning, either by the user, or in the CAD drawing. 

<br>

#### Check for Expanded Boundary Layers

>```python 
>checkEBL(self)
>```
>* CHecking for expanded boundary layers in CAD drawing and corrects geometry if necessary.

<br>

#### Check for Closure

>```python
>checkClosureCentroid(self)
>```
>* Checks for closure: creating boundary polygon and returns it's centroid coordinates.

<br>

#### Check for Location

>```python
>checkLocation(self)
>```
> * Checking County server geodatabase for location data on tract/parcel.

<br>

#### Check for Tract Information

>```python
>checkServerTractMaps(self)
>```
> * Checks for Tract information from server geodatabase.

<br>

#### Check for Parcel Information

>```python
>checkServerParcelMaps(self)
>```
>* Checks for Parcel information from server geodatabase.

<br>

#### Check for Records of Survey Information

>```python
>checkServerRecordsOfSurvey(self)
>```
>* CHecks for Record of Survey information from server geodatabase.

<br>

#### Truncating Values

>```python
>truncate(self, v, n)
>```
>* Trybcates coordinates a the n-th decimal places, for the value v(double).

<br>

#### Boundary Course Traverse Path

>```python
>traverseCourse(self)
>```
>* Obtains the course and order for the boundary traverse path over multilines (PIQ).

<br>

#### Obtain Next Course Segment

>```python
>nextCourseSegment(self, course, segments)
>```
>* Gets the next course coordinate based on the initial line (*course[1]*), and the line segment coordinates from ArcGIS Boundary feature class (PIQ). Returns a JSON string indexed by the order ID (the order to which the lines are added to the course), and for each item, the Boundary feature class OBJECTID, its true start and end coordinates (reversed from the feature class line direction if needed - always clockwise).

<br>

#### Correct Boundary Geometry

>```python
>correctBoundaryGeometry(self)
>```
>* Checks and corrects (if needed) the boundary course geometry given a course and a direction (clockwise or counter-clockwise). The function checks the start and end endpoints and if need reversing it updating the featur class's multiline geometry in the geodatabase.

<br>

#### Decimal Degrees to Degrees-Minutes-Seconds

>```python
>dd2dms(self, dd)
>```
>* Returns formatted coordinates of the Degrees:Minutes:Seconds format. This secondary function restructures decimal degree coordinates into degree/minutes/seconds coordinats. It is called from the main module function.

<br>

#### Bearing to Word

>```python
>bearingLabel(self, bearing)
>```
> * Returns the corresponding direction word based on radial bearing values

<br>

#### Map Document Description

>```python
>describeMapDocument(self)
>```
> * Generates a description of the map document

<br>

#### Describe Horizontal Controls

>```python
>describeHorizontal Controls(self)
>```
> * Obtains and generates the Preamp description from horizontal geodetic controls to the point of beginning.

<br>

#### Format Labels for Bearing and Distance

>```python
>labelBearingDistance(self, bearing, distance)
>```
> * Generates a formatted bearing and distance string from coordinates

<br>

#### Generate CSV Boundary Table

>```python
>boundaryToTable(self)
>```
> * Creates a csv-formatted boundary table containing the course data

<br><br>

## Classes and Execution Code in Folders

### Python Classes and Functions

* [AMC Class](amc/amc.py)
* [ALD Code](amc/ald.py)

#### Execution Code

* [AMC and ALD Combined Execution on native Python Scirpt](amc/pyamcld.py)
* [CAD to AMC ArcGIS Pro Geoprocessing Tool Script](amc/gpamc.py)
* [JSON to Legal Description ArcGIS Pro Geoprocessing Tool Script](amc/gpald.py)
* [Automated Map Checking ArcGIS Toolbox](amc/Automated%20Map%20Checking.tbx)

<br><br>

## Folders and Python Classes

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

