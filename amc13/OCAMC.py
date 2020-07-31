import math, os, arcpy, json

computername = os.getenv('COMPUTERNAME')

cadname = 'TR18141'
cadfile = 'TR18141_REVISION2_MASTER.dwg'


if computername == 'SRVYGS046C':
    cadpath = os.path.join(r'f:\OneDrive\Professional\Projects\OCPW\OCML\OCAMC\input_CAD', cadfile)
    prjpath = r'f:\OneDrive\Professional\Projects\OCPW\OCML\OCAMC\python\LegalDescDev'

elif computername == 'OCPW-B180019':
    cadpath = os.path.join(r'E:\Dev\Repos\OCAMC\Examples\Input', cadfile)
    prjpath = r'E:\Dev\Repos\OCAMC'


scale = 'grid' # or 'ground'
scalefactor = 0.99996770
tpob = None
direction = None
#direction = 'counter-clockwise'
tolerance = 2 # decimal places for truncation


os.chdir(prjpath)

from amc import amc

amc1 = amc(cadname, scale, scalefactor, cadpath, prjpath, tpob, direction, tolerance)
amc1.baseChecks()
amc1.boundaryProcessing()
amc1.createLegalDescription()
jsonResponse = amc1.finalizeReport()




print(json.dumps(jsonResponse, indent=4))





# Test development for ground to grid (and vice versa) conversion
def g2g(self, coor, anchor=False):
    """AMC Class Function: Convert coordinates grid to ground (and vice versa)
    Converts grid to ground or ground to grid coordinates based on existing project's scale ('grid' or 'ground'), the project's scalefactor, and whether the point is an anchor or not.
    """
    cx, cy = coor
    if anchor is False:
        if self.scale == 'grid':
            gridc = cx, cy
            groundc = cx / self.scalefactor, cy / self.scalefactor
        elif self.scale == 'ground':
            gridc = cx * self.scalefactor, cy * self.scalefactor
            groundc = cx, cy
    else:
        gridc = groundc = cx, cy

    return gridc, groundc













#TODO This is a TODO tag on a comment.
#? This is a question tag one a comment.
#x This is an underlined text coment
#! This is an important comment.
