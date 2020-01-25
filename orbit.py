from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from sgp4.propagation import sgp4

minutes_per_day = 1440.
tle1 = "1 25994           19355.00000000  .00000084  00000-0  18613-4 0 00000"
tle2 = "2 25994 098.2118 066.7845 0001041 114.3599 185.8016 14.57112272000016"
satellite = twoline2rv(tle1, tle2, wgs72)
# 2440587.5
j = (1576919521.235 / (86400.)) + 2440587.5 # - 1
m = (j - satellite.jdsatepoch) * minutes_per_day

print(j, satellite.jdsatepoch, m)
p,v =  sgp4(satellite, m)
print([i*1000 for i in p])