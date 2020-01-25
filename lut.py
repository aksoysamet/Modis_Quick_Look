import gzip
import numpy as np
import struct


class LUT:
    def __init__(self, file):
        print("LUT Reading Started")
        with gzip.open(file, "rb") as f:
            self.f = f
            self.load()

    def load(self):
        self.m1LUT250 = np.frombuffer(self.f.read(4*2*40*4*2), dtype=np.dtype('>f4')).reshape((2, 40, 4, 2))  # noqa
        self.m1LUT500 = np.frombuffer(self.f.read(4*5*20*2*2), dtype=np.dtype('>f4')).reshape((5, 20, 2, 2))  # noqa
        self.m1LUT1000 = np.frombuffer(self.f.read(4*15*10*2), dtype=np.dtype('>f4')).reshape((15, 10, 2))  # noqa
        self.f.seek((4*2*40*4*2 + 4*5*20*2*2 + 4*15*10*2), 1)
        self.RVSrefLUT250 = np.frombuffer(self.f.read(4*2*40*2*1354), dtype=np.dtype('>f4')).reshape((2, 40, 2, 1354))  # noqa
        self.RVSrefLUT500 = np.frombuffer(self.f.read(4*5*20*2*1354), dtype=np.dtype('>f4')).reshape((5, 20, 2, 1354))  # noqa
        self.RVSrefLUT1000 = np.frombuffer(self.f.read(4*15*10*2*1354), dtype=np.dtype('>f4')).reshape((15, 10, 2, 1354))  # noqa
