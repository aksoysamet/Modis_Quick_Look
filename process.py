import numpy as np


class Process:
    def __init__(self, size, dataParser, bandlist, calibration, lut):
        self.prev_sample = 1
        self.prev_time = -1
        self.bandlist = bandlist
        self.dataParser = dataParser
        self.sCalibration = calibration
        self.LUT = lut
        self.B250 = np.empty((2, size*40, 1354*4), dtype=np.uint16)  # 0, 1
        self.B500 = np.empty((5, size*20, 1354*2), dtype=np.uint16)  # 2 .. 6
        self.B1000 = np.empty((31, size*10, 1354), dtype=np.uint16)  # 7 .. 36
        self.dvpk = 0

    def addPacketToView(self, pk, byte, ifovs, mirrorSide):
        for band in range(0, 2):
            if band not in self.bandlist:
                continue
            for ifov in ifovs:
                for sample in range(0, 4):
                    for detector in range(0, 4):
                        row = (4 * ifov) + detector
                        row = int(pk/1354)*40 + (39 - row)
                        col = (pk % 1354)*4 + sample
                        try:
                            value = byte[(ifov % 5)*83 + sample*4 + detector + band*16]  # noqa
                            svAverage = self.sCalibration.svSums250[band][(4 * ifov) + detector][sample] / 50  # noqa
                            dnEVstar = (value-svAverage) / self.LUT.RVSrefLUT250[band][(4 * ifov) + detector][mirrorSide][(pk % 1354)]  # noqa
                            erf = (self.LUT.m1LUT250[band][(4 * ifov) + detector][sample][mirrorSide] * dnEVstar) * 256  # noqa
                            self.B250[band][row][col] = int(erf)
                        except IndexError:
                            self.B250.resize((2, self.B250.shape[1]+40, 5416))

        for band in range(0, 5):
            if (band+2) not in self.bandlist:
                continue
            for ifov in ifovs:
                for sample in range(0, 2):
                    for detector in range(0, 2):
                        row = (2 * ifov) + detector
                        row = int(pk/1354)*20 + (19 - row)
                        col = (pk % 1354)*2 + sample
                        try:
                            value = byte[(ifov % 5)*83 + sample*2 + detector + 32 + band*4]  # noqa
                            svAverage = self.sCalibration.svSums500[band][(2 * ifov) + detector][sample] / 50  # noqa
                            dnEVstar = (value-svAverage) / self.LUT.RVSrefLUT500[band][(2 * ifov) + detector][mirrorSide][(pk % 1354)]  # noqa
                            erf = (self.LUT.m1LUT500[band][(2 * ifov) + detector][sample][mirrorSide] * dnEVstar) * 256  # noqa
                            self.B500[band][row][col] = int(erf)
                        except IndexError:
                            self.B500.resize((4, self.B500.shape[1]+20, 2708))

        for band in range(0, 31):
            if (band+7) not in self.bandlist:
                continue
            for ifov in ifovs:
                row = ifov
                row = int(pk/1354)*10 + (9 - row)
                col = (pk % 1354)
                try:
                    value = byte[(ifov % 5)*83 + 52 + band]
                    svAverage = self.sCalibration.svSums1000[band][ifov] / 50
                    if band < 15:
                        dnEVstar = (value-svAverage) / self.LUT.RVSrefLUT1000[band][ifov][mirrorSide][(pk % 1354)]  # noqa
                        erf = (self.LUT.m1LUT1000[band][ifov][mirrorSide] * dnEVstar) * 256  # noqa
                        self.B1000[band][row][col] = int(erf)
                    else:
                        self.B1000[band][row][col] = int(value-svAverage) >> 4
                except IndexError:
                    print(band, row, col)
                    self.B1000.resize((31, self.B1000.shape[1]+10, 1354))

    def procDVP(self, byte, gS, time, sC, mS):
        if sC != self.prev_sample and self.dvpk != 0:
            if time != self.prev_time:
                if self.prev_time != -1:
                    dt = time - self.prev_time
                    dp = round(dt/1477)
                    self.dvpk = ((self.dvpk + dp*1354)//1354)*1354
                    self.prev_sample = 1
                prev_time = time
            dp = sC - self.prev_sample
            self.dvpk += dp
            self.prev_sample = sC

        if sC == self.prev_sample:
            if time != self.prev_time:
                if self.prev_time != -1:
                    dt = time - self.prev_time
                    dp = round(dt/1477)
                    if sC == 1:
                        dp -= 1
                    if dp > 0:
                        self.dvpk += dp*1354
                self.prev_time = time
            arr = self.dataParser.read_uint12(byte)
            if gS == 1:
                self.addPacketToView(self.dvpk, arr, range(0, 5), mS)
            elif gS == 2:
                self.addPacketToView(self.dvpk, arr, range(5, 10), mS)
                self.prev_sample += 1
                self.dvpk += 1
                if self.prev_sample == 1355:
                    self.prev_sample = 1
        return self.dvpk
