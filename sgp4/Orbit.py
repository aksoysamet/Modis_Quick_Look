from .TLE import TLE
from .Julian import Julian
from .NoradSGP4 import NoradSGP4
import math
from . import Globals

class Orbit:
    def __init__(self, tle):
        self.m_tle = tle
        self.m_pNoradModel = None

        epochYear = int(self.m_tle.FLD_EPOCHYEAR)
        epochDay  = self.m_tle.FLD_EPOCHDAY

        if epochYear < 57:
            epochYear += 2000
        else:
            epochYear += 1900

        self.m_jdEpoch = Julian.fromYD(epochYear,epochDay)
        
        self.m_secPeriod = -1.0

        mm     = self.mnMotion()
        rpmin  = mm * 2 * Globals.PI / Globals.MIN_PER_DAY
        a1     = math.pow(Globals.XKE / rpmin, Globals.TWOTHRD)
        e      = self.Eccentricity()
        i      = self.Inclination()
        temp   = (1.5 * Globals.CK2 * (3.0 * Globals.sqr(math.cos(i)) - 1.0) /\
                math.pow(1.0 - e * e, 1.5))
        delta1 = temp / (a1 * a1)
        a0     = a1 *\
                (1.0 - delta1 *\
                ((1.0 / 3.0) + delta1 *\
                (1.0 + 134.0 / 81.0 * delta1)))
        delta0 = temp / (a0 * a0)

        self.m_mnMotionRec        = rpmin / (1.0 + delta0)
        self.m_aeAxisSemiMinorRec = a0 / (1.0 - delta0)
        self.m_aeAxisSemiMajorRec = self.m_aeAxisSemiMinorRec / math.sqrt(1.0 - (e * e))
        self.m_kmPerigeeRec       = Globals.XKMPER * (self.m_aeAxisSemiMinorRec * (1.0 - e) - Globals.AE)

        if Globals.TWOPI / self.m_mnMotionRec >= 255.:
            raise TypeError("SDP4 not supported")
        else:
            self.m_pNoradModel = NoradSGP4(self)

    def Period(self):
        if self.m_secPeriod < .0:
            if self.m_mnMotionRec is 0:
                self.m_secPeriod = .0
            else:
                self.m_secPeriod = (Globals.TWOPI) / self.m_mnMotionRec * 60.0
        
        return self.m_secPeriod
    
    def getPosition(self, tsince):
        eci = self.m_pNoradModel.getPosition(tsince)
        eci.ae2km()
        return eci

    def getTleTime(self):
        return self.m_jdEpoch.getTime()
    
    def Inclination(self):
        return self.m_tle.FLD_I * Globals.RADS_PER_DEG 
    def Eccentricity(self):
        return self.m_tle.FLD_E
    def RAAN(self):
        return self.m_tle.FLD_RAAN * Globals.RADS_PER_DEG 
    def ArgPerigee(self):
        return self.m_tle.FLD_ARGPER * Globals.RADS_PER_DEG 
    def BStar(self):
        return self.m_tle.FLD_BSTAR / Globals.AE
    def Drag(self):
        return self.m_tle.FLD_MMOTIONDT
    def mnMotion(self):
        return self.m_tle.FLD_MMOTION
    def mnAnomaly(self):
        return self.m_tle.FLD_M * Globals.RADS_PER_DEG 

    def SemiMajor(self):
        return self.m_aeAxisSemiMajorRec
    def SemiMinor(self):
        return self.m_aeAxisSemiMinorRec
    def mnMotionRec(self):
        return self.m_mnMotionRec
    def Major(self):
        return self.SemiMajor() * 2.0
    def Minor(self):
        return self.SemiMinor() * 2.0
    def Perigee(self):
        return self.m_kmPerigeeRec
    def Epoch(self):
        return self.m_jdEpoch