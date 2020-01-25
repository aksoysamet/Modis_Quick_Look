from .Vector import Vector
from .ECI import ECI
from .Julian import Julian
import math
from . import Globals

class NoradBase:
    def __init__(self, orbit):
        self.m_Orbit = orbit
        self.initialize()

    def initialize(self):
        self.m_satInc = self.m_Orbit.Inclination()
        self.m_satEcc = self.m_Orbit.Eccentricity()

        self.m_cosio  = math.cos(self.m_satInc)
        self.m_theta2 = self.m_cosio * self.m_cosio
        self.m_x3thm1 = 3.0 * self.m_theta2 - 1.0
        self.m_eosq   = self.m_satEcc * self.m_satEcc
        self.m_betao2 = 1.0 - self.m_eosq
        self.m_betao  = math.sqrt(self.m_betao2)

        self.m_aodp  = self.m_Orbit.SemiMinor()  # SemiMajor Olabilir
        self.m_xnodp = self.m_Orbit.mnMotionRec()

        self.m_perigee = Globals.XKMPER * (self.m_aodp * (1.0 - self.m_satEcc) - Globals.AE)

        self.m_s4      = Globals.S
        self.m_qoms24  = Globals.QOMS2T
        if self.m_perigee < 156.0:
            self.m_s4 = self.m_perigee - 78.0
            if self.m_perigee <= 98.0:
                self.m_s4 = 20.0
            self.m_qoms24 = math.pow((120.0 - self.m_s4) * Globals.AE / Globals.XKMPER, 4.0)
            self.m_s4 = self.m_s4 / Globals.XKMPER + Globals.AE

        pinvsq = 1.0 / (self.m_aodp * self.m_aodp * self.m_betao2 * self.m_betao2)

        self.m_tsi   = 1.0 / (self.m_aodp - self.m_s4)
        self.m_eta   = self.m_aodp * self.m_satEcc * self.m_tsi
        self.m_etasq = self.m_eta * self.m_eta
        self.m_eeta  = self.m_satEcc * self.m_eta

        psisq  = abs(1.0 - self.m_etasq)

        self.m_coef  = self.m_qoms24 * math.pow(self.m_tsi,4.0)
        self.m_coef1 = self.m_coef / math.pow(psisq,3.5)

        c2 = self.m_coef1 * self.m_xnodp *\
                            (self.m_aodp * (1.0 + 1.5 * self.m_etasq + self.m_eeta * (4.0 + self.m_etasq)) +\
                            0.75 * Globals.CK2 * self.m_tsi / psisq * self.m_x3thm1 *\
                            (8.0 + 3.0 * self.m_etasq * (8.0 + self.m_etasq)))

        self.m_c1    = self.m_Orbit.BStar() * c2
        self.m_sinio = math.sin(self.m_satInc)

        a3ovk2 = -Globals.XJ3 / Globals.CK2 * math.pow(Globals.AE,3.0)

        self.m_c3     = self.m_coef * self.m_tsi * a3ovk2 * self.m_xnodp * Globals.AE * self.m_sinio / self.m_satEcc
        self.m_x1mth2 = 1.0 - self.m_theta2
        self.m_c4     = 2.0 * self.m_xnodp * self.m_coef1 * self.m_aodp * self.m_betao2 *\
                    (self.m_eta * (2.0 + 0.5 * self.m_etasq) +\
                    self.m_satEcc * (0.5 + 2.0 * self.m_etasq) -\
                    2.0 * Globals.CK2 * self.m_tsi / (self.m_aodp * psisq) *\
                    (-3.0 * self.m_x3thm1 * (1.0 - 2.0 * self.m_eeta + self.m_etasq * (1.5 - 0.5 * self.m_eeta)) +\
                    0.75 * self.m_x1mth2 *\
                    (2.0 * self.m_etasq - self.m_eeta * (1.0 + self.m_etasq)) *\
                    math.cos(2.0 * self.m_Orbit.ArgPerigee())))

        theta4 = self.m_theta2 * self.m_theta2
        temp1  = 3.0 * Globals.CK2 * pinvsq * self.m_xnodp
        temp2  = temp1 * Globals.CK2 * pinvsq
        temp3  = 1.25 * Globals.CK4 * pinvsq * pinvsq * self.m_xnodp

        self.m_xmdot = self.m_xnodp + 0.5 * temp1 * self.m_betao * self.m_x3thm1 +\
                    0.0625 * temp2 * self.m_betao *\
                    (13.0 - 78.0 * self.m_theta2 + 137.0 * theta4)

        x1m5th = 1.0 - 5.0 * self.m_theta2

        self.m_omgdot = -0.5 * temp1 * x1m5th + 0.0625 * temp2 *\
                    (7.0 - 114.0 * self.m_theta2 + 395.0 * theta4) +\
                    temp3 * (3.0 - 36.0 * self.m_theta2 + 49.0 * theta4)

        xhdot1 = -temp1 * self.m_cosio

        self.m_xnodot = xhdot1 + (0.5 * temp2 * (4.0 - 19.0 * self.m_theta2) +\
                    2.0 * temp3 * (3.0 - 7.0 * self.m_theta2)) * self.m_cosio
        self.m_xnodcf = 3.5 * self.m_betao2 * xhdot1 * self.m_c1
        self.m_t2cof  = 1.5 * self.m_c1
        self.m_xlcof  = 0.125 * a3ovk2 * self.m_sinio *\
                    (3.0 + 5.0 * self.m_cosio) / (1.0 + self.m_cosio)
        self.m_aycof  = 0.25 * a3ovk2 * self.m_sinio
        self.m_x7thm1 = 7.0 * self.m_theta2 - 1.0

    def FinalPosition(self, incl, omega, e, a, xl, xnode, xn, tsince):
        beta = math.sqrt(1.0 - e * e)

        axn  = e * math.cos(omega)
        temp = 1.0 / (a * beta * beta)
        xll  = temp * self.m_xlcof * axn
        aynl = temp * self.m_aycof
        xlt  = xl + xll
        ayn  = e * math.sin(omega) + aynl

        capu   = Globals.Fmod2p(xlt - xnode)
        temp2  = capu
        temp3  = 0.0
        temp4  = 0.0
        temp5  = 0.0
        temp6  = 0.0
        sinepw = 0.0
        cosepw = 0.0
        fDone  = False

        for i in range(1, 11):
            if fDone:
                break
            sinepw = math.sin(temp2)
            cosepw = math.cos(temp2)
            temp3 = axn * sinepw
            temp4 = ayn * cosepw
            temp5 = axn * cosepw
            temp6 = ayn * sinepw

            epw = (capu - temp4 + temp3 - temp2) /\
                        (1.0 - temp5 - temp6) + temp2

            if abs(epw - temp2) <= Globals.E6A:
                fDone = True
            else:
                temp2 = epw

        ecose = temp5 + temp6
        esine = temp3 - temp4
        elsq  = axn * axn + ayn * ayn
        temp  = 1.0 - elsq
        pl = a * temp
        r  = a * (1.0 - ecose)
        temp1 = 1.0 / r
        rdot  = Globals.XKE * math.sqrt(a) * esine * temp1
        rfdot = Globals.XKE * math.sqrt(pl) * temp1
        temp2 = a * temp1
        betal = math.sqrt(temp)
        temp3 = 1.0 / (1.0 + betal)
        cosu  = temp2 * (cosepw - axn + ayn * esine * temp3)
        sinu  = temp2 * (sinepw - ayn - axn * esine * temp3)
        u     = Globals.AcTan(sinu, cosu)
        sin2u = 2.0 * sinu * cosu
        cos2u = 2.0 * cosu * cosu - 1.0

        temp  = 1.0 / pl
        temp1 = Globals.CK2 * temp
        temp2 = temp1 * temp

        rk = r * (1.0 - 1.5 * temp2 * betal * self.m_x3thm1) +\
                    0.5 * temp1 * self.m_x1mth2 * cos2u
        uk = u - 0.25 * temp2 * self.m_x7thm1 * sin2u
        xnodek = xnode + 1.5 * temp2 * self.m_cosio * sin2u
        xinck  = incl + 1.5 * temp2 * self.m_cosio * self.m_sinio * cos2u
        rdotk  = rdot - xn * temp1 * self.m_x1mth2 * sin2u
        rfdotk = rfdot + xn * temp1 * (self.m_x1mth2 * cos2u + 1.5 * self.m_x3thm1)

        sinuk  = math.sin(uk)
        cosuk  = math.cos(uk)
        sinik  = math.sin(xinck)
        cosik  = math.cos(xinck)
        sinnok = math.sin(xnodek)
        cosnok = math.cos(xnodek)
        xmx = -sinnok * cosik
        xmy = cosnok * cosik
        ux  = xmx * sinuk + cosnok * cosuk
        uy  = xmy * sinuk + sinnok * cosuk
        uz  = sinik * sinuk
        vx  = xmx * cosuk - cosnok * sinuk
        vy  = xmy * cosuk - sinnok * sinuk
        vz  = sinik * cosuk

        x = rk * ux
        y = rk * uy
        z = rk * uz

        vecPos = Vector(x, y, z)

        altKm = (vecPos.magnitude() * (Globals.XKMPER / Globals.AE))

        xdot = rdotk * ux + rfdotk * vx
        ydot = rdotk * uy + rfdotk * vy
        zdot = rdotk * uz + rfdotk * vz

        vecVel = Vector(xdot, ydot, zdot)

        gmt = Julian(self.m_Orbit.Epoch().getDate(),self.m_Orbit.Epoch().getTime())
        gmt.addMin(tsince)

        eci = ECI(vecPos, vecVel, gmt)
        return eci