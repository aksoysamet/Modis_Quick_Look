from dataParser import DataParser
from imageSaver import *
from process import Process
from streamCalibration import StreamCalibration
from lut import LUT
from nobow import NoBow
import os
import numpy as np
from Geo import Geo
from osgeo import gdal
from ScPos import ScPos


class Main():
    def __init__(self, file, bandlist, tle):
        self.size = (os.path.getsize(file)//642)//1354
        self.file = file
        self.bandlist = bandlist
        self.firstScan = True
        self.pr = DataParser()
        self.nb = NoBow(bandlist)
        self.geo = Geo(10, 1354, tle)
        self.Lats = np.empty((self.size*10, 1354), dtype=np.float)
        self.Longs = np.empty((self.size*10, 1354), dtype=np.float)
        if "P042" in file:
            lut = "TerraLUTs.bin.gz"
        elif "P154" in file:
            lut = "AquaLUTs.bin.gz"
        lutfile = "D:\\modis\\simulcast\\LUTs\\" + lut
        self.LUT = LUT(lutfile)
        self.cal = StreamCalibration(self.pr)
        self.p = Process(self.size, self.pr, bandlist, self.cal, self.LUT)
        self.pk = self.read()
        self.B250 = self.p.B250[:, :(self.pk//1354)*40]
        self.B500 = self.p.B500[:, :(self.pk//1354)*20]
        self.B1000 = self.p.B1000[:, :(self.pk//1354)*10]
        self.Lats = self.Lats[:(self.pk//1354)*10]
        self.Longs = self.Longs[:(self.pk//1354)*10]
        print("No Bow Started")
        self.B250, self.B500, self.B1000 = self.nb.getNoBowArr(self.B250, self.B500, self.B1000)  # noqa

    def getBandArr(self, band):
        if band < 2 and band >= 0:
            return self.B250[band]
        elif band < 7:
            return self.B500[band-2]
        elif band < 37:
            return self.B1000[band-7]
        return []

    def GeoCalculate(self, scanTimeTag, pk):
        loc = self.geo.calcLoc(scanTimeTag)
        id = (pk//1354)*10
        geoLats, geoLons = self.geo.calcScan(scanTimeTag)
        self.Lats[id:id+10] = geoLats
        self.Longs[id:id+10] = geoLons
        if self.firstScan:
            self.firstScan = False
            tsince = (((scanTimeTag - self.geo.orbit.getTleTime()) / 1000.0) / 60.0) + self.geo.oneScan/4  # noqa
            prevScEci = self.geo.orbit.getPosition(tsince-self.geo.oneScan)
            scEci = self.geo.orbit.getPosition(tsince)
            scPos = ScPos(scEci, prevScEci)
            self.Rotation = scPos.R

    def read(self):
        pk = 0
        pScan = -1
        lastTime = -1
        print("Reading Started")
        with open(self.file, "rb") as f:
            while True:
                byte = f.read(642)
                if byte == b"":
                    break
                gS, t, pT, mS, scanC, sid, sC = self.pr.getHeader(byte)
                if scanC != pScan:
                    if pScan is not -1 and lastTime is not -1:
                        self.GeoCalculate(t, pk)
                    self.cal.reset()
                    pScan = scanC
                    lastTime = t
                if pT == 0:
                    if sid == 0:
                        pk = self.p.procDVP(byte, gS, t, sC, mS)
                        lastTime = t
                        if sC == 1 and gS == 1 and pk != 0:
                            # print(t)
                            print(f"{int(pk/1354)*40}x1354 pixel readed")
                            # if int(pk/1354)*40 == 200:
                            #     break
                    elif sid == 1:
                        cal_type = sC >> 5
                        if cal_type == 3:
                            self.cal.procDCP(byte, gS)
        print("Read Complete")
        return pk


# file = "../P0420064AAAAAAAAAAAAAA19358101513001.PDS"
file = "../P1540064AAAAAAAAAAAAAA19358084234001.PDS"
tle1 = ""
tle2 = ""
# P042 Terra Time: 1576919109.113 - 1576919521.235
# P154 Aqua Time: 1576231118.711
if "P042" in file:
    prefix = "MOD"
    tle1 = "1 25994           19354.00000000  .00000130  00000-0  28806-4 0 00006"  # noqa
    tle2 = "2 25994 098.2117 065.7986 0001029 113.5397 344.1213 14.57111880000016"  # noqa
elif "P154" in file:
    prefix = "MYD"
    tle1 = "1 27424U          19346.00000000  .00000135  00000-0  29940-4 0 00002"  # noqa
    tle2 = "2 27424 098.2152 284.2602 0001374 164.7068 010.5448 14.57107082000017"  # noqa


bandlist = [0, 3, 2]  # 0 = Red | 3 = green | 2 = blue | 1 = NIR
# 13, 11, 9
# 12, 11, 8
main = Main(file, bandlist, [tle1, tle2])

print(main.B250.shape, main.B500.shape, main.B1000.shape)
print(main.Lats.shape, main.Longs.shape)
# 1 Km RGB

red = main.getBandArr(bandlist[0])*6
if len(bandlist) < 3:
    green = None
    blue = None
else:
    green = main.getBandArr(bandlist[1])*6
    blue = main.getBandArr(bandlist[2])*6

red, green, blue = reSampleArray(red, green, blue)

if green is not None and blue is not None:
    print(red.shape, green.shape, blue.shape)
else:
    print(red.shape)
img_Arr = buildImgArr(red, green, blue)

print("Saving image to", "output/" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".png")  # noqa
saveArrayToImg(img_Arr, "output/" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".png")  # noqa
print("Save completed")

# import csv
# w = open("output/lats.csv", "w", newline='')
# wr = csv.writer(w, dialect='excel')
# wr.writerows(main.Lats)
# w.close()

driver = gdal.GetDriverByName('GTiff')
output_raster = driver.Create('output/lats.tif', main.Lats.shape[1], main.Lats.shape[0], 1, gdal.GDT_Float32)  # Open the file  # noqa
output_raster.GetRasterBand(1).WriteArray(main.Lats)
output_raster.FlushCache()
output_raster = None

output_raster = driver.Create('output/longs.tif', main.Longs.shape[1], main.Longs.shape[0], 1, gdal.GDT_Float32)  # Open the file  # noqa
output_raster.GetRasterBand(1).WriteArray(main.Longs)
output_raster.FlushCache()
output_raster = None

if green is None or blue is None:
    ratio = red.shape[1]//1354
else:
    ratio = max(red.shape[1], green.shape[1], blue.shape[1])//1354

ds = gdal.Open("output/" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".png")  # noqa
metadata = {
    "X_DATASET": "output/longs.tif",
    "X_BAND": "1",
    "Y_DATASET": "output/lats.tif",
    "Y_BAND": "1",
    "PIXEL_OFFSET": "0",
    "LINE_OFFSET": "0",
    "PIXEL_STEP": str(ratio),
    "LINE_STEP": str(ratio)
}
ds.SetMetadata(metadata, "GEOLOCATION")

gdal.Translate('output/img.vrt', ds, options='-of VRT')
ds = None
ds = gdal.Open('output/img.vrt')
gdal.Warp("output/" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".tif", ds, options='-geoloc -t_srs EPSG:4326 -overwrite')  # noqa
ds = None
ratio = 100/(ratio*4)  # 4 Kat küçük
gdal.Translate("output/QL_" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".jpg",  # noqa
                "output/" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".png",  # noqa
                options='-outsize ' + str(ratio) + '% ' + str(ratio) + '% -of JPEG')  # noqa

rotateImageSave("output/QL_" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".jpg",  # noqa
    "output/QL_" + prefix + "_" + "_".join(str(x) for x in bandlist) + "_rotated.jpg",  # noqa
    180-main.Rotation)


# Cleaning
def rmFTry(n):
    def rmFiles():
        if os.path.exists("output/img.vrt"):
            os.remove("output/img.vrt")
        if os.path.exists("output/" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".png" + ".aux.xml"):  # noqa
            os.remove("output/" + prefix + "_" + "_".join(str(x) for x in bandlist) + ".png" + ".aux.xml")  # noqa
        if os.path.exists("output/lats.tif"):
            os.remove("output/lats.tif")
        if os.path.exists("output/longs.tif"):
            os.remove("output/longs.tif")
    if n is not 0:
        print("Trying to remove files")
        try:
            rmFiles()
            print("Files are removed")
        except PermissionError:
            import time
            time.sleep(.5)
            rmFTry(n-1)


rmFTry(10)
