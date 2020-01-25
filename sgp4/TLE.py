class TLE:
    def __init__(self, line1, line2):
        self.m_Line1 = line1
        self.m_Line2 = line2
        self.initialize()

    def initialize(self):
        line = self.m_Line1.rstrip()
        if (len(line) >= 64 and
            line.startswith('1 ') and
            line[8] == ' ' and
            line[23] == '.' and
            line[32] == ' ' and
            line[34] == '.' and
            line[43] == ' ' and
            line[52] == ' ' and
            line[61] == ' ' and
            line[63] == ' '):
        
            self.FLD_NORADNUM = int(line[2:7])
            self.FLD_INTLDESC = line[9:17]
            self.FLD_EPOCHYEAR = int(line[18:20])
            self.FLD_EPOCHDAY = float(line[20:32])
            self.FLD_MMOTIONDT = float(line[33:43])
            self.FLD_MMOTIONDT2 = float(line[44] + "0." + line[45:52].replace("-","e-"))
            self.FLD_BSTAR = float(line[53] + "0." + line[54:61].replace("-","e-"))
            self.FLD_SET = int(line[64:68])
        else:
            raise ValueError(f"'{line}' is wrong")
        
        line = self.m_Line2.rstrip()
        if (len(line) >= 69 and
            line.startswith('2 ') and
            line[7] == ' ' and
            line[11] == '.' and
            line[16] == ' ' and
            line[20] == '.' and
            line[25] == ' ' and
            line[33] == ' ' and
            line[37] == '.' and
            line[42] == ' ' and
            line[46] == '.' and
            line[51] == ' '):

            self.FLD_I = float(line[8:16])
            self.FLD_RAAN = float(line[17:25])
            self.FLD_E = float('0.' + line[26:33].replace(' ', '0'))
            self.FLD_ARGPER = float(line[34:42])
            self.FLD_M = float(line[43:51])
            self.FLD_MMOTION = float(line[52:63])
            self.FLD_ORBITNUM = line[63:68]
        else:
            raise ValueError(f"'{line}' is wrong")
