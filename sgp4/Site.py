from .CoordGeo import CoordGeo
from .CoordTopo import CoordTopo
from .ECI import ECI
from .Vector import Vector
import Globals
import math

WANT_ATMOSPHERIC_CORRECTION = True

class Site:
    def __init__(self, geo):
        self.m_geo = geo

    @classmethod
    def fromLLA(cls, degLat, degLon, kmAlt):
        return cls(CoordGeo(Globals.deg2rad(degLat),Globals.deg2rad(degLon),kmAlt))

    def setGeo(self, geo):
        self.m_geo = geo

    def getPosition(self, date):
        return ECI(self.m_geo, date)

    def getLookAngle(self, eci):
        global WANT_ATMOSPHERIC_CORRECTION
        date = eci.getDate()
        eciSite = ECI(self.m_geo, date)

        vecRgRate = Vector(eci.getVel().m_x - eciSite.getVel().m_x,\
            eci.getVel().m_y - eciSite.getVel().m_y,\
            eci.getVel().m_z - eciSite.getVel().m_z)

        x = eci.getPos().m_x - eciSite.getPos().m_x
        y = eci.getPos().m_y - eciSite.getPos().m_y
        z = eci.getPos().m_z - eciSite.getPos().m_z
        w = math.sqrt(Globals.sqr(x) + Globals.sqr(y) + Globals.sqr(z))

        vecRange = Vector(x,y,z,w)

        theta = date.toLMST(self.getLon())

        sin_lat   = math.sin(self.getLat())
        cos_lat   = math.cos(self.getLat())
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        top_s = sin_lat * cos_theta * vecRange.m_x +\
            sin_lat * sin_theta * vecRange.m_y -\
            cos_lat * vecRange.m_z

        top_e = -sin_theta * vecRange.m_x +\
            cos_theta * vecRange.m_y

        top_z = cos_lat * cos_theta * vecRange.m_x +\
            cos_lat * sin_theta * vecRange.m_y +\
            sin_lat * vecRange.m_z
        
        az = math.atan(-top_e / top_s)

        if top_s > .0:
            az += Globals.PI

        if az < .0:
            az += Globals.TWOPI

        el   = math.asin(top_z / vecRange.m_w)
        rate = (vecRange.m_x * vecRgRate.m_x +\
            vecRange.m_y * vecRgRate.m_y +\
            vecRange.m_z * vecRgRate.m_z) / vecRange.m_w

        topo = CoordTopo(az, el, vecRange.m_w, rate)

        if WANT_ATMOSPHERIC_CORRECTION:
            topo.m_El += Globals.deg2rad((1.02 /\
                math.tan(Globals.deg2rad(Globals.rad2deg(el) + 10.3 /\
                (Globals.rad2deg(el) + 5.11)))) / 60.0)
            if topo.m_El < .0:
                topo.m_El = el

            if topo.m_El > (Globals.PI / 2):
                topo.m_El = (Globals.PI / 2)
        
        return topo

    def getLat(self):
        return self.m_geo.m_Lat

    def getLon(self):
        return self.m_geo.m_Lot

    def getAlt(self):
        return self.m_geo.m_Alt
