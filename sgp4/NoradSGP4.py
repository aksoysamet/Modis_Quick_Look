from .NoradBase import NoradBase
from . import Globals
import math

class NoradSGP4(NoradBase):
    def __init__(self, orbit):
        super().__init__(orbit)
        self.m_c5 = 2.0 * self.m_coef1 * self.m_aodp * self.m_betao2 *\
            (1.0 + 2.75 * (self.m_etasq + self.m_eeta) + self.m_eeta * self.m_etasq)
        self.m_omgcof = self.m_Orbit.BStar() * self.m_c3 * math.cos(self.m_Orbit.ArgPerigee())
        self.m_xmcof = -Globals.TWOTHRD * self.m_coef * self.m_Orbit.BStar() * Globals.AE / self.m_eeta
        self.m_delmo = math.pow(1.0 + self.m_eta * math.cos(self.m_Orbit.mnAnomaly()), 3.0)
        self.m_sinmo = math.sin(self.m_Orbit.mnAnomaly())

    def getPosition(self, tsince):
        isimp = False
        if (self.m_aodp * (1.0 - self.m_satEcc) / Globals.AE) < (220.0 / Globals.XKMPER + Globals.AE):
            isimp = True
        
        d2 = 0.
        d3 = 0.
        d4 = 0.

        t3cof = 0.
        t4cof = 0.
        t5cof = 0.

        if not isimp:
            c1sq = self.m_c1 * self.m_c1

            d2 = 4.0 * self.m_aodp * self.m_tsi * c1sq

            temp = d2 * self.m_tsi * self.m_c1 / 3.0

            d3 = (17.0 * self.m_aodp + self.m_s4) * temp
            d4 = 0.5 * temp * self.m_aodp * self.m_tsi *\
                (221.0 * self.m_aodp + 31.0 * self.m_s4) * self.m_c1
            t3cof = d2 + 2.0 * c1sq
            t4cof = 0.25 * (3.0 * d3 + self.m_c1 * (12.0 * d2 + 10.0 * c1sq))
            t5cof = 0.2 * (3.0 * d4 + 12.0 * self.m_c1 * d3 + 6.0 *\
                d2 * d2 + 15.0 * c1sq * (2.0 * d2 + c1sq))

        xmdf   = self.m_Orbit.mnAnomaly() + self.m_xmdot * tsince
        omgadf = self.m_Orbit.ArgPerigee() + self.m_omgdot * tsince
        xnoddf = self.m_Orbit.RAAN() + self.m_xnodot * tsince
        omega  = omgadf
        xmp    = xmdf
        tsq    = tsince * tsince
        xnode  = xnoddf + self.m_xnodcf * tsq
        tempa  = 1.0 - self.m_c1 * tsince
        tempe  = self.m_Orbit.BStar() * self.m_c4 * tsince
        templ  = self.m_t2cof * tsq

        if not isimp:
            delomg = self.m_omgcof * tsince
            delm = self.m_xmcof * (math.pow(1.0 + self.m_eta * math.cos(xmdf), 3.0) - self.m_delmo)
            temp = delomg + delm

            xmp = xmdf + temp
            omega = omgadf - temp

            tcube = tsq * tsince
            tfour = tsince * tcube

            tempa = tempa - d2 * tsq - d3 * tcube - d4 * tfour
            tempe = tempe + self.m_Orbit.BStar() * self.m_c5 * (math.sin(xmp) - self.m_sinmo)
            templ = templ + t3cof * tcube + tfour * (t4cof + tsince * t5cof)

        a  = self.m_aodp * Globals.sqr(tempa)
        e  = self.m_satEcc - tempe

        xl = xmp + omega + xnode + self.m_xnodp * templ
        xn = Globals.XKE / math.pow(a, 1.5)

        return self.FinalPosition(self.m_satInc, omgadf, e, a, xl, xnode, xn, tsince)