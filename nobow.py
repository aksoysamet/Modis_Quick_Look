import numpy as np
import math


class NoBow:
    def __init__(self, bandlist):
        self.scanAngle1000 = 110.0 / 1354
        self.trackAngle1000 = 0.812352557 / 10
        self.earthRadius = 1000 * 6378.17
        self.spacecraftAltitude = 1000 * 705.295
        self.bandlist = bandlist
        self.ix1000 = self.calc(10, 1354, 1000, self.scanAngle1000, self.trackAngle1000)  # noqa
        self.ix500 = self.calc(2*10, 2*1354, 1000/2, self.scanAngle1000/2, self.trackAngle1000/2)  # noqa
        self.ix250 = self.calc(4*10, 4*1354, 1000/4, self.scanAngle1000/4, self.trackAngle1000/4)  # noqa

    def getNoBowArr(self, B250, B500, B1000):
        fB250 = np.empty(B250.shape)
        fB500 = np.empty(B500.shape)
        fB1000 = np.empty(B1000.shape)
        for p in range(0, B1000.shape[1], 10):
            fB250[:, p*4:(p*4)+40], fB500[:, p*2:(p*2)+20], fB1000[:, p:p+10] = self.getNoBowValues(B250[:, p*4:(p*4)+40], B500[:, p*2:(p*2)+20], B1000[:, p:p+10])  # noqa
            print("No Bow Done: ", p//10)
        return (fB250, fB500, fB1000)

    def getNoBowValues(self, B250, B500, B1000):
        fB250 = [self.load(4*10, 4*1354, x, self.ix250) if c in self.bandlist else x for c, x in enumerate(B250)]  # noqa
        fB500 = [self.load(2*10, 2*1354, x, self.ix500) if c+2 in self.bandlist else x for c, x in enumerate(B500)]  # noqa
        fB1000 = [self.load(10, 1354, x, self.ix1000) if c+7 in self.bandlist else x for c, x in enumerate(B1000)]  # noqa
        return (fB250, fB500, fB1000)

    def load(self, nRows, nCols, values, ix):
        fvalues = np.zeros((nRows, nCols), dtype=np.uint8)
        for rx in range(nRows):
            for cx in range(nCols):
                fvalues[rx][cx] = values[ix[rx][cx]][cx]
        return fvalues

    def calc(self, nRows, nCols, resolution, scanAngleIncr, trackAngleIncr):
        nRowsHalf = int(nRows / 2)
        nColsHalf = int(nCols / 2)
        z = np.zeros((nRowsHalf+1, nColsHalf+1), dtype=int)
        for row in range(nRowsHalf+1):
            for col in range(nColsHalf+1):
                scanAngle = col * scanAngleIncr
                trackAngle = row * trackAngleIncr
                z[row][col] = int(round(self.calcZ(scanAngle, trackAngle) / resolution))  # noqa
        ix4th = np.zeros((nRowsHalf+1, nColsHalf+1), dtype=int)
        for col in range(nColsHalf+1):
            row = 0
            binCount = z[row+1][col] - z[row][col]
            binValue = 0
            for ixRow in range(nRowsHalf):
                if binCount == 0:
                    row += 1
                    binCount = z[row+1][col] - z[row][col]
                    binValue += 1
                ix4th[ixRow][col] = binValue
                binCount -= 1
        ix = np.zeros((nRows, nCols), dtype=int)
        for rx in range(nRowsHalf):
            for cx in range(nColsHalf):
                ix[rx][(nColsHalf-1)-cx] = (nRowsHalf-1) - ix4th[(nRowsHalf-1)-rx][cx]  # noqa
                ix[rx][nColsHalf+cx] = (nRowsHalf-1) - ix4th[(nRowsHalf-1)-rx][cx]  # noqa
                ix[nRowsHalf+rx][(nColsHalf-1)-cx] = nRowsHalf + ix4th[rx][cx]
                ix[nRowsHalf+rx][nColsHalf+cx] = nRowsHalf + ix4th[rx][cx]
        return ix

    def calcZ(self, scanAngle, trackAngle):
        d1 = 0
        scD = self.spacecraftAltitude + self.earthRadius
        if abs(scanAngle) > 0.0:
            aB = 180.0 - self.asin((scD * self.sin(abs(scanAngle))) / self.earthRadius)  # noqa
            aA = 180.0 - aB - abs(scanAngle)
            d1 = (scD * self.sin(aA)) / self.sin(aB)
        else:
            d1 = self.spacecraftAltitude
        return (d1 * self.sin(trackAngle))

    def sin(self, x):
        return math.sin(math.radians(x))

    def asin(self, x):
        return math.degrees(math.asin(x))
