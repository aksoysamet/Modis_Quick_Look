import math

X = 0
Y = 1
Z = 2

def calcRotation(opp, prevOpp):
    global X, Y, Z
    cur = [opp[X],opp[Y],opp[Z]]
    prev = [prevOpp[X],prevOpp[Y],prevOpp[Z]]
    curH = calcAngle(cur[X],cur[Y])
    curD = math.sqrt((cur[X]*cur[X]) + (cur[Y]*cur[Y]))
    cur[X] = curD * cos(0.0)
    cur[Y] = curD * sin(0.0)
    prevH = calcAngle(prev[X],prev[Y])
    prevH = (360.0 + (prevH - curH)) % 360.0
    prevD = math.sqrt((prev[X]*prev[X]) + (prev[Y]*prev[Y]))
    prev[X] = prevD * cos(prevH)
    prev[Y] = prevD * sin(prevH)
    curE = calcAngle(cur[X],cur[Z])
    curD = math.sqrt((cur[X]*cur[X]) + (cur[Z]*cur[Z]))
    cur[X] = curD * cos(0.0)
    cur[Z] = curD * sin(0.0)
    prevE = calcAngle(prev[X],prev[Z])
    prevE = (360.0 + (prevE - curE)) % 360.0
    prevD = math.sqrt((prev[X]*prev[X]) + (prev[Z]*prev[Z]))
    prev[X] = prevD * cos(prevE)
    prev[Z] = prevD * sin(prevE)
    R = calcAngle(prev[Y],prev[Z])
    R = (R + 270.0) % 360.0
    return R

def calcRay(scanAngle, trackAngle, scDistToOrig, scAlt):
    rayLength = .0
    earthRadius = scDistToOrig - scAlt
    try:
        rayAngle = acos((sin(scanAngle)*cos(trackAngle))/tan(scanAngle))
    except ZeroDivisionError:
        rayAngle = acos(0)
    if abs(rayAngle) > .0:
        angle1 = 180.0 - asin((scDistToOrig * sin(abs(rayAngle))) / earthRadius)
        angle2 = 180.0 - angle1 - abs(rayAngle)
        rayLength = (scDistToOrig * sin(angle2)) / sin(angle1)
    else:
        rayLength = scAlt
    return [rayLength*cos(scanAngle),rayLength*sin(scanAngle),rayLength*sin(trackAngle)]

def applyRotation(ray, rotation):
    global X, Y, Z
    if ray[Y] is .0 and ray[Z] is .0:
        return
    d = math.sqrt((ray[Y]*ray[Y]) + (ray[Z]*ray[Z]))
    a = calcAngle(ray[Y],ray[Z])
    a = (a + rotation) % 360.0
    ray[Y] = d * cos(a)
    ray[Z] = d * sin(a)

def applyElevation(ray, opp):
    global X, Y, Z
    if ray[X] is .0 and ray[Z] is .0:
        return
    oppXYd = math.sqrt((opp[X]*opp[X])+(opp[Y]*opp[Y]))
    oppAngle = (360.0 + atan(opp[Z]/oppXYd)) % 360.0
    rayAngle = calcAngle(ray[X],ray[Z])
    rayAngle = (rayAngle + oppAngle) % 360.0
    rayD = math.sqrt((ray[X]*ray[X]) + (ray[Z]*ray[Z]))
    ray[X] = rayD * cos(rayAngle)
    ray[Z] = rayD * sin(rayAngle)

def applyHeading(ray, opp):
    global X, Y, Z
    if ray[X] is .0 and ray[Y] is .0:
        return
    oppAngle = calcAngle(opp[X],opp[Y])
    rayAngle = calcAngle(ray[X],ray[Y])
    rayAngle = (rayAngle + oppAngle) % 360.0
    rayD = math.sqrt((ray[X]*ray[X]) + (ray[Y]*ray[Y]))
    ray[X] = rayD * cos(rayAngle)
    ray[Y] = rayD * sin(rayAngle)

def greenwichHourAngleJD(JD):
    rToD = 360.0 / (2*math.pi)
    solarDay = 1.0027379093
    jd2000 = JD - 2451545.5
    IJD = (JD+0.5) - 0.5
    fday = JD - IJD
    Tu = (IJD - 2451545.0) / 36525
    gmst = 24110.54841 +\
    		  (8640184.812866 * Tu) +\
		  (0.093104 * Tu * Tu) -\
		  (6.2e-6 * Tu * Tu * Tu)
    gmst = (gmst/86400.0) * 360.0
    xls = (280.46592 + 0.9856473516 * jd2000) % 360.0
    gs = (357.52772 + 0.9856002831 * jd2000) % 360.0
    xlm = (218.31643 + 13.17639648 * jd2000) % 360.0
    omega = (125.04452 - 0.052953768 * jd2000) % 360.0
    dpsi = (-17.1996 * math.sin(omega/rToD)) +\
    		  (0.2062 * math.sin(omega/rToD*2.0)) -\
		  (1.3187 * math.sin(xls/rToD*2.0)) +\
		  (0.1426 * math.sin(gs/rToD)) -\
		  (0.2274 * math.sin(xlm/rToD*2.0))
    epsm = 23.43929 - 3.560e-7 * jd2000
    deps = (9.2025 * math.cos(omega/rToD)) + (0.5736 * math.cos(2*xls/rToD))
    eps = epsm + (deps/3600)
    dpsi = dpsi / 3600
    gha = gmst + (dpsi * math.cos(eps/rToD)) + (fday * 360 * solarDay)
    return principleAngle(gha/rToD)

def principleAngle(angle):
    base = angle % (2*math.pi)
    return base + (2*math.pi) if base < .0 else base

def calcAngle(x, y):
    d = math.sqrt((x*x) + (y*y))
    try:
        angle = asin(y/d)
    except ZeroDivisionError:
        angle = asin(0)
    if x < 0:
      angle = 180.0 - angle
    elif (y < 0):
        angle = 360.0 + angle
    return angle

def modToRange(min, value, max):
    range = max - min
    while value < min:
      value += range
    while value > max:
      value -= range
    return value

def sin(degrees):
    return math.sin(math.radians(degrees))

def cos(degrees):
    return math.cos(math.radians(degrees))

def tan(degrees):
    return math.tan(math.radians(degrees))

def asin(value):
    return math.degrees(math.asin(min(1,max(value,-1))))

def acos(value):
    return math.degrees(math.acos(min(1,max(value,-1))))

def atan(value):
    return math.degrees(math.atan(value))