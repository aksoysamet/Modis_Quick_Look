from . import Globals
import math
from .Vector import Vector
from .CoordGeo import CoordGeo

UNITS_NONE = 0
UNITS_AE = 1
UNITS_KM = 2

class ECI:
    def __init__(self, pos, vel, date, UnitType=1):
        self.m_pos = pos
        self.m_vel = vel
        self.m_date = date
        self.m_VecUnits = UnitType

    @classmethod
    def fromGEO(cls, geo, date):
        global UNITS_KM
        mfactor = Globals.TWOPI * (Globals.OMEGA_E / Globals.SEC_PER_DAY)
        lat = geo.m_Lat
        lon = geo.m_Lon
        alt = geo.m_Alt

        theta = date.toLMST(lon)
        c = 1.0 / math.sqrt(1.0 + Globals.F * (Globals.F - 2.0) * Globals.sqr(math.sin(lat)))
        s = Globals.sqr(1.0 - Globals.F) * c
        achcp = (Globals.XKMPER * c + alt) * math.cos(lat)

        m_pos = Vector()
        m_pos.m_x = achcp * math.cos(theta)
        m_pos.m_y = achcp * math.sin(theta)
        m_pos.m_z = (Globals.XKMPER * s + alt) * math.sin(lat)
        m_pos.m_w = math.sqrt(Globals.sqr(m_pos.m_x) +\
            Globals.sqr(m_pos.m_y) + Globals.sqr(m_pos.m_z))

        m_vel = Vector()
        m_vel.m_x = -mfactor * m_pos.m_y
        m_vel.m_y =  mfactor * m_pos.m_x
        m_vel.m_z = .0
        m_vel.m_w = math.sqrt(Globals.sqr(m_vel.m_x) + Globals.sqr(m_vel.m_y))

        return cls(m_pos, m_vel, date, UNITS_KM)

    def toGeo(self):
        self.ae2km()
        theta = Globals.AcTan(self.m_pos.m_y,self.m_pos.m_x)
        lon = (theta - self.m_date.toGMST()) % Globals.TWOPI

        if lon < .0:
            lon += Globals.TWOPI

        r = math.sqrt(Globals.sqr(self.m_pos.m_x) + Globals.sqr(self.m_pos.m_y))
        e2 = Globals.F * (2.0 - Globals.F)
        lat = Globals.AcTan(self.m_pos.m_z,r)

        delta = 1e-7
        phi = 0.
        c = 0.
        
        while abs(lat - phi) > delta:
            phi = lat
            c = 1.0 / math.sqrt(1.0 - e2 * Globals.sqr(math.sin(phi)))
            lat = Globals.AcTan(self.m_pos.m_z + Globals.XKMPER * c * e2 * math.sin(phi), r)

        alt = r / math.cos(lat) - Globals.XKMPER * c

        return CoordGeo(lat, lon, alt)

    def ae2km(self):
        global UNITS_KM
        global UNITS_AE
        if self.m_VecUnits == UNITS_AE:
            self.MulPos(Globals.XKMPER / Globals.AE)
            self.MulVel((Globals.XKMPER / Globals.AE) * (Globals.MIN_PER_DAY / 86400))
            self.m_VecUnits = UNITS_KM

    def getPos(self):
        return self.m_pos
    
    def getVel(self):
        return self.m_vel

    def getDate(self):
        return self.m_date

    def MulPos(self, factor):
        self.m_pos.mul(factor)
    
    def MulVel(self, factor):
        self.m_vel.mul(factor)
