##############################################################
# PYTHON AUTOMATED MAP CHECKING ANALYSIS                     #
# AMC Class Definition                                       #
# Version: 1.6                                               #
# Author: Dr. Kostas Alexandridis, GISP                      #
# Organization: OC Survey Geospatial Services                #
# Date: August 2020                                        #
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
        self.__version__ = "1.6.dev1"
        self.__author__ = "Dr. Kostas Alexandridis"
        arcpy.AddMessage("Automated Map Checking (AMC) Python Class")
        arcpy.AddMessage("Version: {}".format(self.__version__))
        arcpy.AddMessage("Author: {}".format(self.__author__))

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
        AMC Class Function: Import CAD Drawing and perform basic checks
        Imports the CAD drawing and performs basic layer and geometry checks
        """

        self.appendReport("\n{:-^80s}\n".format(" PART 1: AMC BASE CHECKS EXECUTION "))
        stime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M %p")
        self.appendReport("Script started on: {}\n".format(stime))

        # Define new JSON to hold code execution data:
        self.jsonExecution = {}
        self.jsonExecution["Class"] = self.pyclass
        self.jsonExecution["Version"] = self.__version__
        self.jsonExecution["Author"] = self.__author__
        self.jsonExecution["DateTime"] = self.now
        self.jsonExecution["Workstation"] = self.computer
        self.jsonExecution["Domain"] = self.domain
        self.jsonExecution["CondaEnv"] = self.condaenv
        self.jsonExecution["PythonVer"] = self.sysver

        # Define new json to hold record checks:
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

        # Define new JSON to hold control information
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

