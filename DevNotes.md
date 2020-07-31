# OCAMC Code Development Notes {style="text-align:center; color:brown; background-color: Linen"}

<br>

>### Contents {#toc, style="color: purple"}
>* [AMC Versions](#title)
>* [Version 1.5 Notes](#v15)
>   * [Boundary Fields Table](#BoundaryFieldsTable)
>   * [Separate Fields](#SeparateParcels)

<br><br>

## AMC Versions {#title, style="color: brown"}

Name|Version|Date|Status|Notes
---|---|---|---|---
amc|1.4|2019|Stable|Basic version - operates on single boundary parcels
amc15|[1.5](#v15)|2020|Development|Adds additional parcel/map processing capabilities for multiple case studies

<br>

---

<br>

## Version 1.5 {#v15, style="color: darkgreen"}

- [ ] In the conversion of the CAD drawing to geodatabase, the default name of the feature dataset to be created using the *arcpy.CADtoGeodatabase_conversion()* command has been changed from a variable (cadname in v 1.4) to a static ("CAD" in v 1.5) so that the geodatabase names will be standardized and not vary from input to input.


- [ ] The check for closures python function: *checkClosureCentroid()* has been removed and it's functionality has now been incorporated and merged with part 2 of the checks (as part of the *checkLayers()* and *createFeatureClasses()* functions), achieving better code efficiency in execution.

- [ ] The names and number of layers in the CAD drawing has been modified and revised to reflect the agreed standardization of layers for the OC Survey field templates of the County of Orange. The original six layers are replaced by a longer list of layers with different names. This change has significant consequences in the code execution and in the methods used to convert, use, store and query the layers in the resulting geodatabases (and feature classes that are produced). Changes in the code over multiple fuctions has been implemented and applied.

  - [ ] The new template/test drawing that contains the revised layers is *TR18141_REVISION3.dwg* (and its variants).
  - [x] To add code for wkt points (Fizza) - Need to add new entry into the master json file as well:

    ```python
    wktpoints = [i.split(" ") for i in wkt.split("((")[1].split("))")[0].split(", ")]
    ```
  - [x] The revisions for WKT points array was implemented in version 1.5.

- [x] The code was revised and is up to date with single boundary parcel example.

- [ ] TODO: The unicode changes are formatted during the execution for *annweb* fields - need to leave them unformatted for the code to work correctly.


* #### Boundary Fields Table {#BoundaryFieldsTable, style="color: purple"}

    Field | Type | Length | Description | FC | JSON
    :--- | :--- | ---: | :--- | ---: | ---:
    oid | OID@ |  | OBJECTID (ArcGIS) | 0 | 
    shape | SHAPE@ |  | SHAPE (ArcGIS) | 1 | 
    loid | LONG |  | Line ID | 2 | 1
    coid | LONG |  | Course ID | 3 | 2
    poid | LONG |  | Parcel ID | 4 | 3
    toid | LONG |  | TPOB ID | 5 | 4
    tpob | TEXT |  | TPOB Present | 6 | 5
    shapetype | TEXT |  | Shape Type | 7 | 6
    wkt | TEXT | 3000 | Well Known TEXT (WKT) Geometry | 8 | 7
    nwkt | LONG |  | Points in WKT Geometry | 9 | 8
    wktpoints | ARRAY |  | Formatted Array of WKT Points |  | 9
    startx | DOUBLE |  | Startpoint X | 10 | 10
    starty | DOUBLE |  | Startpoint Y | 11 | 11
    midx | DOUBLE |  | Midpoint X | 12 | 12
    midy | DOUBLE |  | Midpoint Y | 13 | 13
    endx | DOUBLE |  | Endpoint X | 14 | 14
    endy | DOUBLE |  | Endpoint Y | 15 | 15
    midchordx | DOUBLE |  | Mid-chord X | 16 | 16
    midchordy | DOUBLE |  | Mid-chord Y | 17 | 17
    centerx | DOUBLE |  | Radial Center X | 18 | 18
    centery | DOUBLE |  | Radial Center Y | 19 | 19
    bearing | DOUBLE |  | Line Bearing or Chord Bearing | 20 | 20
    distance | DOUBLE |  | Line Distance or Chord Length | 21 | 21
    height | DOUBLE |  | Height of Line/Arc | 22 | 22
    arclength | DOUBLE |  | Arc Length | 23 | 23
    radius | DOUBLE |  | Arc Radius | 24 | 24
    midbearing | DOUBLE |  | Mid-chord Bearing to Center | 25 | 25
    delta | DOUBLE |  | Radial Curve Angle | 26 | 26
    radbearing_cs | DOUBLE |  | Radial Bearing: Center to Start | 27 | 27
    radbearing_sc | DOUBLE |  | Radial Bearing: Start to Center | 28 | 28
    radbearing_ce | DOUBLE |  | Radial Bearing: Center to End | 29 | 29
    radbearing_st | DOUBLE |  | Radial Tangent Angle at Start | 30 | 30
    radtangent | TEXT |  | Radial Tangent Description | 31 | 31
    desc_grid | TEXT | 3000 | Legal Description (Grid) | 32 | 32
    desc_ground | TEXT | 3000 | Legal Description (Ground) | 33 | 33
    ann_grid | TEXT |  | Annotation (Grid) | 34 | 34
    ann_ground | TEXT |  | Annotation (Ground) | 35 | 35
    annweb_grid | TEXT |  | Web Annotation (Grid) | 36 | 36
    annweb_ground | TEXT |  | Web Annotation (Ground) | 37 | 37



<br>

### Separate Parcels {#SeparateParcels, style="color: purple"}

- [ ] The code fails in the loop of line 1687 because the PIQ (parcel lines) are all mixed together for the two boundary parcels. They either need to be separated, or select the lines that belong to each parcel.

- [ ] Another idea is to add properties for the PIQ line (field) that contains which parcel it belongs to for separate parcels.

- [ ] Another issue is on the *checkClosureCentroid()* function: the function doese not update and populate fields for both of the parcels. There are some issues with the var *poid* - needs to be revisited.

- [ ] Proposed solution: First loop though the boundary area polygons:  

    ```python
    # Loop through the parcel boundary areas (polygons)
    with arcpy.da.SearchCursor("PARCELS", ["OID@", "SHAPE@", "CentroidX", "CentroidY", "AreaSqFeet", "AreaAcres"]) as cursor1:
        for row1 in cursor1:
            oid1 = row1[0]
            print("Selected Parcel: {}".format(oid1))
        
            # For each of the boudnary polygons, make a selection (select by attribute OBJECTID) and create a temporary layer (layer1)
            layer1 = arcpy.SelectLayerByAttribute_management("PARCELS", "NEW_SELECTION", "OBJECTID = {}".format(oid1))
        
            # For each of the selected polygons, select all the polylines in the PIQ feature class whose boundary touches 
            # the boundaries of the polygon (select by location) and create a temporary layer (layer2)
            layer2 = arcpy.SelectLayerByLocation_management("PIQ"< "BOUNDARY_TOUCHES", layer1, None, "NEW_SELECTION", "NOT_INVERT")

            # Now loop through the selected multiline (PIQ) layer2 and get all the OBJECTIDs that belong to this parcel.
            with arcpy.da.SearchCursor(layer2, ["OID@", "SHAPE@"]) as cursor2:
                for row in cursor2:
                    oid2 = row2[0]
                    print("\t{}".format(oid2))

            # Finally, remove temporary layers using arcpy
            arcpy.Delete_management(layer1, layer2)
    ```
  - [x] Tried it and it works
  - [ ] Need to revise the *traverseCourse* function: Either loop through each of the parcels from the beginning (eg, add parameter courseID in the function), or loop internally within the function.
  - [ ] Another option is to add a parcelID into the boundary lines so we can match the boundary lines by parcelID (this will be preferred)

- [ ] Need to institute a new naming convention and variables for the entire code in order to facilitate multiple parcel cases. Specifically:

    Var | Name | Description
    --- | --- | ---
    **poid** | Parcel ID | Boundary parcel object ID: can be single, or multiple
    **toid** | TPOB ID | True point of beginning or point of beginning ID: can be single or multiple, and each one can be possibly associated with each of the Parcel IDs (poid) depending on the case
    **loid** | Line ID | The multiline (PIQ) ID that comes from the CAD drawing into ArcGIS geodatabase. It is essentially the OBJECTID of the PIQ multiline feature class
    **coid** | Course ID | The course order ID for the traverse procedure. Calculated for each parcel and starts from 1 for each of the boundaries (poid)

- [ ] Need to move the boundary fields creation of the PIQ layers into the *createFeatureClasses()* function.

<br>

#### Update on ArcGIS 2.6 (7/31/2020) {#upd200731}

- [x] The new ArcGIS Pro 2.6 arcpy (I believe) has changed the way the CAD drawing is imported to the geodatabase. Now, after import, the creation of a boundary parcel (for single and multiple parcels) fails to create unique parcels, as the parcel segments and parcel lines are both imported together in the V-LINE-PIQ multiline feature class.
- [x] I noticed that it now creates an additional feature class called "ParcelSegment" in the "CAD" feature dataset imported to the geodatabase. This "ParcelSegment" multiline feature class does separate the different types in their attribute table. In the attribute "Layer", it does separate the "V-LINE-PIQ" (boundary edges) from "V-LINE-PCLS" (segments). Thus, we can use this process to create a new boundary polygon area, using arcpy:

    ```python
    # Set the arcpy workspace to the feature dataset of the 'CAD' group in the geodatabase (group created by CAD importing)
    arcpy.env.workspace = os.path.join(gdbpath, "CAD")
    arcpy.env.OverwriteOutput = True
    
    # Two possible options here

    # First option:
    fclist = arcpy.ListFeatureClasses() # List the feature classes in the feature dataset
    if "ParcelSegment" in fclist:
        layer1 = arcpy.SelectLayerByAttribute_management("ParcelSegment", "NEW_SELECTION", "Layer='V-LINE-PIQ'", "NON_INVERT")
        arcpy.FeatureToPolygon_management(layer1, "Boundary")
    
    # Second option:
    if arcpy.Exists("ParcelSegment"):
        layer1 = arcpy.SelectLayerByAttribute_management("ParcelSegment", "NEW_SELECTION", "Layer='V-LINE-PIQ'", "NON_INVERT")
        arcpy.FeatureToPolygon_management(layer1, "Boundary")
    ```

- [ ] 


