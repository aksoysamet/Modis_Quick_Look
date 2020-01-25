import numpy as np


class StreamCalibration:
    def __init__(self, dataParser):
        self.svSums250 = np.zeros((2, 40, 4))
        self.svSums500 = np.zeros((5, 20, 2))
        self.svSums1000 = np.zeros((31, 10))
        self.dataParser = dataParser

    def reset(self):
        self.svSums250 = np.zeros((2, 40, 4))
        self.svSums500 = np.zeros((5, 20, 2))
        self.svSums1000 = np.zeros((31, 10))

    def addPacketToCal(self, pk, byte, ifovs):
        for ifov in ifovs:
            for band in range(0, 2):
                for sample in range(0, 4):
                    for detector in range(0, 4):
                        row = (4 * ifov) + detector
                        col = sample
                        try:
                            self.svSums250[band][row][col] += byte[(ifov % 5)*83 + sample*4 + detector + band*16]  # noqa
                        except IndexError:
                            pass

            for band in range(0, 5):
                for sample in range(0, 2):
                    for detector in range(0, 2):
                        row = (2 * ifov) + detector
                        col = sample
                        try:
                            self.svSums500[band][row][col] += byte[(ifov % 5)*83 + sample*2 + detector + 32 + band*4]  # noqa
                        except IndexError:
                            pass

            for band in range(0, 31):
                if (band+7) not in self.bandlist:
                    continue
                row = ifov
                try:
                    self.svSums1000[band][row] += byte[(ifov % 5)*83 + 52 + band]  # noqa
                except IndexError:
                    pass

    def procDCP(self, byte, groupSequence):
        arr = self.dataParser.read_uint12(byte)
        if groupSequence == 1:
            self.addPacketToCal(arr, range(0, 5))
        elif groupSequence == 2:
            self.addPacketToCal(arr, range(5, 10))
