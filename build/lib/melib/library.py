""" 
    **library.py**

    Routines to perform short mechanical engineering design tasks without explicit instantiation.
"""

import cmath
import math
# import matplotlib.pyplot as plt
import numpy as np
import sys
# sys.path.insert(0, ".")
from melib.xt import mdxziplist,engfmt,openplot
from melib.excel import Xcel

PIE = math.pi
CALCRECORD = ""
XXXX = "Dummy"

def calcrecord():
    return CALCRECORD


def resetrecord(s=""):
    global CALCRECORD
    CALCRECORD = s


#
#TESTING = 'bmdiagram'
# TESTING="bearingpick"
# TESTING="isofits"
TESTING = ""
#
#
#
SVAR = " _ssssss_ "
NVAR = " _nnnnnn_ "
# the arguments should str, e.g. unitconvert("Calories_per_Cm2Min","W_per_M2")


def unitconvert(fromunit, tounit):
    """ Returns the coefficient to convert a number from one unit to another.  For example,

    >>> y=x*unitconvert("Calories_per_Cm2Min","W_per_M2")

    will convert 'x' in units of 'Cal/(cm2-min)' to 'y' in 'Watts/m2'.

    The supported unit pairs are:

    * "Calories_per_Cm2Min" ---> "W_per_M2"

    * "Grams_per_Dm2Hr"     ---> "Kg_per_M2H"

    * "Lbf_inch"            ---> "N-m"
    """
    # Irradiance from calories/(cm2-min)
    Calories_per_Cm2Min = {'W_per_M2': 697}
    # Transpiration rate from g/(dm2-h)
    Grams_per_Dm2Hr = {"Kg_per_M2H": 4e-05}
    Lbf_inch = {"N-m": 0.113}  # 1 lbf-in=1/2.204*9.81*0.0254 N-m
    x = eval(fromunit)
    y = x[tounit]
    return y


def dictquery(d, k):
    z = ""
    if k == "?":
        z += "%s data exist only for the following ('+++' means that a second argument needs to be provided, e.g. temperature):\n\n" % (d["dname"])
        for s in d.keys():
            if s!="dname":
                zs="* "+s
                if len(d[s])>1:
                    zs+=" +"
                z += zs+"\n"
        return (True, z)
    return (False, k)


def thconductivity(metal, T=[]):
    """ Returns the thermal conductivity[W/m-C] of the metal.  The second argument is the temperature[ :superscript:`o` C].
    Enter

    >>> print(thconductivity("?"))

    to see the supported metals.
    """
    thca = {"inconel 750": (np.array([149, 316, 538, 649, 760, 871]), np.array([16.9, 20.5, 26.5, 28.7, 31.4, 35.3])),
            "ss304": (np.array([16.2])), "dname": "Thermal Conductivity(W/m-C)"}
    q = dictquery(thca, metal)
    if q[0]:
        return q[1]
    if metal in thca.keys():
        thc = thca[metal]
        if len(thc) > 1:
            if T==[]: T=thc[0][0]
            return np.interp(T, thc[0], thc[1])
        else:
            return thc[0]
    else:
        print("No Thermal Conductivity data for %s.  Returns 0." % metal)
        return 0.0


def density(metal, T=[]):
    """ Returns the density[kg/m3] of the metal.  The optional second argument is the temperature[ :superscript:`o` C].
    Enter

    >>> print(thconductivity("?"))

    to see the supported metals.
    """
    density_data = {"inconel 750": (np.array([8250])), "ss304": (np.array([8030])),
                    "steel": (np.array([7850])), "alum": (np.array([2700])), "dname": "Density[kg/m3]"}
    q = dictquery(density_data, metal)
    if q[0]:
        return q[1]
    x = density_data[metal]
    if len(x) > 1:
        if T==[]: T=x[0][0]
        return np.interp(T, x[0], x[1])
    else:
        return x[0]

#


def opendatafiles(tags=["bearing", "mats", "sgear", "shaft", "vbelt"], makezip=False):
    """

    Action
        Opens the Excel files in the `data` folder and returns file pointers.


    Arguments
        `tags` : Array of strings.
        Excel file names.  All data files will be opened if tags is unspecified.

        `makezip` : Boolean.
        Whether to add the files to a zip package (used in notebooks).

    Returns
        Xcel pointers to the data files.  You may have to use these pointers when calling
        other `library` functions.

    Example

        >>> [Xbear, Xmat, Xgear, Xshaft, Xbelt]=opendatafiles()

    """
    x = []
    import os
    pt = os.path.dirname(os.path.realpath(__file__))
    for s in tags:
        #        datafilename=DATAFOLDER+"\\"+"%s.xlsx"%s
        datafilename=pt+"\\data\\%s.xlsx"%s
        x.append(Xcel(datafilename))
        if makezip:
            mdxziplist([datafilename])
    return x

def alloyprop(x, base, alloyname, props):
    """

    Action
        Alloy material property look up. Uses the files in the `data` folder.

    Arguments
        `x` :  Xcel pointer to `mats.xlsx`.  See the file for supported metals.

        `base` : Sheet name in `matx.xlsx`, e.g. *steel*, *alum*, *titanium*, *nickel*

        `alloyname` : Alloy designation as they appear in column C of the Excel sheet, e.g. "1350-H19"

        `props` : Properties wanted as in the HEADINGS in the file, e.g. *['SUMPA', 'SYMPA']* to get Su and Sy

    Example
        >>> xmat=opendatafiles(tags=["mats"])[0]
        >>> [su, sy, rho]=alloyprop(xmat, "nickel", "N06110", ["SUMPA", "SYMPA", "RHO"])
        >>> print(su, sy, rho)
        >>> 1205.0 1034.0 8330.0

    """
    if x == None:
        x = opendatafiles(tags=["mats"])[0]
        x.sheet(base)
    else:
        x.sheet(base)
    noftables = x.vir("NOFTABLES")
    tablenum = 1
    v = x.rnvit(tablenum, alloyname, props)
    while np.isnan(v[0]) and tablenum < noftables:
        tablenum += 1
        v = x.rnvit(tablenum, alloyname, props)
    return v

def alumprop(x, alloyname, props):
    """ Short cut for `alloyprop(x, "alum", alloyname, props)`

    """
    return alloyprop(x, "alum", alloyname, props)


def titanprop(x, alloyname, props):
    """ Short cut for `alloyprop(x, "titanium", alloyname, props)`

    """
    return alloyprop(x, "titanium", alloyname, props)


def steelprop(x, alloyname, props):
    """ Short cut for `alloyprop(x, "STEELS", alloyname, props)`

    """
    return alloyprop(x, "steel", alloyname, props)

# COLUMNS


def fixity(econ, ideal=False):  # e.g. econ="pinned-pinned"
    """ Returns the value of the constant K in the Euler equation for
    buckling.  The arguments are

    econ : End conditions.  Could be:
              "pinned-pinned"
              "fixed-fixed"
              "fixed-free" (or "free-fixed")
              "fixed-pinned" (or "pinned-fixed")
    ideal : Returns theoretical values if this True.
            Otherwise, returns practical values

    Example
        >>> Ka=fixity("pinned-fixed")  # Actual value For pinned-fixed ends
        >>> Ki=fixity("pinned-fixed", ideal=True)  # Ideal value For pinned-fixed ends

    """
    did = {"pinned-pinned": 1.0, "fixed-fixed": 0.5,
           "fixed-free": 2.0, "fixed-pinned": 0.7}
    dpr = {"pinned-pinned": 1.0, "fixed-fixed": 0.65,
           "fixed-free": 2.1, "fixed-pinned": 0.8}
    s = econ.lower()
    if s == "free-fixed":
        s = "fixed-free"
    if s == "pinned-fixed":
        s = "fixed-pinned"
    if ideal:
        return did[s]
    else:
        return dpr[s]
# Welded joints
# t : Plate thickness
# Returns the minimum fillet weld sizes for this plate thickness
def weldsize(t):
    """ Returns the minimum weld size[mm] for plate thickness 't'[mm]

    Argument
        `t` : Plate thickness in mm

    Returns
        The minimum weld size[mm] recommended for this plate thickness

    Example:
        weldsize(18.0) # returns 6.35 mm

    Reference: Mott, Table 20-4 Minimum weld sizes for thick plates

    """
    ta = np.array([0.5, 0.75, 1.50, 2.25, 6, np.inf])*25.4
    wa = np.array([3.0/16, 0.25, 5.0/16, 3./8, 0.5, 5.0/8])*25.4
    j = np.where(ta > t)[0][0]
    return(wa[j])

def fi(a, x):
    try:
        j = np.where(a == x)[0][0]
        return j
    except:
        return None


def alumweldstrength(base, filler):
    """
    Action
        Allowable shear stresses for fillet welds on aluminium
    Arguments
        `base` : Designation for the metal joined, e.g. `1100`

        `filler` : Filler alloy number, e.g. `4043`
    Return
        Allowable shear stress in MPa
    Example
        >>>alumweldstrength(6061, 5356) # returns 48.00 MPa
    """
    fillers = np.array([1100, 4043, 5356, 5556])
    metals = np.array([1100, 3003, 6061, 6063])
    taua = np.array([[22, 33, None, None], [22, 34, None, None],
                     [None, 34, 48, 59], [None, 34, 45, 45]])
    if base == "?":
        return(fillers, metals)
    j = fi(fillers, filler)
    i = fi(metals, base)
    if i == None or j == None:
        return None
    return taua[i][j]

# WELDED STRUCTURES
def ec3cutoff(detail):
    """
    Action
        Eurocode 3 Cut-off limits for lattice girder joints as per Table 2.4 in Design Guide, Zhao et al
    Argument
        `detail` : The Detail category from Table B.2, e.g. `56` for K-joint with overlap
    Return
        Cut-off limit (the life is indefinite for stress ranges below this limit)
    Example
        >>> ec3cutoff(71)  # returns 32 MPa
    """
    Cut_offs = {90: 41, 71: 32, 56: 26, 50: 23, 45: 20, 36: 16}
    return Cut_offs[detail]


def ec3life(nomstress, tr, joint="K", overlap=True, section="CHS"):
    """
    Arguments
        `nomstress` : Nominal stress range, MPa

        `tr` : Wall thickness ratio (Chord thickness divided by brace thickness)

        `joint` : 'K' or 'N'

        `overlap` : True if overlap joint; False if joint with a gap

        `section` : Not used.  Only CHS are supported

    Returns `N`
        N[0] = Life in cycles for the thickness ratio `tr` as given

        N[1] = Life in cycles for `tr` as 1.0

        N[2] = Life in cycles for `tr` as 1.40

    Example
        ec3life(120.0, 1.2, joint='N')   # returns (80357,25866,134848) cycles
    """
    def onelife(nomstress, se):
        if nomstress < se:
            return np.inf
        else:
            return 1.e8*(se/nomstress)**5
    if joint.upper() == "K" and overlap and section.upper() == "CHS":
        (tboun, dc1, dc2) = (1.40, 56, 71)
    elif joint == "N" and overlap and section.upper() == "CHS":
        (tboun, dc1, dc2) = (1.40, 50, 71)
    else:
        sys.exit("unsupported E3LIFE call with (joint=%s, overlap=%s, section=%s)" % (
            joint, overlap, section))
    Se1 = ec3cutoff(dc1)
    Se2 = ec3cutoff(dc2)  # Endurance strength when tr>=tboun
    N1 = 1.e8*(Se1/nomstress)**5
    N2 = 1.e8*(Se2/nomstress)**5
    if nomstress < Se1 and nomstress < Se2:
        return np.array([np.inf, N1, N2])
    if tr > tboun:
        N = onelife(nomstress, Se2)
        return np.array([N, N1, N2])
    elif tr > 1.0:
        if nomstress < Se1:
            return np.array([np.inf, N1, N2])
        elif nomstress < Se2:
            N = 1.e8*(Se1/nomstress)**5
            return np.array([N, N1, N2])
        else:
            N = (tr-1.0)/(tboun-1.0)*(N2-N1)+N1
            return np.array([N, N1, N2])
    else:
        N = onelife(nomstress, Se1)
        return np.array([N, N1, N2])

def boltgrades(x, grade, props):
    """
    Arguments
        `x` : Pointer to the bolts sheet in the materials data file

        `grade` : Bolt grade, e.g. "4.8"

        `props` : ["Dmin","Dmax","SUMPA","SYMPA","PROOF"] or a subset

    Returns `v`
        v[0] = Value from the file for 'props[0]'

        v[1] = Value from the file for 'props[1]'

        etc

    Example
        x=opendatafiles(["mats"])[0]

        x.sheet("bolts")

        v=boltgrades(xmat, "4.8", ["Dmin", "PROOF"])

        print(v) # will print "[  1.6 310. ]"

    """
    if x == None:
        x = opendatafiles(tags=["mats"])[0]
        x.sheet("bolts")
    else:
        x.sheet("bolts")
    
    v = x.rnvit(1, "GRADE "+grade, props)
    return v



def boltpitch(dmajor, coarse=True):
    """
    Arguments
        `dmajor` : Major diameter

        `coarse` : True if coarse thread; False if fine thread

    Returns pitch[mm] and stress area[mm2] as a tuple


    Example

        (pitch, At)=boltpitch(42, coarse=False) ==> pitch=3, At=1206

    """

    dcoarse = np.array([1, 1.6, 2, 2.5, 3, 4, 5, 6, 8, 10,
                        12, 16, 20, 24, 30, 36, 42, 48])
    pcoarse = np.array([.25, .35, .4, .45, .5, .7, .8, 1,
                        1.25, 1.5, 1.75, 2., 2.5, 3, 3.5, 4, 4.25, 5])
    dfine = np.array([1.6, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 30, 36])
    pfine = np.array([.2, .25, .35, .35, .5, .5, .75,
                      1, 1.25, 1.25, 1.5, 1.5, 2, 2, 3])
    if coarse:
        d = dcoarse
        p = pcoarse
    else:
        d = dfine
        p = pfine
    pitch = np.interp(dmajor, d, p)
    At = PIE/4*(dmajor-0.9382*pitch)**2
    return(pitch, At)


# ARGUMENTS
# x : The Xcel pointer to the Belt Data file
# beltdes: Belt designation, e.g. "3V" or "5V"
# datumlength[mm] : Length target for the belt
# RETURNS values read from Optibelt Catalogue Table 25
# 1: Belt designation, e.g. "3V 1060"
# 2: Outside length[mm] of this belt designation
# 3: Length factor, c3
def vbeltlengths(x, beltdes="5V", datumlength=673.0):
    """
    Arguments
        `x` : Xcel pointer to the belts data file

        `beltdes` : Belt designation, e.g. "3V" or "5V"

        `datumlength` : Length target for the belt, mm

    Returns values read from Optibelt Catalogue Table 25

        [1] = Belt designation, e.g. "3V 1060"

        [2] = Outside length[mm] of this belt designation

        [3] = Length factor, c3


    Example

        x=opendatafiles(["vbelt"])[0]

        v=vbeltlengths(x, "5V", 673.0)

        print(v) # will print "('5V 500', 1270, 0.84)"

    """

    if x == "?":
        z = '__vbeltlengths__ (`Xv`, `beltdes`= _ssssss_ , `datumlength`= _nnnnnn_ )\n\n'
        z += '* Xv : The pointer to the excel file that has data from Optibelt Catalogue Table 24\n'
        z += '* beltdes: Belt designation, e.g. "3V" or "5V"\n'
        z += '* datumlength[mm] : Length target for the belt\n\n'
        z += 'RETURNS (d, L, c3) with\n\n'
        z += '* d : Belt designation, e.g. "3V 1060"\n'
        z += '* L : Outside length[mm] of this belt designation\n'
        z += '* c3 : Length factor, c3\n\n'
        z += '_Note_ :\n\n* "nnnnnn" is a number\n* "ssssss" is a string\n\n'
        return z

    x.sheet("LENGTHS")
    for i in range(1, x.maxrow()):
        d = x.cell(i, 1)
        if d == beltdes:
            L = x.cell(i, 3)
            if L > datumlength:
                d2 = x.cell(i, 2)
                c3 = x.cell(i, 4)
                return(d+" %d" % d2, L, c3)
    return (None, None, None)
# ARGUMENTS
# x : The Xcel pointer to the Belt Data file
# beltdes: Belt designation, e.g. "3V" or "5V"
# rpm: Speed of the driving pulley[rpm]
# dsheave: Diameter of the driving pulley[mm]
# rat: Speed reduction across this belt transmission stage
# RETURN values read from Optibelt Table 41(beltdes=3V) or 43(beltdes=5V)
# 1:PN(Nominal rating,kW) from Optibelt Catalogue Table 41(for 3V) or 43(for 5V)
# 2:Additional power per belt from Optibelt Catalogue Tables 41 or 43(3V or 5V)


def vbeltpower(x, beltdes="5V", rpm=3000, dsheave=100.0, rat=2.0):
    """
    Arguments
        `x` : Xcel pointer to the belts data file

        `beltdes` : Belt designation, e.g. "3V" or "5V"

        `rpm` : Speed of the driving pulley[rpm]

        `dsheave` : Diameter of the driving pulley[mm]

        `rat` : Speed reduction across this belt transmission stage

    Returns values read from Optibelt Table 41(beltdes=3V) or 43(beltdes=5V)

        [1] = PN(Nominal rating,kW) from Optibelt Catalogue Table 41(for 3V) or 43(for 5V)

        [2] = Additional power per belt from Optibelt Catalogue Tables 41 or 43(3V or 5V)

    Example

        x=opendatafiles(["vbelt"])[0]

        v=vbeltpower(x, "5V", rpm=3000, dsheave=100.0, rat=2.0)

        print(v) # will print "(24.98, 4.47)"

    """

    if x == "?":
        z = '__vbeltpower__ (`Xv`, `beltdes`=%s, `rpm`=%s, `dsheave`=%s, `rat`=%s)\n\n' % (
            SVAR, NVAR, NVAR, NVAR)
        z += '* `Xv` : The Xcel pointer to the Belt Data file\n\
* `beltdes` : Belt designation, e.g. "3V" or "5V"\n\
* `rpm` : Speed of the driving pulley[rpm]\n\
* `dsheave` : Diameter of the driving pulley[mm]\n\
* `rat` : Speed reduction across this belt transmission stage\n\n\
RETURN values read from Optibelt Tables 41 or 43:\n\n\
* `kw` : PN(Nominal rating,kW) from Optibelt Catalogue Table 41(for 3V) or 43(for 5V)\n\
* `kwadd` : Additional power per belt from Optibelt Catalogue Tables 41 or 43(3V or 5V)\n\n'
        return z
    if rat > 1.57:
        k = 3
    elif rat > 1.27:
        k = 2
    elif rat > 1.06:
        k = 1
    elif rat > 1.01:
        k = 0
    if not beltdes in ["3V", "5V"]:
        print("vbeltpower: Unsupported belt designation.")
        return (0, 0)
    x.sheet(beltdes+"POWER")
    ncols = x.cell(1, 1)
    for j in range(2, ncols+1):
        d = x.cell(1, j)
        if d >= dsheave:
            for i in range(2, x.maxrow()):
                n = x.cell(i, 1)
                if n >= rpm:
                    return (x.cell(i, j), x.cell(i, ncols+2+k))

# ARGUMENTS
# x : The Xcel pointer to the Belt Data file
# d : Diameter of the driving pulley[mm]
# D : Diameter of the driven pulley[mm]
# C : Centre distance
# RETURN
# 1: Wrap angle beta (for the driving sheave - see Optibelt catalogue p.73)
# 2: Arc contact correction factor c1 (Optibelt Catalogue Table 22)


def vbeltc1(x, d, D, C):
    """
    Arguments
        `x` : Xcel pointer to the belts data file

        `d` : Diameter of the driving pulley[mm]

        `D` : Diameter of the driven pulley[mm]

        `C` : Centre distance[mm]

    Returns

        [1] = Wrap angle beta (for the driving sheave - see Optibelt catalogue p.73)

        [2] = Arc contact correction factor c1 (Optibelt Catalogue Table 22)

    Example

        x=opendatafiles(["vbelt"])[0]

        v=vbeltc1(x, 75, 230, 420)

        print(v) # will print "(156.0, 0.99)"

    """

    x.sheet("BETA")
    r = abs(D-d)/C
    for i in range(2, x.maxrow()):
        if x.cell(i, 1) >= r:
            s=x.cell(i, 2)[:-1]
            return(float(s), x.cell(i, 3))

#
# GEAR FUNCTIONS

def geartip(dp, m):
    """
        Call with `dp` =pitch diameter and `m` =module both expressed using the same units
        , e.g. mm.  The function returns the tip radius.  It is assumed that the
        addendum is equal to the module.

        **Example** : ``geartip(168, 8)`` --> `184`

    """
    return dp+2*m  # Assumes ADDENDUM=m


def mintoothnum(phi):
    """
        Call with ``phi`` as the pressure angle in degrees. Returns the minimum
        number of teeth allowed on the pinion to prevent interference when driving
        a rack.  The pressure angles of 14.5, 20, and 12 are supported. Reference is
        Mott, Table 8-7.

        **Example** : ``mintoothnum(20)`` --> `18`
    """
    MINTOOTHNUM = {14.5: 32, 20: 18, 25: 12}
    if phi in MINTOOTHNUM.keys():
        return MINTOOTHNUM[phi]
    else:
        sys.exit("MINTOOTHNUM error - Wrong pressure angle (%.1f)" % phi)


def huntingteeth(Np, Ng):
    """
        This function is used by the auto marker.

        When the number of teeth on a pinion and the gear has common multiples,
        there may be preferential matching between gears and this would cause
        premature wear.  When called with ``Np`` and ``Ng`` as the numbers of
        teeth on the pinion and the gear, respectively, this function returns

            0 if ``Ng`` is an integer multiple of ``Np``

            0.5  if there is at least one common multiple, e.g. both are even numbers

            1 if there are no common multiples

            **Examples**
                ``huntingteeth(23,46)`` --> `0`

                ``huntingteeth(22,46)`` --> `0.5`

                ``huntingteeth(23,47)`` --> `1`
    """
    Np = int(Np)
    Ng = int(Ng)
    r = int(Ng/Np)
    if (Ng == (r*Np)):
        return 0
    for i in range(2, Np):
        if (Np % i == 0) and (Ng % i) == 0:
            return 0.5
    return 1

# ARGUMENTS:
# bhn: Brinelll hardness
# grade: Gear Material grade (1 or 2; default=1)
# RETURN:
# (Sat, Sac): Allowable (bending, contact) strength numbers[MPa]


def agmastrength(h, surface="none", grade=1, record=False):
    """
        Call this function with ``h`` as the Brinell hardness of the gear
        material and it will return the AGMA allowable bending and contact
        stress numbers for Grade 1 AGMA materials.

        The reference is the `AGMA 2001-D04`, e.g. as in Mott Figs
        9.11 and 9.12.  AGMA does not allowable extrapolation for hardness values
        above 400HB.

        **Examples**
            ``agmastrength(400)`` --> `(301.5, 1088.6)`

            ``agmastrength(600)`` --> `(301.5, 1088.6)`

            ``agmastrength(300)`` --> `(248.2, 866.6)`

        You may specify Grade 2 by using the argument ``grade``, e.g.
        ``agmastrength(300, grade=2)`` returns `(324.0, 959.5)`.

        If a surface treatment is specified by using the argument ``surface``,
        the strength is adjusted accordingly by using the AGMA recommendations as
        tabulated in Mott, Table 9-5.

        The allowable surface modifications are 'flame hardened' and
        'carburised'.  The default is no surface modification.

        **Examples**
            ``agmastrength(300, surface="flame hardened")`` --> `(310, 1207)`

            ``agmastrength(300, surface="carburised")`` --> `(379, 1241)`

    """
    global CALCRECORD
    if record:
        CALCRECORD = ["", ""]
    if h>400:
        h=400
    if surface == "none":
        bhn = h
        if grade == 1:
            Sat = 0.533*bhn+88.26
            Sac = 2.22*bhn+200.6
            if record:
                CALCRECORD[0] = "0.533*%.0f+88.26" % bhn
                CALCRECORD[1] = "2.22*%.0f+200.6" % bhn
        elif grade == 2:
            Sat = 0.703*bhn+113.1
            Sac = 2.41*bhn+236.5
            if record:
                CALCRECORD[0] = "0.703*%.0f+113.1" % bhn
                CALCRECORD[1] = "2.41*%.0f+236.5" % bhn
    elif grade > 1:
        sys.exit("AGMASTRENGTH: Surface hardening allowed only for Grade 1.")
    else:
        CALCRECORD = ["Surface hardening:%s" % surface]*2
        hrc = h
        if hrc > 54:
            hrc = 54
        if surface == "flame hardened":
            Sat = 310
            if hrc == 50:
                Sac = 1172
            elif hrc == 54:
                Sac = 1207
            else:
                sys.exit("AGMASTRENGTH: Only 50HRC or 54HRC allowed")
        elif surface == "carburised":
            Sat = 379
            Sac = 1241
        else:
            sys.exit("AGMASTRENGTH: Unknown surface treatment('%s')" % surface)
    #
    return (Sat, Sac)

# ARGUMENTS:
# r: Desired reliabilityy, e.g. 0.99 for 99%
# RETURN:
# KR: Reliability factor


def agmaKR(r):
    """
        Call with ``r`` as the required reliability and the function will return
        the corresponding AGMA reliability factor KR.

        **Example** ``agmaKR(0.98)`` --> `0.98333`

    """
    import numpy as np
    R = [0.9, 0.99, 0.999, 0.9999]
    K = [0.85, 1.0, 1.25, 1.50]
    # K=0.70 for R=0.50 but I will not allow using R<0.90.  If they do, K will
    # be that for R=0.90
    Kr = np.interp(r, R, K)
    return Kr


# Called by agmaJ().
def J2(N1, N2):
    import numpy as np
    from scipy import interpolate
    # The starting point for the following tables are Collins, Mechanical Design
    # I added them points using the Mott Figure 9-15(b)
    x = np.array([17, 19, 21, 26, 29, 35, 55, 135])
    y = np.array([17, 19, 21, 26, 29, 35, 55, 135])
    # a[row,col] is the J for N1=x[col] and N2=y[row]
    a = np.array([  # N1
        [0.289,  0.315,    0.326, 0.347, 0.356,  0.378, 0.415, 0.447],  # 17
        [0.289,  0.316,    0.326, 0.348, 0.357,  0.380, 0.417, 0.448],  # 19
        [0.289,  0.317,    0.327, 0.349, 0.358,  0.381, 0.418, 0.450],  # 21
        [0.289,  0.319,    0.330, 0.351, 0.360,  0.384, 0.422, 0.454],  # 26
        [0.289,  0.321,    0.332, 0.353, 0.363,  0.387, 0.425, 0.458],  # 29
        [0.289,  0.325,    0.336, 0.358, 0.367,  0.392, 0.431, 0.465],  # 35
        [0.289,  0.333,    0.343, 0.366, 0.376,  0.402, 0.444, 0.480],  # 55
        [0.289,  0.339,    0.351, 0.376, 0.387,  0.414, 0.460, 0.499]])  # 135
# N2    7      19         21    26     29       35     55     135

    fp = interpolate.interp2d(x, y, a)
    return fp(N1, N2)[0]

# ARGUMENTS
# sdrive: The drive description, e.g. "UNIFORM", "LIGHT SHOCK", ...
# sload: The load description, e.g.  "UNIFORM", "LIGHT SHOCK", ...
# RETURN
# The Overload factor, Ko


def agmaKo(sdrive, sload):
    """
        Call with ``sdrive`` describing the drive characteristics and ``sload``
        representing the load characteristics and the function will return the
        AGMA overload factor Ko.  The acceptable values are:

        ``sdrive : ["UNIFORM", "LIGHT SHOCK", "MODERATE SHOCK"]``

        ``sload : ["UNIFORM", "LIGHT SHOCK", "MODERATE SHOCK", "HEAVY SHOCK"]``

        **Example** ``agmaKo("light shock", "uniform")`` --> `1.2`

        The arguments are case-insensitive.
    """
    sdrive = sdrive.upper()
    sload = sload.upper()
    load = ["UNIFORM", "LIGHT SHOCK", "MODERATE SHOCK", "HEAVY SHOCK"]
    drive = ["UNIFORM", "LIGHT SHOCK", "MODERATE SHOCK"]
    Ko = [[1.0, 1.25, 1.50, 1.75], [1.2, 1.4, 1.75, 2.25], [1.3, 1.7, 2.0, 2.75]]
    i = drive.index(sdrive)
    j = load.index(sload)
    return Ko[i][j]

# ARGUMENTS
# m:module[mm]
# RETURN
# The size factor Ks


def agmaKs(m, record=False):
    """"
        Call with ``m`` as the gear module in `mm` and the function will return
        the AGMA shape factor ``Ks``.

        **Example** ``agmaKs(8)`` --> `1.15`
    """
    global CALCRECORD
    import numpy as np
    x = np.array([5.0, 6.0, 8.0, 12.0, 20.0])
    y = np.array([1.0, 1.05, 1.15, 1.25, 1.40])
    z = np.interp(m, x, y)
    if record:
        CALCRECORD = "$K_s(Module=%.0f)=%.2f$" % (m, z)
    return z

# ARGUMENTS
# fw : Face width[mm]
# d: Pitch diameter[mm]
# gearbox: The application type ("Open", "Commercial enclosed units", etc.)


def _agmaKm(fw, d, gearbox, record=False):
    global CALCRECORD
    if record:
        CALCRECORD = ""
    F = fw/25.4
    Dp = d/25.4
    if Dp < 0.0001:
        return 1.e6
    # Load distribution factor
    if (F < 1.0):
        Cpf = F/(10*Dp)-0.025
        CALCRECORD = "$C_{pf}=\\frac{%.0f/25.4}{10%.0f/25.4}-0.025$=%.4f" % (
            fw, d, Cpf)
    else:
        Cpf = F/(10*Dp)-0.0375+0.0125*F
        CALCRECORD = "$C_{pf}=\\frac{%.0f}{10\\times%.0f}-0.0375+0.0125\\frac{%.0f}{25.4}$=%.4f\n" % (
            fw, d, fw, Cpf)
#        print ("Cpf=%f"%Cpf)
    applic_type = {"open gearing": 0, "commercial enclosed units": 1,
                   "precision": 2, "extra precision": 3}
    k = applic_type[gearbox.lower()]
    C0 = [0.247,   0.127,  0.0675, 0.0380]
    C1 = [0.0167,  0.0158, 0.0128, 0.0102]
    C2 = [-0.765,  -1.093, -0.926, -0.822]
    Cma = C0[k]+C1[k]*F+C2[k]*1.0e-4*F*F
    CALCRECORD += "$C_{ma}=%.4f+%.4f\\frac{%.0f}{25.4}%.4f\\times10^{-4}(\\frac{%.0f}{25.4})^2=%.4f\
$\n" % (C0[k], C1[k], fw, C2[k], fw, Cma)
    Km = (1.0+Cpf+Cma)
    CALCRECORD += "$K_m=1.0+%.4f+%.4f=%.2f$" % (Cpf, Cma, Km)
#        print("Cma=%f"%Cma)
    return Km


def agmaKm(fw, d, gearbox, record=False):
    """
        Call with ``fw`` as the face width in `mm`, ``d`` as the pinion
        diameter in `mm`, and the ``gearbox`` describing the application,
        the function returns the AGMA load distribution factor ``Km``.

        The allowable values for the case-insensitive string ``gearbox`` are

            ``"open gearing"``

            ``"commercial enclosed units"``

            ``"precision"``

            ``"extra precision"``

        **Example** ``agmaKm(80, 160, "commercial enclosed units")`` --> `1.2275`
    """
    if type(fw) == np.ndarray:
        Km = np.zeros(len(fw))
        for i in range(0, len(fw), 2):
            Km[i] = _agmaKm(fw[i], d[i], gearbox, record=False)
            if (i+1) < len(fw):
                Km[i+1] = Km[i]
    else:
        Km = _agmaKm(fw, d, gearbox, record=record)
    return Km


def agmaKB(m, t):  # m: module[mm], t:rim thickness[
    """
        Call with ``m`` as the gear module in `mm` and ``t`` as the rim
        thickness in `mm`.The returned value is
        the AGMA rim thickness factor, ``KB``.

        For solid gear blanks, use the gear pitch radius as the rim
        thickness and the function will return 1.

        The function will return a value less than 1 only when the rim thickness
        is low.  Modern gears can usually be designed to deliver a rim
        thickness factor of 1.0.

        **Example** ``agmaKB(3,25)`` --> `1.0`
    """
    import math
    h = 2.2*m
    mB = t/h
    if mB > 1.2:
        return 1.0
    elif mB > 0:
        return 1.6*math.log(2.242/mB)
    else:
        return 1.6



def agmaKv(agmanumber, vt, record=False):
    """
        Call with ``agmanumber`` as the AGMA quality number (e.g. "A10") and
        ``vt`` as the pitch line linear velocity

            Pitch line velocity[m/s] = angular speed[rad/s] * pitch radius[m]

        The returned value is the AGMA dynamic factor ``Kv``

        **Example** : ``agmaKv("A11", 10)`` --> `1.582`
    """
    global CALCRECORD
    if type(agmanumber) == str:
        n = int(agmanumber[1:])
    else:
        n = agmanumber
    if n < 5:
        return 1.1
    B = 0.25*(n-5.0)**0.667
    C = 3.5637+3.9914*(1-B)
    kv = (C/(C+np.sqrt(vt)))**(-B)
    if record:
        CALCRECORD = "$B=0.25(%.0f-5.0)^{0.667}=%.4f$\n" % (n, B)
        CALCRECORD += "$C=3.5637+3.9914\\times(1-B)=%.4f$\n" % C
        CALCRECORD += "$K_v=\\frac{C}{C+\\sqrt{%.1f}}^{-B}=%.2f$\n" % (vt, kv)
    return kv


# ARGUMENTS:
# Np: Number of teeth on the pinion
# Ng: Number of teeth on the gear
# RETURN
# AGMA Bending Geometry Factor (J) values for the pinion and the gear
def agmaJ(Np, Ng):
    """
        Call with ``Np`` and ``Ng`` as the numbers of teeth for the pinion and
        the gear, respectively.  The returned value is the AGMA Bending Geometry
        Factors, Jp and Jg, for the pinion and the gear, respectively.

        **Example** ``agmaJ(17, 41)``-->> `(0.2890, 0.3891)`
    """
    Jp = J2(Np, Ng)
    Jg = J2(Ng, Np)
    return (Jp, Jg)

# ARGUMENTS:
# Np: Number of teeth on the pinion
# Ng: Number of teeth on the gear
# RETURN
# AGMA Contact Geometry Factor (I) (the same for the pinion and the gear)


def agmaI(Np, Ng):
    """
        Call with ``Np`` and ``Ng`` as the numbers of teeth for the pinion and
        the gear, respectively.  The returned value is the AGMA Contact Geometry
        Factor, I.  Note that I is the same for the pinion and the gear.

        **Example** ``agmaI(17, 41)``-->> `0.094356`
    """
    import math
    mG = Ng/Np
    phi = 20.0/180*math.pi
    Cc = np.cos(phi)*np.sin(phi)/2*mG/(mG+1)
    C1 = Np*np.sin(phi)/2
    C2 = C1*mG
    C3 = math.pi*np.cos(phi)
    a = np.sqrt((Np+2)**2-(Np*np.cos(phi))**2)
    b = np.sqrt(Np**2-(Np*np.cos(phi))**2)
    C4 = (a-b)*0.5
    Cx = ((C1-C3+C4)*(C2+C3-C4))/(C1*C2)
    return Cc*Cx

# ARGUMENTS:
# NC : Design life in terms of the number of cycles
# HB : Brinell Hardness
# surface = Surface hardness, e.g. "case" or "nitrided"; default is None
# RETURN
# Bending strength life adjustment factor, YN


def agmayn(Nc, HB=400, surface=""):  # Nc:Nof cycles; HB:Brinell; surface:surface hardening
    """
        Call with ``Nc`` as tooth design life in terms of number of cycles, ``HB`` the
        Brinell hardness, and ``surface`` the surface condition.  The default surface
        condition is none; the allowable choices are "nitrided" and "case" (short for case-carburised)

        The returned value is the AGMA Bending Stress cycle factor, YN.

        **Example**
            >>> agmayn(1.e8)
            >>> 0.9767774605590424

    """
    import math
    import numpy as np
    # print(type(Nc))
    if (type(Nc)) == np.ndarray:
        z = np.zeros(len(Nc))
        for i in range(0, len(Nc)):
            z[i] = agmayn(Nc[i], HB, surface=surface)
        return z
    if Nc < 0.001:
        return 0.0
    if Nc > 4e6:
        return 1.3558/Nc**0.0178
    if surface == "case":
        C = 6.1514/1000**0.1192
    elif surface == "nitrided":
        C = 3.517/1000**0.0817
    else:
        y = np.array([2.3194/1000**0.0538, 4.9404 /
                      1000**0.1045, 9.4518/1000**0.148])
        x = np.array([160.0,                250.0,               400.0])
        C = np.interp(HB, x, y)
    m = (C-1.04)/math.log10(1000.0/4.0e6)
    b = C-3*m
    return (m*math.log10(Nc)+b)

# ARGUMENTS:
# NC : Design life in terms of the number of cycles
# HB : Brinell Hardness
# surface = Surface hardness, e.g. "nitrided"; default is None
# RETURN
# Contact strength life adjustment factor, ZN


def agmazn(Nc, surface=""):  # Nc:Nof cycles; surface:surface hardening
    """
        Call with ``Nc`` as tooth design life in terms of number of cycles, ``HB`` the
        Brinell hardness, and ``surface`` the surface condition.  The default surface
        condition is none; the only other choice is "nitrided"

        The returned value is the AGMA Pitting resistance stress cycle factor, ZN.

        **Example**
            >>> agmazn(1.e8)
            >>> 0.9484368889886681

    """
    if (type(Nc)) == np.ndarray:
        z = np.zeros(len(Nc))
        for i in range(0, len(Nc)):
            z[i] = agmazn(Nc[i], surface=surface)
        return z

    if Nc < 4e6:
        if surface == "nitrided":
            return 1.1
        else:
            return 1.5
    if Nc < 1e7:
        if surface == "nitrided":
            return 1.249/Nc**0.0138
        else:
            return 2.466/Nc**0.056
    else:
        return 1.4488/Nc**0.023




#
# SHAFT FUNCTIONS
#
#
def shaftendur(uts, condition="ground"):
    """
        Call with ``uts`` = Tensile strength[MPa] and ``condition`` = a string describing
        the surface condition.  The returned value is the endurance strength
        read off the following chart:

        .. image:: ../../assets/shaftendur.png

        The valid options for the second argument are:

            * ``'ground'`` (default)
            * ``'polished'``
            * ``'cold drawn'``
            * ``'machined'`` (equivalent to ``'cold drawn'`` )
            * ``'hot rolled'``

        **Example**
            >>> shaftendur(900,'hot rolled')
            >>> 212.5

    """
    condition = condition.lower()
    if condition == "ground":
        su = np.array([350, 475, 650, 875, 1050, 1250, 1450, 1500])
        sn = np.array([137, 203, 297, 400, 478,  553,  600,  612])
        return np.interp(uts, su, sn)
    elif condition == "polished":
        return 0.50*uts
    elif condition == "cold drawn" or condition == "machined":
        su = np.array([350, 525, 650, 900, 1075, 1162, 1275, 1450, 1500])
        sn = np.array([137, 200, 249, 325, 375,  400, 425, 450, 429])
        return np.interp(uts, su, sn)
    elif condition == "hot rolled":
        su = np.array([350, 450, 600, 800, 1000, 1250, 1400, 1500])
        sn = np.array([137, 150, 175, 200, 225, 247, 238, 237.5])
        return np.interp(uts, su, sn)
    else:
        print("shaftendur : Surface condition not recognised")

# rel : Desired reliability (for example 0.99)
# Mott Table 5-2


def shaftreliability(rel):
    """
        ``rel`` is the desired target reliability, e.g. 0.10 for 10%

        The returned value is the reliability factor ``CR``

        **Example**
            >>> shaftreliability(0.99)
            >>> 0.81

    """
    if rel > 1:
        sys.exit("SHAFTRELIABILITY error rel=%f" % rel)
    # The reliability factor
    R = [0.5, 0.9, 0.99, 0.999]
    CR = [1.0, 0.90, 0.81, 0.75]
    cr = np.interp(rel, R, CR)
    return cr

# dia: Shaft diameter[mm]


def sizefactor(dia):
    """
        ``dia`` is the shaft diameter in mm

        The returned value is the size factor ``CS`` read off a digitised
        version of the Mott chart Fig 5-9.

        **Example**
            >>> sizefactor(200)
            >>> 0.6964150943396226

    """
    DA = np.array([12.5, 25.0, 50.0, 75.0, 100.0, 150.0, 203.0, 250.0])
    CS = np.array([0.94, 0.875, 0.81, 0.776, 0.755, 0.720, 0.695, 0.68])
    if type(dia) == list or type(dia) == np.ndarray:
        cs = np.array(np.ones(len(dia)))
        for i in range(0, len(dia)):
            if dia[i] >= 8.00:
                cs[i] = np.interp(dia[i], DA, CS)
        return cs
    if dia < 8.00:
        return 1.0
    cs = np.interp(dia, DA, CS)
    return cs

# Shaft functions


def shoulderscfdelta(D, d):
    x = D/d
    if x > 2.0:
        x = 2.0
    deltafit = +(33.78826 * x**8)+(-428.02758 * x**7)+(2360.48676 * x**6)    \
        + (-7400.99264 * x**5)+(14428.18588 * x**4)+(-17907.43776 * x**3)   \
        + (13817.79262 * x**2)+(-6060.73737 * x**1)+(1157.17958 * x**0)
    return deltafit


def shoulderscf(D, d, R, uts, record=False):  # as per AS1403
    """
        Calculates the stress concentration factor for a shaft shoulder according to
        AS1403.

            .. image:: ../../assets/shoulderscf.png


        ``D, d, R`` are the dimensions as shown in the figure above.

        ``uts`` is the tensile strength in MPa.

        The returned value is the stress concentration factor as per AS1403.

        **Example**
            >>> shoulderscf(200,100,10, 450)
            >>> 1.6973600000014022

    """
    global CALCRECORD
    from scipy import interpolate
    if (d > D):
        temp = D
        D = d
        d = temp
    if d == 0:
        CALCRECORD = "Shoulder SCF cannot be computer because shaft diameter is zero."
        return np.inf
#    print("shoulderscf(%.0f,%.0f,%.1f,%.0f)"%(D,d,R,uts))
    x = [400, 500, 600, 800, 900]
    y = [0.50, 0.20, 0.05, 0.0]
    z = [[1.11, 1.075, 1.05, 1.1, 1.15], [1.40, 1.30, 1.30, 1.38, 1.45], [1.88, 1.86, 1.87, 2.1, 2.3],
         [2.52, 2.70, 2.90, 3.4, 3.7]]
    f = interpolate.interp2d(x, y, z, kind='linear')
    delta = shoulderscfdelta(D, d)
    Z = R/d+delta
    K = f(uts, Z)[0]
    if record:
        #         CALCRECORD ="$\\text{Shoulder SCF: }\\Delta=%.3f\\text{; }Z=\\frac{%.1f}{%.1f}+%.3f\\rightarrow%.3f$\
        # "%(delta, R, d, delta, K)
        CALCRECORD = "Shoulder SCF as per AS1403 (d=%.1f mm, D=%.1f mm, r=%.2f mm, Shaft UTS=%.0f MPa): \
\n" % (d, D, R, uts)
        CALCRECORD += "$\\Delta=%.3f\\text{; }Z=\\frac{%.1f}{%.1f}+%.3f\\rightarrow%.3f$\
\n" % (delta, R, d, delta, K)
    return K

# AS1403


def keyseatscf(uts, record=False):
    """

        .. image:: ../../assets/keyseatscf.png

        Calculates the stress concentration factor for a sidemilled keyway with
        a H7/k6 transition fit according to AS1403 Figure 7.  The other keyways
        in the AS1403 chart are not supported by this function.

        The returned value is the stress concentration factor as per Figure 7 of AS1403.

        **Example**
            >>> keyseatscf(650)
            >>> 1.6365625047124999

    """
    global CALCRECORD
    # p=[1.43518519e-08, -2.32539683e-05,   1.45429894e-02,-1.02420635e+00] # for H7/s6 interference fit
    p = [3.79629630e-09, -4.88492063e-06,   2.90687831e-03,
         7.68412698e-01]  # for H7/k6 transition fit
    kt = np.polyval(p, uts)
    if record:
        CALCRECORD = "Keyseat SCF as per AS1403 for a sidemilled key with a H7/k6 transition fit, Shaft UTS=%.0f MPa:\n" % uts
        CALCRECORD += "$%s\\times%.0f^3-%s\\times%.0f^2+%s\\times%.0f+%.4f=%.3f$\
\n" % (engfmt(p[0], p=9, d=4, latex=True), uts, engfmt(-p[1], p=6, d=4, latex=True), uts,
            engfmt(p[2], p=3, d=4, latex=True), uts, p[3], kt)
    return kt

# This is for bearing fit K8/k6 (transition fit)
# AS1403 SCF for a bearing seat (L14/S53)


def bearingscf(uts, record=False):
    """

        .. image:: ../../assets/bearingscf.png

        Calculates the stress concentration factor for a bearing seat with
        a K8/k6 transition fit according to AS1403 Figure 5.  The other bearing
        fit in the AS1403 chart is not supported by this function.

        The returned value is the stress concentration factor as per Figure 5 of AS1403.

        **Example**
            >>> bearingscf(800)
            >>> 2.08896825088

    """
    global CALCRECORD
    # for the bearing fit in the assignment (K8/k6)
    p = [-2.40740741e-09,   6.01587302e-06,  -3.05767196e-03, 1.91753968e+00]
    scf = np.polyval(p, uts)
    if record:
        CALCRECORD = "Bearing SCF : For a K8/k6 fit from AS1403, Shaft UTS=%.0f MPa:\n" % uts
        CALCRECORD += "$-%s\\times%.0f^3+%s\\times%.0f^2-%s\\times%.0f+%.4f=%.3f$\
\n" % (engfmt(-p[0], p=9, d=4, latex=True), uts, engfmt(p[1], p=6, d=4, latex=True), uts,
            engfmt(-p[2], p=3, d=4, latex=True), uts, p[3], scf)
    return scf

# Shrink fit for H7/s6 fit as per AS1403 Figure 6


def shrinkscf(uts, record=False):
    """

        .. image:: ../../assets/shrinkscf.png

        Calculates the stress concentration factor for a component fitted onto a
        shaft using a H7/s6 interference fit, according to Figure 6 of AS1403.
        The other two fits in the AS1403 chart are not supported by this function.

        The returned value is the stress concentration factor as per Figure 6 of AS1403.

        **Example**
            >>> shrinkscf(400)
            >>> 1.6204761921599997

    """
    global CALCRECORD
    p = np.array([-3.61111111e-09,   8.27380952e-06,  -
                  3.95079365e-03, 2.10809524e+00])
    scf = np.polyval(p, uts)
    if record:
        CALCRECORD = "Shrink fit SCF as per AS1403 for H7/s6 fit, Shaft UTS=%.0f MPa:\n" % uts
        CALCRECORD += "$-%s\\times%.0f^3+%s\\times%.0f^2-%s\\times%.0f+%.4f=%.3f$\
\n" % (engfmt(-p[0], p=9, d=4, latex=True), uts, engfmt(p[1], p=6, d=4, latex=True), uts,
            engfmt(-p[2], p=3, d=4, latex=True), uts, p[3], scf)
    return scf


def gearmountscf(gearmount, shaftuts, record=False):
    gmount = gearmount.upper()
    if gmount == "INTEGRAL":
        scf = 1.0
    elif "ONESIDED KEY" in gmount:
        scf = keyseatscf(shaftuts, record=record)
    elif "SHRINK FIT" in gmount:
        scf = shrinkscf(shaftuts, record=record)
    else:
        scf = 1.0
    return scf


def scfa(k1, k2, k3=1, record=False):
    """
        Compute the combined stree concentration factors when two or three
        stress raising features coincide.  The calculation is done as per
        AS1403 Article 8.2 (d) adapted to three features.  The combined the SCF
        is the sum of the largest SCF plus 0.2 times the sum of the two lesser
        values.  For example, if ``k2=max(k1,k2,k3)`` , then the returned value is
        ``k2+0.2*(k1+k3)`` .

        **Example**
            >>> scfa(2.0, 3.0, 4.0)
            >>> 5.0


    """
    global CALCRECORD
    k = sorted(np.array([k1, k2, k3]))
    scf = k[2]
    if record:
        CALCRECORD = "Combined SCF : $%.3f" % k[2]
    if k[1] > 1:
        scf += 0.2*k[1]
        if record:
            CALCRECORD += "+0.2\\times%.3f" % (k[1])
    if k[0] > 1:
        scf += 0.2*k[0]
        if record:
            CALCRECORD += "+0.2\\times%.3f" % (k[0])
    if record:
        CALCRECORD += "$"
    return scf

# Examples for s: H7f4, H3s9
# Only supports 1-digit specs (do not use H11 for example)


def isofits(X=None, d=60.0, s="H7f6"):
    """
        Look up the upper and lower limits for the hole and the shaft for the
        specified fit.  The only fits supported are

        * ``Hxfy`` with ``x`` = 1,2,...,11 and ``y`` =3,4,...,9 and 3 < D <= 250
        * ``Hxsy`` with ``x`` = 1,2,...,11 and ``y`` =3,4,...,9 and 3 < D <=1250

        The data is read from the ``fits`` sheet in the ``shaft.xlsx`` file.

        **Examples**
            >>> isofits(d=60.0, s="H7f6")
            >>> (30, 0, -30, -49)
            >>> isofits(d=60.0, s="H7s6")
            >>> (30, 0, 72, 53)
            >>> isofits(d=110.0, s="H7s6")
            >>> ((35, 0, 101, 79)
            >>> isofits(d=2000.0, s="H7s6")
            >>> SystemExit: isofits: nominal diameter (2000) is too large
    """
    HTABLEFIRSTROW = 4
    fTABLEFIRSTROW = 46
    sTABLEFIRSTROW = 76
    if s[0].upper() != 'H':
        sys.exit(
            "LIBRARY.PY - isofits error.  Unknown Hole fit spec: %s" % s[0])
    if not s[2].lower() in "fs":
        sys.exit(
            "LIBRARY.PY - isofits error.  Unknown shaft fit spec: %s" % s[2])
    if X == None:
        X = opendatafiles(tags=["shaft"])[0]
        X.sheet("fits")
    else:
        X.sheet("fits")
    D = np.array([3, 6, 10, 18, 30, 50, 80, 120, 180, 250, 315, 400,
                  500, 630, 800, 1000, 1250.001])  # Basic sizes for H table
    if d>=1250.0:
        sys.exit("isofits: nominal diameter (%.0f) is too large"%d)
    if d <= D[0]:
        j = 0
    else:
        j = np.where(D <= d)[0][-1]+1
    # print("For d=%.0d, s='%s', j=%d"%(d,s,j))
    irow = HTABLEFIRSTROW+j*2
    jcol = int(s[1])+2
    hupper = int(X.cell(irow, jcol))
    hlower = int(X.cell(irow+1, jcol))
#
    if s[2].lower() == 'f':
        if d>=250.0:
            sys.exit("isofits: nominal diameter (%.0f) is too large"%d)
        D = np.array([3, 6, 10, 18, 30, 50, 80, 120, 180, 250.001])
        if d <= D[0]:
            j = 0
        else:
            j = np.where(D <= d)[0][-1]+1
        irow = fTABLEFIRSTROW+j*2
    else:
        if d>=1250.0:
            sys.exit("isofits: nominal diameter (%.0f) is too large"%d)

        D = np.array([3, 6, 10, 18, 30, 50, 65, 80, 100, 120, 140, 160, 180, 200, 225, 250,
                      280, 315, 355, 400, 450, 500, 560, 630, 710, 800, 900, 1000, 1120, 1250.001])
        if d <= D[0]:
            j = 0
        else:
            j = np.where(D <= d)[0][-1]+1
        irow = sTABLEFIRSTROW+j*2
    jcol = int(s[3])
#    print("For d=%.0d, s='%s', irow=%d, jrow=%d"%(d,s,irow,jcol))
    supper = int(X.cell(irow, jcol))
    slower = int(X.cell(irow+1, jcol))

    return(hupper, hlower, supper, slower)

# Bending Moment Diagram
#   Force units [N]  (for P, Q)
#   Position units [m] (for p, q, c, L)
# Two forces (in two planes): P and Q  [N]  --- numpy arrays
#    P[0]=Py; Q[0]=Qy
#    P[1]=Pz; Q[1]=Qz
# Two supports: B and C
# The origin for positions is B, i.e. b=0
# Positions of other from B: p, q, c
# Length of the beam : L
# x : The positions where we want the shear force and the bending moment values
# The input units are always expected to be newtons and metres
# but the output could be in US units if "metric" is set to False.
# xpos = The array of x-positiyons where we want V and M values


def bmdiagram(P, p=0.5, L=1.0, Q=np.zeros(2), q=0,  cc=[], draw=True, vlim=[], mlim=[], xlim=[],
              xcrit=[], yname='y', zname='z', filename="", fu='N', xu='m', record=False, debug=False):
    """
        This function can be used to draw the shear force and the bending moment
        diagrams and calculate the values of the bending moments in the nominated
        stress points and the reaction forces for a shaft represented as a simply
        supported beam supported by two bearings (B and C) and subject to two
        loads (P and Q) as in the following diagram:

            .. image:: ../../assets/bmdiagram.png

        * ``P`` = [Py, Pz] in newtons
        * ``p`` = Position of the P application point from the left end, m
        * ``Q`` = [Qy, Qz] in newtons
        * ``q`` = Position of the Q application point from the left end, m
        * ``L`` = The distance between the two supports, m

        You do not need to include ``q`` and ``Q`` if there is only one force.
        The other arguments are:

        * ``draw`` : Will draw the shear force and bending moment diagrams if True
        * ``xcrit`` : Will calculate the bending moments at these positions
        * ``filename`` : Will store the diagrams in the image file "filename".png


        **Examples**
            >>> P = np.array([-11280, 31000.0])
            >>> Q = np.array([2860.0,   7860])
            >>> p = 0.185
            >>> q = 0.473
            >>> L = 0.650
            >>> xcrit = np.array([p, q])
            >>> filename='examplebmdiagram'
            >>> (M, B, C) = bmdiagram(P, p, L, Q, q, draw=True,xcrit=xcrit, filename=filename, record=True)

        The above will create the following two image files:

            .. image:: ../../assets/examplebmdiagram_xy.png

            .. image:: ../../assets/examplebmdiagram_xz.png

        and will return

            M = ``array`` ([[ 1348.8,   199.9], [-4498.7, -2574.1]])

            B = ``array`` ([  7290.7, -24317.3])

            C = ``array`` ([  1129.3, -14542.7])

    """
    if type(P) == str and P == "?":
        z = "bmdiagram():\n\n"
        z += 'Call this function as `bmdiagram`(P, p, L, Q, q, draw=(True or False), xcrit=[x$_1$, x$_2$, ...], filename="yourchoice")\n\n'
        z += '* P = [Py, Pz] in newtons\n'
        z += '* p = Position of the P application point from the left end, m\n'
        z += '* Q = [Qy, Qz] in newtons\n'
        z += '* q = Position of the Q application point from the left end, m\n'
        z += '* L = The distance between the two supports, m\n\n'
        z += 'You do not need to include `q` and `Q` if there is only one force.  The \
other arguments are:\n\n'
        z += '* draw : Will draw the shear force and bending moment diagrams if True\n'
        z += '* xcrit : Will calculate the bending moments at these positions\n'
        z += '* filename : Will store the diagrams in the image file "filename".png\n\n'
        return (z)
    import numpy as np
    import matplotlib.pyplot as plt
    global CALCRECORD
    if debug:
        print("(p,L,q,cc)", p, L, q, cc)
    oneplane = (P[1] == 0 and Q[1] == 0)
    if oneplane:
        n = 1
    else:
        n = 2
    if cc == []:
        c = L
    else:
        c = cc
    b = 0
    force_unit = fu
    moment_unit = fu+xu
    x_unit = xu
    B = np.zeros(n)  # y- and-z forces on support B
    C = np.zeros(n)  # y- and-z forces on support C
    if record:
        if cc == []:
            scc = "[]"
        else:
            scc = "%.3f" % cc
        CALCRECORD = "\n\nBMDIAGRAM(P=[%.0f,%.0f],p=%.3f,L=%.3f,Q=[%.0f,%.0f],q=%.3f,cc=%s)\n\n"\
            % (P[0], P[1], p, L, Q[0], Q[1], q, scc)
    xpos = np.array([b, c, p, q])
    if debug:
        print("xpos =", xpos)
    if record:
        CALCRECORD += "\nxcrit array: "
    if xcrit == []:
        xcrit = xpos
        if record:
            CALCRECORD += "xcrit unspecified.  Calculate for "
    if record:
        for i in range(0, len(xcrit)):
            CALCRECORD += "%.3f, " % xcrit[i]
        CALCRECORD += " m \n\n"
    Mcrit = np.array([np.zeros(len(xcrit)), np.zeros(len(xcrit))])
    # This sorting is neccesary because the force is sometimes
    ix = np.argsort(xpos)
    # outside the bearing span (e.g. the belt force in hdmixer)
    x = xpos[ix]
    if debug:
        print("x=", x)
    F = np.zeros([n, len(xpos)])
    # print("(P, p)=([%.0f,%.0f], %.3f);(Q,q)=([%.0f,%.0f],%.3f); b=%.3f; c=%.3f"\
    #    %(P[0],P[1],p,Q[0],Q[1],q,b,c))

    for k in range(0, n):  # k:(0,1) --> (y, z)
        C[k] = -((p-b)*P[k]+(q-b)*Q[k])/(c-b)
        B[k] = -P[k]-Q[k]-C[k]
        if record:
            CALCRECORD += "\nRight(R) and Left(L) Bearing forces on %s plane:\n\n" % (
                ["x-y", "x-z"][k])
            sr = "R%s=$-\\frac{(p-b)P_%s+(q-b)Q_%s}{c-b}=\
-\\frac{(%.0f-%.0f)(%.0f)+(%.0f-%.0f)(%.0f)}{%.0f-%.0f}=%.0f$\n\n"
            fstr = ["y", "z"][k]
            if xu == 'm':
                CALCRECORD += sr % (fstr, fstr, fstr, p*1000, b*1000,
                                    P[k], q*1000, b*1000, Q[k], c*1000, b*1000, C[k])
            else:
                CALCRECORD += sr % (fstr, b, p, P[k], p, q, Q[k], b, c, C[k])
            CALCRECORD += "L%s=$-P_%s-Q_%s-R_%s=-(%.0f)-(%.0f)-(%.0f)=%.0f$\
\n\n" % (fstr, fstr, fstr, fstr, P[k], Q[k], C[k], B[k])
        F[k] = np.array([B[k], C[k], P[k], Q[k]])
        f = F[k][ix]
        fv = [f[0], f[0]+f[1], f[0]+f[1]+f[2], f[0]+f[1]+f[2]+f[3]]
        xv = [x[0], x[0], x[1], x[1], x[2], x[2], x[3],  x[3]]
        v = [0,  fv[0], fv[0], fv[1], fv[1], fv[2], fv[2], fv[3]]
        xm = [xv[0], xv[2],     xv[4], xv[6]]  # Positions for moment plot
        mm = [0, 0, 0, 0]  # Moment values
        mm1 = fv[0]*(xm[1]-xm[0])
        mm2 = mm1+fv[1]*(xm[2]-xm[1])
        mm3 = mm2+fv[2]*(xm[3]-xm[2])
        mm = [0, mm1, mm2, mm3]
        for i in range(0, len(xcrit)):
            Mcrit[k][i] = np.interp(xcrit[i], xm, mm)
        if draw:
            fig = plt.figure(k)
            plt.clf()
            ax = fig.add_subplot(211)
            plt.plot(xv, v, 'k', linewidth=2)
            dy = abs(max(fv)-min(fv))/30
            plt.text((x[0]+x[1])/2, fv[0]+dy, '%.1f' % fv[0], fontsize='small')
            plt.text((x[2]+x[1])/2, fv[1]+dy, '%.1f' % fv[1], fontsize='small')
            plt.text((x[2]+x[3])/2, fv[2]+dy, '%.1f' % fv[2], fontsize='small')
            plt.grid()
            plt.ylabel('V, %s' % force_unit)
            plt.title("x-%s plane" % ([yname, zname][k]))
            if len(vlim) > 0:
                ax.set_ylim(vlim[k, 0], vlim[k, 1])
            if len(xlim) > 0:
                ax.set_xlim(xlim[0], xlim[1])
            ax = fig.add_subplot(212)
            plt.plot(xm, mm, 'k', linewidth=2)
            plt.grid()
            plt.xlabel('Position, %s' % x_unit)
            plt.ylabel('BM, %s' % moment_unit)
            if len(mlim) > 0:
                ax.set_ylim(mlim[k, 0], mlim[k, 1])
            if len(xlim) > 0:
                ax.set_xlim(xlim[0], xlim[1])
            # Calculate the Mxy and Mxz at the critical points:
            for i in range(0, len(xcrit)):
                plt.plot(xcrit[i], Mcrit[k][i], 'o', color='k')
#
            if filename != "":
                plt.savefig('%s_x%s.png' % (filename, [yname, zname][k]))
                plt.close()
            if filename == "":
                plt.show()
    if record:
        if c < 1:
            CALCRECORD += "\n\n* Stress point locations [mm] = "
        else:
            CALCRECORD += "\n\n* Stress point locations [m] = "
        for i in range(0, len(xcrit)):
            if c > 1:
                CALCRECORD += "%6.0f, " % (xcrit[i])
            else:
                CALCRECORD += "%.0f, " % (1000*xcrit[i])
        #
        CALCRECORD += "\n* BMZ (x-y plane) [N-m] = "
        for i in range(0, len(xcrit)):
            CALCRECORD += " %6.0f," % (Mcrit[0][i])
    #    CALCRECORD=CALCRECORD[:-1]+" %s\n"%(fu+xu)
        #
        CALCRECORD += "\n* BMY (x-z plane) [N-m] = "
        for i in range(0, len(xcrit)):
            CALCRECORD += "%6.0f," % Mcrit[1][i]
        CALCRECORD += "\n"
#    CALCRECORD=CALCRECORD[:-1]+" %s\n"%(fu+xu)
    if oneplane:
        Mcrit = Mcrit[0]
        B = B[0]
        C = C[0]
    #
    return (Mcrit, B, C)


if False:
    P = np.array([-11280, 31000.0])
    Q = np.array([2860.0,   7860])
    p = 0.185
    q = 0.473
    L = 0.650
    xcrit = np.array([p, q])
#    filename='examplebmdiagram'
    filename = ""
    (M, B, C) = bmdiagram(P, p, L, Q, q, draw=True,
                          xcrit=xcrit, filename=filename, record=True)
# Bearing functions:
# ARGUMENTS:
# F = np.array([LB, RB]) with LB/RB as left/right bearing total radial force(kN)
# ncycles = Bearing design life desired at F (cycles)
# xb = Xcel pointer to the bearing data file
# cr = Reliability factor; default=1 (L10 or 90% reliability)
# dmin = np.array([LDmin,RDmin]) The minimum bore diameter, mm , for left and right


def bearingpick(F, ncycles, xb=None, cr=1.0, dmin=np.array([0, 0]), record=False):
    """
        This function selects suitable deep groove ball bearings for a shaft
        supported by two bearings.  It picks the first bearing that satisfies
        the requirements in the ``metric`` sheet of the bearing data file, ``bearing.xlsx``

        The function returns a ``dictionary`` variable with the fields as defined
        in the examples below.

        The arguments to the function are:

            ``F`` [kN] : The radial load(s). Could be one single force or
            a numpy array ``[FL, FR]`` where ``FL`` and ``FR`` are the total
            radial forces on the left and right bearings

            ``ncycles`` : Required life as number of cycles

            *** Optional Arguments *** :

            ``xb`` : Pointer to the bearing data Excel file
            (if a different file with the same format but different data is to be used)

            ``cr`` : Reliability factor. The default is 1, corresponding to an
            L10 life or 90% reliability

            ``dmin`` [mm]  Minimum bore diameters, reflecting the strength
            requirement that the shaft segment diameters on the left and right
            support points cannot be less than these specified values.  The minimum
            of the two dmin values are used.  The argument can be a single number or
            a numpy array.  The default value is 0  indicating no diameter requirement.

        **Examples**
            >>> bearingpick(120, 2.e6)
            >>> {'no': 6319,        # Bearing number
                 'bore': 95,        # Bore diameter, mm
                 'C': 153,          # Dynamic rating, kN
                 'rmax': 2.5,       # Maximum fillet radius
                 'dmin': 108,       # Minimum shaft shoulder diameter, mm
                 'dmax': 187,       # Maximum shaft shoulder diameter, mm
                 'mass': 5.65,      # Bearing mass, kg
                 'width': 45,       # Bearing width, mm
                 'req': 151.2,      # Required rating (calculated using F and ncycles )
                 'constraint':'Load' # Would be 'Dmin' if the choice were based on diameter
                 'Co': 118          # Static rating

            >>> bearingpick(120, 2.e6, dmin=105
            >>> {'no': 6226,
                 'bore': 130,
                 'C': 156,
                 'rmax': 2.5,
                 'dmin': 143,
                 'dmax': 217,
                 'mass': 5.8,
                 'width': 40,
                 'req': 151.19052598738477,
                 'constraint': 'Dmin',
                 'Co': 132}

    """
    global CALCRECORD
    if not (type(F) == list or type(F) == np.ndarray):
        F = np.array([F, 0])
    # if xb == None:
    #     xb = Xcel("data\\bearing.xlsx", sheetname="metric")
    # else:
    #     xb.sheet("metric")
    if xb == None:
        xb = opendatafiles(tags=["bearing"])[0]
        xb.sheet("metric")
    else:
        xb.sheet("metric")
    Pd = np.max(np.abs(F))
    C = Pd*(ncycles/(cr*1.e6))**(1.0/3)
    d = np.min(dmin)
    if record:
        CALCRECORD += "bearingpick([%.1f,%.1f] kN, %.0f cycles, dmin=%.0f mm)==> C=%.2f\n\n" % (
            F[0], F[1], ncycles, d, C)
    constraint = "Load"
    for irow in range(7, 1+xb.maxrow()):
        rating = xb.cell(irow, 8)
        bore = xb.cell(irow, 4)
        CALCRECORD += "%03d. C=%.0f, D=%.0f " % (irow, rating, bore)
        if rating >= C:
            if bore < d:
                constraint = "Dmin"
                continue
            bearingnumber = xb.cell(irow, 3)
            bore = xb.cell(irow, 4)
            width = xb.cell(irow, 6)
            Co = xb.cell(irow, 7)
#            C=xb.cell(irow,8)
            rmax = xb.cell(irow, 9)
            dmin = xb.cell(irow, 10)
            dmax = xb.cell(irow, 11)
            mass = xb.cell(irow, 12)
            bearing = {"no": bearingnumber, "bore": bore, "C": rating, "rmax": rmax,
                       "dmin": dmin, "dmax": dmax, "mass": mass, "width": width,
                       "req": C, 'constraint': constraint, 'Co': Co}
            return bearing
        else:
            CALCRECORD += "-- skip\n\n"
    return {"no": 0, "bore": 0, "C": 0, "Co": 0, "rmax": 0, "dmin": 0, "dmax": 0, "mass": 0, "width": 0, "rating": rating}


def bearingdims(xb, bnum, name):
    if xb == None:
        xb = Xcel("bearing.xlsx", sheetname="metric")
    else:
        xb.sheet("metric")

    dims = {'bore': 4, 'width': 6, "od": 5, "dmin": 10, "dmax": 11, "rmax": 9,
            "mass": 12, "C": 8, "Co": 7}
    xb.sheet("metric")
    return xb.vir(bnum, dims[name])

# r: Desired reliabilityy, e.g. 0.99 for 99%
# RETURN:
# KR: Reliability factor


def bearingrel(r):
    """
        The bearing reliability factor corresponding to the desired reliability

        ``r`` is the desired reliability, e.g. 0.90 for an L10 life.

        **Examples**
            >>> bearingrel(0.99)
            >>> 0.21

    """
    import numpy as np
    if r > 1:
        r = r/100
    R = [0.9, 0.95, 0.96, 0.97, 0.98, 0.99]
    K = [1.0, 0.62, 0.53, 0.44, 0.33, 0.21]
    Kr = np.interp(r, R, K)
    return Kr


def dgbbrtfacs(e=None, TC=None, Y=None):
    """
        This function is used in selection of a bearing subject to both radial
        and thrust loads.  As you will see in the lectures, this is an iterative
        process and this function can be called repeatedly in search of a solution.

        The function always returns a tuple with three components (e, TC, Y), one the same as
        the supplied value and the other two computed by the function.
        There are three arguments and only one should be specified.

        ``e`` is specified.  The function computes the values of T/Co and Y from the
        bearing thrust factors table (e.g. Mott Table 14-5)

        ``TC`` (representing T/Co) is specified.  The function computes e and Y

        ``Y`` is specified.  The function computes T/Co and e

        **Examples**
            >>> dgbbrtfacs(e=0.27)
            >>> (0.27, 0.07, 1.63)
            >>> dgbbrtfacs(TC=0.027)
            >>> (0.218, 0.027, 2.01)
            >>> dgbbrtfacs(Y=1.15)
            >>> (0.38, 0.28, 1.15)
    """
    ea = np.array([0.19, 0.22, 0.26, 0.28, 0.30, 0.34, 0.38, 0.42, 0.44])
    TCa = np.array([14, 28, 56, 84, 110, 170, 280, 420, 560])/1000
    Ya = np.array([2.30, 1.99, 1.71, 1.55, 1.45, 1.31, 1.15, 1.04, 1.0])
    if e != None:
        a = np.where(ea == e)
        if len(a) > 0 and len(a[0]) > 0:
            TC = TCa[a[0][0]]
            Y = Ya[a[0][0]]
        else:
            TC = np.interp(e, ea, TCa)
            Y = np.interp(e, ea, Ya)
    elif TC != None:
        a = np.where(TCa == TC)
        if len(a) > 0 and len(a[0]) > 0:
            j = a[0][0]
            (e, Y) = (ea[j], Ya[j])
        else:
            e = np.interp(TC, TCa, ea)
            Y = np.interp(TC, TCa, Ya)
    elif Y != None:
        a = np.where(Ya == Y)
        if len(a) > 0 and len(a[0]) > 0:
            j = a[0][0]
            (e, TC) = (ea[j], TCa[j])
        else:
            e = np.interp(Y, Ya, ea)
            TC = np.interp(Y, Ya, TCa)

    return (e, TC, Y)

# metric key sizes
# d = Shaft diameter in mm
# Returns W and H of the parallel key for this shaft diameter
# Data from Mott Table 11-1, which is DIN6885, T1 data (I checked it against
# Roloff/Matek, Tabellenbuch, TB12-2)


def keysize(d):
    """
        Returns a tuple (width,height) for the specified diameter, d[mm] as per
        DIN6885, T1 (and also Table 11-1 in Mott).

        **Examples**

        >>> keysize(20)
        >>> (6, 6)
        >>> keysize(120)
        >>> (32, 18)
    """
    D = np.array([8, 10, 12, 17, 22, 30, 38, 44, 50, 58, 65, 75, 85, 95,
                  110, 130, 150, 170, 200, 230, 260, 290, 330, 380, 440, 500])
    W = np.array([2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 56,
                  63, 70, 80, 90, 100])
    H = np.array([2, 3, 4, 5, 6, 7, 8, 8, 9, 10, 11, 12, 14, 14, 16, 18, 20, 22, 25, 28, 32, 32,
                  36, 40, 45, 50])
    j = np.where(D >= d)[0]
    if len(j) > 0:
        j = j[0]
    else:
        j = len(W)-1
    return(W[j], H[j])

# ARGUMENTS
# m - Gear module, mm
# Np - Pinion toth number  (on the intermediate shaft)
# Ng - Gear tooth number (on the load shaft)
# Ni - Idler (the idler is between the pinion and the gear) tooth number
# s - The distance between pinion and gear centers, mm
# beta - The angle PINION-IDLER centre line makes with the vertical, degrees
# NA - Number of teeth on the input gear on the input (motor) shaft
# NB - Number of teeth on the gear on the intermediate shaft (NA drives NB)


def plotidler(m, Np, Ng, Ni, beta, NA, NB, filename=""):
    import matplotlib.pyplot as plt
    plt.clf()
    Rp = m*Np/2
    Rg = m*Ng/2
    Ri = m*Ni/2
    ci = m*(Np+Ni)/2  # Centre distance for Gear C and the Idler
    di = m*(Ng+Ni)/2  # Centre distance for Gear D and the Idler
    xi = (Rp+Ri)*math.sin(beta/180*PIE)
    yi = (Rp+Ri)*math.cos(beta/180*PIE)
    s = max(np.roots([1, -2*ci*math.cos(beta/180*PIE), ci*ci-di*di]))

    pinion = plt.Circle((0, 0), Rp, color='k', fill=False)
    gear = plt.Circle((0, s), Rg, color='k', fill=False)
    idler = plt.Circle((-xi, yi), Ri, color='b', fill=False)
    gearB = plt.Circle((0, 0), m*NB/2, color='y', linestyle='--', fill=False)
    gearA = plt.Circle((0, -m*(NA+NB)/2), m*NA/2, color='y',
                       linestyle='--', fill=False)
    ax = plt.gca()
    ax.cla()  # clear things for fresh plot
    ax.set_ylim((-m*(NA*2+NB)/2, Rg+s))
    ax.set_xlim((-xi-Ri, m*NB/2))
    dr = 0.1*Rp
    lw = 0.5
    ax.add_artist(pinion)
    ax.add_artist(gear)
    ax.add_artist(idler)
    ax.add_artist(gearB)
    ax.add_artist(gearA)
    plt.plot([0, 0], [-1.1*Rp, s+Rg+0.1*Rp],  'k-.', linewidth=lw)
    plt.plot([-1.1*Rp, 1.1*Rp], [0, 0], 'k-.', linewidth=lw)
    plt.plot([-xi-Ri-0.1*Rp, -xi+Ri+0.1*Rp], [yi, yi], 'b-.', linewidth=lw)
    plt.plot([-xi, -xi], [yi-Ri-dr, yi+Ri+dr], 'b-.', linewidth=lw)
    plt.plot([-Rg-dr, Rg+dr], [s, s], 'k-.', linewidth=lw)
    # plt.plot([0, -xi],[0, yi], color='r')
    #plt.text(-xi, yi, "(%.1f, %.1f)"%(-xi, Rp+yi))
    plt.grid(color='0.5', linestyle='--', linewidth=0.1)
    plt.xlabel('mm')
    plt.ylabel('mm')
    (dx, dy) = (5, 5)
    plt.text(dx, dy, "C"),
    plt.text(dx, s+dy, "D")
    plt.title("Np=%d, Ng=%d, Ni=%d" % (Np, Ng, Ni), fontsize=10)
#    plt.show()
    if filename == "":
        plt.show()
    else:
        plt.savefig(filename)
        plt.show()
# plotidler(5,17,54,29,30, 17,53)  # Data for the 2020 example file (0.xlsx)
#

# Miscellaneous
#
# STRESS CONCENTRATION FACTORS:
# The following is for the same geometry as that in shoulderscf(D, d, R, uts)
# However, this one is for an axial load it is also not adjusted for the UTS
# as in the AS1403 chart


def scf_roundbartension(D, d=10, r=1):  # used to be scf_shaft_with_shoulder
    """
        The stress concentration factor for a stepped round bar in tension

        .. image:: ../../assets/scf_roundbartension.png

        ``D, d, r`` are the dimensions as in the figure above in mm.

        **Example**
            >>> scf_roundbartension(200, 100, 10)
            >>> 1.964

    """

    if D == "?":
        return("scf_roundbartension(D, d, r) $\\rightarrow$ SCF\n\n")
    t = (D-d)/2.0
    y = t/r
    yq = math.sqrt(y)
    if y >= 0.1 and y <= 2.0:
        C1 = 0.926+1.157*yq-0.099*y
        C2 = 0.012-3.036*yq+0.961*y
        C3 = -0.302+3.977*yq-1.744*y
        C4 = 0.365-2.098*yq+0.878*y
    elif y > 2.0 and y <= 20.0:
        C1 = 1.200+0.860*yq-0.022*y
        C2 = -1.805-0.346*yq-0.038*y
        C3 = 2.198-0.486*yq+0.165*y
        C4 = -0.593-0.028*yq-0.106*y
    p = np.array([C4, C3, C2, C1])
    x = 2*t/D
    Kt = np.polyval(p, x)
    return Kt


# Stepped shaft subject to torsion (Peterson Chart 3.12)
Peterson_3_12 = np.array([[0.905, 0.783, -0.075], [-0.437, -1.969, 0.553],
                          [1.557, 1.073, -0.578], [-1.061, 0.171, 0.086]])

# The following function is based on the coefficients in Paterson Stress Charts
# Chart 3.10, p 165


def scf_roundbarbending(D, d=10, r=1):  # used to be scf_roundbar_bending(d,D,R)
    if D == "?":
        return("scf_roundbarbending(D, d, r) $\\rightarrow$ SCF\n\n")
    import math
    t = (D-d)/2.0
    y = t/r
    yq = math.sqrt(y)
    if y >= 0.1 and y <= 2.0:
        C1 = 0.947+1.206*yq-0.131*y
        C2 = 0.022-3.405*yq+0.915*y
        C3 = 0.869+1.777*yq-0.555*y
        C4 = -0.810+0.422*yq-0.260*y
    elif y > 2.0 and y <= 20.0:
        C1 = 1.232+0.832*yq-0.008*y
        C2 = -3.813+0.968*yq-0.260*y
        C3 = 7.423-4.868*yq+0.869*y
        C4 = -3.839+3.070*yq-0.600*y
    p = np.array([C4, C3, C2, C1])
    x = 2*t/D
    Kt = np.polyval(p, x)
    return Kt


# Mohr Circle
def mohrcircle(sx, sy, txy, filename="None", figno=1, title="2d Mohr's Circle"):
    """
        For the 2d stress element:
            .. image:: ../../assets/stresselement.png

        This function returns the two principal stresses and the maximum shear
        stress as (s1, s2, taumax) in MPa.

        The arguments ``sx, sy, txy`` are as in the figure.

        If a filename is provided, the Mohr's circle is drawn into that file.

        Otherwise, it is drawn on the screen.

        The ``figno`` and ``title`` are optional.

        **Example**

        >>> mohrcircle(10,-4,5,filename="mohrcircle.png", title="melib example")
        >>> (11.60, -5.602, 8.602)

        .. image:: ../../assets/mohrcircle.png

    """
    if sx == "?":
        z = "Call as mohrcircle(sx=$\\sigma_x$, sy=$\\sigma_y$, txy=$\\tau_{xy}$,\
filename='yourchoice.png', title='your choice')"
        return z
    import math
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    R = math.sqrt(((sx-sy)/2.0)**2+txy*txy)
    s1 = (sx+sy)/2+R
    s2 = (sx+sy)/2-R
    draw_circle = not (filename == "None")
    # Plot axes
    ascale = 2
    xmin = s2-R/ascale
    xmax = s1+R/ascale
    ymin = -ascale*R
    ymax = ascale*R
    amin = min(xmin, ymin)
    amax = max(xmax, ymax)
    dx = xmax-xmin
    dy = ymax-ymin
    textstart = amin+dx/100
    if draw_circle:
        (fig, ax) = openplot(figno, aspect=1.0)
        mohr = plt.Circle(((s1+s2)/2, 0), R, color='k',
                          fill=False, linewidth=2.0)
        ax = plt.gca()
        ax.cla()  # clear things for fresh plot
        ax.set_xlim(amin, amax)
        ax.set_ylim(amin, amax)
        ax.plot([amin, amax], [0, 0], 'k', linewidth=2.0)  # x axis
        ax.plot([0, 0], [amin, amax], 'k', linewidth=2.0)  # y axis
        ax.plot(sx,        txy, 'o', color='k')
        ax.plot(sy,       -txy, 'o', color='k')
        ax.plot([(s1+s2)/2, sx], [0, txy], 'b',
                linewidth=1.0)  # Radius of the circlem
        ox = (s1+s2)/2
        ax.plot(ox, 0.0, '+', color='b')
        plt.gca().add_artist(mohr)
        matplotlib.pyplot.text(s1, -dy/12, '%.0f' % s1)
        matplotlib.pyplot.text(s2-dx/8, -dy/12, '%.0f' % s2)
        seff = math.sqrt((s1**2+s2**2+(s1-s2)**2)/2)
        plt.title(title)
        matplotlib.pyplot.text(textstart, amax*0.9, 'R=%.2f' % R)
        matplotlib.pyplot.text(textstart, amax*0.7,
                               '$\\sqrt{{\\sigma_1^2+\\sigma_1^2-(\\sigma_1^2-\\sigma_2^2)}}$=%.2f' % seff)
        plt.grid()
        if filename != "":
            plt.savefig(filename)
        else:
            plt.show()
    return (s1, s2, R)
# mohrcircle(filename="")

def testing(funcname):
    if funcname=='bmdiagram':
        # Lecture 16
        # P=np.array([-11280,31000])
        # Q=np.array([2860,7860])
        # p=0.185
        # q=p+0.288
        # L=p+q+0.177
        # Sheave and Gear Example
        # P=np.array([-10,0])
        # Q=np.array([-20,0])
        # p=-1
        # q=2.0
        # L=5.0
        # c=4.0
        # hdmixer Shaft #1
        P = np.array([-2238, 830])
        Q = np.array([-1170, -3215])
        p = -0.048  # ((0+45)/2-(45+95)/2)/1000
        q = 0.157   # ((95+359)/2-(45+95)/2)/1000
        L = 0.314   # ((359+409)/2-(45+95)/2)/1000
        xcrit = np.array([-0.025, 0.025, 0.157, 0.289])
        # (Mcrit,B,C)=bmdiagram(P,p,L,Q,q,draw=True,xcrit=np.array([-0.02,0.05,0.15,0.25]))
    #    (Mcrit,B,C)=bmdiagram(P,p,L,draw=True,Q=Q, q=q, xcrit=xcrit,record=True)
        (Mcrit, B, C)=bmdiagram(P, p, L, Q=Q, q=q, draw=True, xcrit=xcrit)
        print(">>> bmdiagram(np.array([-2238,830]), -0.048, 0.314, Q=np.array([-1170,-3215]),q=0.157,draw=True,xcrit=np.array([-0.02,0.05,0.15,0.25]))  # returns \n")
        print("Mcrit : ", Mcrit)
        print("B : ", B)
        print("C : ", C)

    if funcname == "bearingpick":
        L10 = 3654*1e6
        F = np.array([4684, 4684])
        L10 = 11571e6
        F = np.array([8000, 5000])
        bearing = bearingpick(F/1000, L10, dmin=np.array([35, 35]))
        print("bearingpick(np.array([8,5], 11571e6, dmin=np.array([35, 35]))) --> ", end="")
        print(bearing)
    if funcname == "isofits":
        d = 40
        s = "H7f6"
        (hupper, hlower, supper, slower) = isofits(None, d, s)
        print("For a basic size of d=%.0f and '%s' fit:" % (d, s))
        print("Hole : %d,%d" % (hupper, hlower))
        print("Shaft: %d,%d" % (supper, slower))
    if funcname=="alloyprop":
        [su, sy, rho]=alloyprop(None, "nickel", "N06110", ["SUMPA", "SYMPA", "RHO"])
        print('alloyprop(None, "nickel", "N06110", ["SUMPA", "SYMPA", "RHO"]) :')
        print(su,sy,rho)
    if funcname=="fixity":
        Ka=fixity("pinned-fixed")  # Actual value For pinned-fixed ends
        Ki=fixity("pinned-fixed", ideal=True)  # Ideal value For pinned-fixed ends
        print("fixity('pinned-fixed') --> %.2f"%Ka)
        print("fixity('pinned-fixed', ideal=True) --> %.2f"%Ki)
    if funcname=="weldsize":
        print('>>> weldsize(18.0) # returns %.2f mm'%(weldsize(18.0)))
    if funcname=="alumweldstrength":
        print(">>>alumweldstrength(6061, 5356) # returns %.2f MPa"%(alumweldstrength(6061, 5356)))
    if funcname=="ec3cutoff":
        print(">>> ec3cutoff(%d)  # returns %.0f MPa"%(71, ec3cutoff(71)))
    if funcname=="ec3life":
        x=ec3life(120.0, 1.2, joint='N')
        print(">>> ec3life(120.0, 1.2, joint='N')   # returns (%.0f,%.0f,%.0f) cycles"%
                 (x[0],x[1],x[2]))
        
        


# General Physics
class Phasor:
    p = 0  # Phasor is a complex number
    dig = 3  # Number of digits in float display
    showpolar = True  # The default print is polar format

    def __init__(self, ra=None, xy=None):
        if xy == None:  # This means the magnitude and the angle are specified
            self.p = cmath.rect(ra[0], ra[1]/180*PIE)
        else:
            self.p = complex(xy[0], xy[1])

    def ra(self):
        r = cmath.polar(self.p)
        return (r[0], r[1]*180.0/PIE)

    def xy(self):
        return (self.p.real, self.p.imag)

    def cnum(self):
        return self.p

    def conj(self):
        (realpart, imagpart)=self.xy()
        return Phasor(xy=[realpart, -imagpart])

    def __add__(self, other):
        xy = self.cnum()+other.cnum()
        return Phasor(xy=(xy.real, xy.imag))

    def __sub__(self, other):
        xy = self.cnum()-other.cnum()
        return Phasor(xy=(xy.real, xy.imag))

    def __mul__(self, other):
        xy = self.cnum()*other.cnum()
        return Phasor(xy=(xy.real, xy.imag))

    def __truediv__(self, q):
        xy = self.cnum()/q.cnum()
        return Phasor(xy=(xy.real, xy.imag))

    def __str__(self, showpolar=True, dig=-1):
        if dig>=0: self.dig=dig
        sf = "{:.%df}" % (self.dig)
        self.showpolar=showpolar
        if self.showpolar:
            ra = self.ra()
            return sf.format(ra[0])+"<"+sf.format(ra[1])
        else:
            c = self.cnum()
            return sf.format(c.real)+"+j("+sf.format(c.imag)+")"

    def test():
        sqrt2 = np.sqrt(2)
        p = Phasor(ra=(sqrt2, 45))
        q = Phasor(ra=(sqrt2, 45))
        # pq = p.sum(q)
        print(p.cnum())
        print("p+q=", p.add(q).cnum())
        print("p*q=", p.mult(q).cnum())
        print("p/q=", p.div(q).cnum())

def delta():
    XT=0.3+0.15+0.325
    P=0.9
    sindelta=P*XT
    delta=np.arcsin(sindelta)/PIE*180
    return delta

def ef():
    Et=Phasor(ra=[1.0,0.0])
    It=Phasor(ra=[1, -36.0])
    Xd=Phasor(ra=[0.3,90])
    Ef=Et+It*Xd
    print("Ef = ", Ef)
def It():
    Ef=Phasor(ra=[1,44.226])
    EB=Phasor(ra=[1,0.0])
    Xd=Phasor(ra=[0.775,90.0])
    It=(Ef-EB)/Xd
    print("It(E,EB,Xd)=", It)
    return It
def Et():
    Ef=Phasor(ra=[1,42.45])
    It=Phasor(ra=[2.41, 21.225])
    Xd=Phasor(ra=[0.3,90.0])
    Et=Ef-Xd*It
    print("Et(Ef,It,Xd)=", Et)

def libraryver():
    return "4:17pm 3 June 2021"