import math

class Vector:
    def __init__(self, x=.0, y=.0, z=.0, w=.0):
        self.m_x = x
        self.m_y = y
        self.m_z = z
        self.m_w = w

    def mul(self, factor):
        self.m_x *= factor
        self.m_y *= factor
        self.m_z *= factor
        self.m_w *= abs(factor)
    
    def sub(self, vec):
        self.m_x -= vec.m_x
        self.m_y -= vec.m_y
        self.m_z -= vec.m_z
        self.m_w -= vec.m_w

    def angle(self, vec):
        return math.acos(self.dot(vec) / (self.magnitude() * vec.magnitude()))

    def magnitude(self):
        return math.sqrt((self.m_x * self.m_x) +\
                   (self.m_y * self.m_y) +\
                   (self.m_z * self.m_z))
    
    def dot(self, vec):
        return (self.m_x * vec.m_x) +\
          (self.m_y * vec.m_y) +\
          (self.m_z * vec.m_z)
