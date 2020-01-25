from sgp4.TLE import TLE
from sgp4.Orbit import Orbit
from ScPos import ScPos
import numpy as np


class Geo:
    def __init__(self, row, col, tle):
        self.nRows = row
        self.nCols = col
        self.oneScan = 1.477 / 60
        self.scanAngleA = 110.0 / 1354
        self.trackAngleA = 0.812352557 / 10
        self.FD_SECS = 0.000333333
        self.FD_MINS = self.FD_SECS / 60.0
        self.halfAngle = 55
        self.initialize(tle)

    def initialize(self, tle):
        self.orbit = Orbit(TLE(tle[0], tle[1]))

    def calcLoc(self, scanTime):
        tsince = (((scanTime - self.orbit.getTleTime()) / 1000.0) / 60.0) + self.oneScan/4  # noqa
        prevScEci = self.orbit.getPosition(tsince-self.oneScan)
        scEci = self.orbit.getPosition(tsince)
        scPos = ScPos(scEci, prevScEci)
        return scPos.calcPos()

    def calcScan(self, scanTime):
        scPos = ScPos()
        midRow = self.nRows / 2
        tsince = (((scanTime - self.orbit.getTleTime()) / 1000.0) / 60.0) + self.oneScan/4  # noqa
        midCol = self.nCols / 2

        lats = np.empty((self.nRows, self.nCols))
        lons = np.empty((self.nRows, self.nCols))

        for row in range(self.nRows):
            samplecol = 0
            loc = None
            for col in range(self.nCols):
                prevScEci = self.orbit.getPosition((tsince+(col*self.FD_MINS))-self.oneScan)  # noqa
                scEci = self.orbit.getPosition(tsince+(col*self.FD_MINS))
                scPos.set(scEci, prevScEci)
                scanAngle = ((col-midCol)*self.scanAngleA)
                trackAngle = ((row-midRow)*self.trackAngleA)
                loc = scPos.calcPos(scanAngle, trackAngle)
                lats[row][col] = loc.getLat()
                lons[row][col] = loc.getLon()
        return (lats, lons)

    def getEstExtents(self, beginTime, endTime):
        tsince = (((beginTime - self.orbit.getTleTime()) / 1000.0) / 60.0)
        prevScEci = self.orbit.getPosition(tsince-self.oneScan)
        scEci = self.orbit.getPosition(tsince)
        beginScPos = ScPos(scEci, prevScEci)
        beginLeft = beginScPos.calcPos(self.halfAngle, 0.0)
        beginRight = beginScPos.calcPos(-self.halfAngle, 0.0)
        tsince = (((endTime - self.orbit.getTleTime()) / 1000.0) / 60.0)
        prevScEci = self.orbit.getPosition(tsince-self.oneScan)
        scEci = self.orbit.getPosition(tsince)
        endScPos = ScPos(scEci, prevScEci)
        endLeft = endScPos.calcPos(self.halfAngle, 0.0)
        endRight = endScPos.calcPos(-self.halfAngle, 0.0)
        return Geo.Extents(beginLeft, beginRight, endLeft, endRight)

    class Location:
        def __init__(self, lat=.0, lon=.0):
            self.lat = lat
            self.lon = lon

        def size(self):
            return 8+8

        def getLat(self):
            return self.lat

        def getLon(self):
            return self.lon

        def set(self, lat, lon):
            this.lat = lat
            this.lon = lon

    class Extents:
        def __init__(self, beginLeft=None, beginRight=None, endLeft=None, endRight=None):  # noqa
            if beginLeft is not None:
                self.beginLeft = beginLeft
                self.beginRight = beginRight
                self.endLeft = endLeft
                self.endRight = endRight
            else:
                self.beginLeft = Geo.Location()
                self.beginRight = Geo.Location()
                self.endLeft = Geo.Location()
                self.endRight = Geo.Location()

        def size(self):
            return self.beginLeft.size() + self.beginRight.size() + self.endLeft.size() + self.endRight.size()  # noqa

        def getBeginLeft():
            return self.beginLeft

        def getBeginRight():
            return self.beginRight

        def getEndLeft():
            return self.endLeft

        def getEndRight():
            return self.endRight

        def getMinLat(self):
            return min(self.beginRight.getLat(), self.beginLeft.getLat(), self.endRight.getLat(), self.endLeft.getLat())  # noqa

        def getMinLon(self):
            return min(self.beginRight.getLon(), self.beginLeft.getLon(), self.endRight.getLon(), self.endLeft.getLon())  # noqa

        def getMaxLat(self):
            return max(self.beginRight.getLat(), self.beginLeft.getLat(), self.endRight.getLat(), self.endLeft.getLat())  # noqa

        def getMaxLon(self):
            return max(self.beginRight.getLon(), self.beginLeft.getLon(), self.endRight.getLon(), self.endLeft.getLon())  # noqa
