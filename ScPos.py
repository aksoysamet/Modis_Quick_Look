import Util
import math
import Geo


class ScPos:
    def __init__(self, scEci=None, prevScEci=None):
        if scEci is not None:
            self.set(scEci, prevScEci)

    def set(self, scEci, prevScEci):
        self.scx = scEci.getPos().m_x
        self.scy = scEci.getPos().m_y
        self.scz = scEci.getPos().m_z
        self.scAlt = scEci.toGeo().m_Alt
        self.scDate = scEci.getDate()  # .getDate()
        self.scD = math.sqrt((self.scx*self.scx) + (self.scy*self.scy) + (self.scz*self.scz))  # noqa
        scale = self.scAlt / self.scD
        self.scOpp = [-self.scx*scale, -self.scy*scale, -self.scz*scale]
        self.R = Util.calcRotation(self.scOpp, self.calcOpp(prevScEci))

    def calcPos(self, scanAngle=.0, trackAngle=.0):
        ray = Util.calcRay(scanAngle, trackAngle, self.scD, self.scAlt)
        Util.applyRotation(ray, self.R)
        Util.applyElevation(ray, self.scOpp)
        Util.applyHeading(ray, self.scOpp)
        x = self.scx + ray[Util.X]
        y = self.scy + ray[Util.Y]
        z = self.scz + ray[Util.Z]
        latGeocentric = Util.atan(z/math.sqrt((x*x)+(y*y)))
        latGeodetic = Util.atan(Util.tan(latGeocentric)/0.9933056)
        # gha =math.degrees(Util.greenwichHourAngleJD(self.scDate.getDate()))
        gmst = self.scDate.toGMST()
        gha = math.degrees(gmst)
        lon = Util.modToRange(-180.0, Util.calcAngle(x, y)-gha, 180.0)
        return Geo.Geo.Location(latGeodetic, lon)

    def calcOpp(self, scEci):
        scx = scEci.getPos().m_x
        scy = scEci.getPos().m_y
        scz = scEci.getPos().m_z
        scD = math.sqrt((scx*scx) + (scy*scy) + (scz*scz))
        scale = scEci.toGeo().m_Alt / scD
        return [-scx*scale, -scy*scale, -scz*scale]
