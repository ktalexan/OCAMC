# OCAMC Development Notes<br>Version 1.6

- [x] Created version 1.6 folder structure and added [sample test input CAD Drawing (TR18184)](/amc16/Test/Input/TR18184_PHASE2.dwg).
- [ ] 
- [ ] 
- [ ] 


## Code Steps


**A. Initialize class object**
  1. Define python class and system variables
  2. Initiate global class variables from definitions
  3. Define output paths for project and geodatabase (and generate directories if needed or delete old ones).
  4. Create new execution report.

<br>

**B. Perform basic checks**
  1. Define new JSON dictionaries to hold information:
     1. Part 1: execution information (*jsonExecution*)
     2. Part 2: record checks (*jsonChecks*)
     3. Part 3: control types (*jsonControls*)
     4. Part 4: boundary info (*jsonBoundary*)
     5. Part 5: legal description (*jsonLegalDescription*) 
  2. Determine map type (based on naming convention). For each below, get MapType, MapID, and MapBookType
     1. Determine if it is Tract Map (TR), Parcel Map (PM) or Record of Survey (RS), or None.
     2. Then populate maptype, mapid and mapbooktype JSON variables in *jsonControls*   
  3. Set spatial reference (ArcGIS: 102646)
  4. Set initial arcpy workspace for project.
  5. Determine if code executes in the county network domain (PFRDNET)
      1. if yes, create server geodatabase connection (SDE) and add it to the output directory.
      2. if no skip this step.
  6. Check new geodatabase (*checkGDB*)


