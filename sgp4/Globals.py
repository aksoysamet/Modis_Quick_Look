import math
PI = 3.141592653589793
TWOPI = 2.0 * PI
RADS_PER_DEG = PI / 180.0

GM = 398601.2  
GEOSYNC_ALT = 42241.892 
EARTH_RAD = 6370.0    
EARTH_DIA = 12800.0   
DAY_SIDERAL = (23 * 3600) + (56 * 60) + 4.09
DAY_24HR = (24 * 3600)

AE = 1.0
AU = 149597870.0
SR = 696000.0
TWOTHRD = 2.0 / 3.0
XKMPER = 6378.135
F = 1.0 / 298.26
GE = 398600.8
J2 = 1.0826158E-3
J3 = -2.53881E-6
J4 = -1.65597E-6
CK2 = J2 / 2.0
CK4 = -3.0 * J4 / 8.0
XJ3 = J3
E6A = 1.0e-06
QO = AE + 120.0 / XKMPER
S = AE + 78.0  / XKMPER
MIN_PER_DAY = 1440.0
SEC_PER_DAY = 86400.0
OMEGA_E = 1.00273790934
XKE = math.sqrt(3600.0 * GE / (XKMPER * XKMPER * XKMPER))
QOMS2T = math.pow((QO-S),4)

def Fmod2p(arg):
    global TWOPI
    modu = arg % TWOPI
    if modu < .0:
        modu += TWOPI
    return modu

def sqr(x):
    return x*x

def AcTan(sinx, cosx):
    global PI
    if cosx == .0:
        if sinx > .0:
            return PI / 2.
        else:
            return 3. * PI / 2.
    elif cosx > .0:
        return math.atan(sinx / cosx)
    else:
        return PI + math.atan(sinx / cosx)

def rad2deg(r):
    global PI
    DEG_PER_RAD = 180.0 / PI
    return r * DEG_PER_RAD

def deg2rad(r):
    global PI
    RAD_PER_DEG = PI / 180.0
    return d * RAD_PER_DEG