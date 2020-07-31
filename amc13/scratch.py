# Test for csv writing
import csv
import pandas as pd

temppath = r"c:\Users\ocpwalexandridisk\Downloads"

with open(os.path.join(temppath, "Test.csv"), "w", newline="") as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=",")
    spamwriter.writerow(["Test1", "Test2", "Test3", "Test4", "Test5"])
    spamwriter.writerow([5, 10, 15, 20, 25])

# It's probably better to use Pandas first in the code to store the tabular data as the code develops, and then when the panda table is finalized it can be tansferred to a csv file. For example
import pandas

df = pandas.read_csv("hrdata.csv",
                     index_col = "Employee",
                     parse_dates = ["Hired"],
                     header = 0,
                     names = ["Employee", "Hired", "Salary", "Sick Days"])

df.to_csv("hrdata_modified.csv")


searchFields = ["OID@", "SHAPE@", "coid", "shapetype", "nwkt", "startx", "starty", "midx", "midy", "endx", "endy", "midchordx", "midchordy", "centerx", "centery", "bearing", "distance", "height", "arclength", "radius", "midbearing", "delta", "radbearing_cs", "radbearing_sc", "radbearing_ce", "radbearing_st", "radtangent", "desc_grid", "desc_ground", "ann_grid", "ann_ground", "annweb_grid", "annweb_ground"]

csvFields = ["Map Type", "Map ID", "Map Book Type", "Measurement No", "Tract/Parcel/Map No", "Lot/Parcel No", "Segment No", "Shape Type", "Number of Features in Shape", "Startpoint X","Startpoint Y", "Midpoint X", "Midpoint Y", "Endpoint X", "Endpoint Y", "Mid-chord X", "Mid-chord Y", "Radial Center X", "Radial Center Y", "Line or Chord Bearing", "Line Distance or Chord Length", "Height of Line/Arc", "Arc Length", "Arc Radius", "Mid-chord Bearing to Center", "Radial Curve Angle", "Radial Bearing Center to Start", "Radial Bearing Start to Center", "Radial Bearing Center to End", "Radial Tangent Angle at Start", "Radial Tangent Description", "Legal Description Grid", "Legal Description Ground", "Annotation Grid", "Annotation Ground", "Web Annotation Grid", "Web Annotation Ground"]

dfb = pandas.DataFrame(columns = csvFields)

with arcpy.da.SearchCursor("Boundary", searchFields) as cursor:
    for i, row in enumerate(cursor):
        dfb = dfb.append({
            "Map Type": self.maptype,
            "Map ID": self.mapid,
            "Map Book Type": self.mapbooktype,
            "Measurement No": i,
            "Tract/Parcel/Map No": self.cadname,
            "Lot/Parcel No": "Boundary",
            "Segment No": row[2],
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
            "Annotation Grid": row[28],
            "Annotation Ground": row[29],
            "Web Annotation Grid": row[30],
            "Web Annotation Ground": row[31]
            }, ignore_index=True)

dfb.to_csv("BoundaryData.csv")

writer = pandas.ExcelWriter()