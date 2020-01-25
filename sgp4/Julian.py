from datetime import datetime
from . import Globals
import pytz
EPOCH_JAN1_00H_1900 = 2415019.5
EPOCH_JAN1_12H_1900 = 2415020.0
EPOCH_JAN1_12H_2000 = 2451545.0

class Julian:
    def __init__(self, date, time):
        self.m_Date = date
        self.time = time

    @classmethod
    def fromYD(cls, year, day):
        cal = datetime.strptime(str(year), "%Y").replace(tzinfo=pytz.utc)
        time = cal.timestamp() * 1000 + round((day -1) * (24 * 60 * 60 * 1000))
        year -= 1
        A = (year // 100)
        B = 2 - A + (A // 4)
        NewYears = int(365.25 * year) +\
            int(30.6001 * 14) + 1720994.5 + B
        m_Date = NewYears + day
        return cls(m_Date, time)

    def toGMST(self):
        UT = (self.m_Date + 0.5) % 1.0
        TU = (self.FromJan1_12h_2000() - UT) / 36525.0

        GMST = 24110.54841 + TU *\
            (8640184.812866 + TU * (0.093104 - TU * 6.2e-06))

        GMST = (GMST + Globals.SEC_PER_DAY * Globals.OMEGA_E * UT) % Globals.SEC_PER_DAY

        if GMST < .0:
            GMST += Globals.SEC_PER_DAY

        return (Globals.TWOPI * (GMST / Globals.SEC_PER_DAY))

    def toLMST(self, lon):
        return (self.toGMST() + lon) % Globals.TWOPI

    def getDate(self):
        return self.m_Date

    def getTime(self):
        return self.time
    
    def FromJan1_00h_1900(self):
        global EPOCH_JAN1_00H_1900
        return self.m_Date - EPOCH_JAN1_00H_1900

    def FromJan1_12h_1900(self):
        global EPOCH_JAN1_12H_1900
        return self.m_Date - EPOCH_JAN1_12H_1900

    def FromJan1_12h_2000(self):
        global EPOCH_JAN1_12H_2000
        return self.m_Date - EPOCH_JAN1_12H_2000

    def addMin(self, min):
        self.m_Date += ((min / 60.0) / 24.0)