# OCAMC Development Notes<br>Version 1.6

- [x] Created version 1.6 folder structure and added [sample test input CAD Drawing (TR18184)](/amc16/Test/Input/TR18184_PHASE2.dwg).
- [ ] 
- [ ] 
- [ ] 


## Code Steps


**A. Initialize class object (*init*)**
1. Define python class and system variables
2. Initiate global class variables from definitions
3. Define output paths for project and geodatabase (and generate directories if needed or delete old ones).
4. Create new execution report.

**B. Perform basic checks (*baseChecks*)**
1. Define new JSON assembly dictionaries to hold information:
   1. Part 1: execution information (*jsonExecution*)
   2. Part 2: record checks (*jsonChecks*)
   3. Part 3: control types and information (*jsonControls*)
   4. Part 4: boundary parcel info (*jsonBoundary*)
   5. Part 5: legal description (*jsonLegalDescription*) 
2. Determine map type (based on naming convention). For each below, get MapType, MapID, and MapBookType
   1. Determine if it is Tract Map (TR), Parcel Map (PM), Record of Survey (RS), or None.
   2. Then populate maptype, mapid and mapbooktype JSON variables in *jsonControls*   
3. Set spatial reference (ArcGIS: 102646)
4. Set initial arcpy workspace for project.
5. Determine if code executes in the county network domain (PFRDNET)
   1. if yes, create server geodatabase connection (SDE) and add it to the output directory.
   2. if no skip this step.
6. Check 1: Check new geodatabase (*checkGDB*)
7. Import the CAD drawing into the project geodatabase.
8. Check 2: Check for the presence of all the layers in the CAD drawing (*checkLayers*)
9. Check 3: Create feature classes and check closure for boundary processing (*createFeatureClasses*)
10. Check 4: Check for the presence of GPS control points in CAD drawing (*checkGPS*)
11. Check 5: Check for geodetic control geometries (*checkGeodeticControls*)
12. Check 6: Check for the (True) Point of Beginning (*checkPOB*)
13. Check 7: Check for expanded boundary layers (*checkEBL*)
14. Check 8: Check for locations (*checkLocation*)
15. Check 9: Map type checks:
    1. If tract map, executes *checkServerTractMaps*
    2. if parcel map, executes *checkServerParcelMaps*
    3. if record of survey, executes *checkServerRecordsOfSurvey*
16. Obtain the number of boundary parcels in the boundary geometry.
17. Get the course data (traverse order) using function *traverseCourse*
18. Check the boundary geometry and correct if needeed using function *correctBoundaryGeometry*

**C. Perform boundary processing (*boundaryProcessing*)**
1. Define boundary fields list
2. Add fields to the boudnary feature class table in the geodatabase.
3. Check for boundary closure and populate types and coordinates.
    1. Define fields for JSON data string structure (*jsonFields*)
    2. Loop through rows in PIQ feature class multilines and populate attribute fields
        * First, populate fields in the current loop feature (row)
        * Second, match the TPOB with the appropriate boundary files
        * Third, obtain and convert to array well known text (WKT) from object's geometry
    3. Repeat the same loop after writing all the previous fields and variables
        * First, get the last feature from the current feature row in the loop, and obtain attributes
        * Secondly, get the preamp and closing for the description
        * Thirdly, if the feature is a line, get all the legal descriptions
        * Fourthly, if the feature is a curve, get all the legal description
    4. Make another loop for updates and corrections (tangency)
4. Write the derived annotation labels for the boundary geometry to the JSON string (*jsonBoundary*)

**C. Process Legal Description (*createLegalDescription*)**
1. Create a map description (*describeMapDocument*)
2. Create a Preamp (for Grid and Ground versions) from Horizontal Controls (*describeHorizontalControls*)
3. Create the legal description

***D. Finalize report (*finalizeReport*)**
1. Compile the final JSON data from JSON strings




