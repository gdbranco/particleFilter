import math
import random
class Particle(object):
    def __init__(self, pos, direction=None, weight = 1):
        if direction is None:
            direction = random.uniform(0, 360)

        self.pos = pos
        self.direction = direction
        self.weight = weight
    
    def __str__(self):
        return "{} {} - {}".format(self.pos[0],self.pos[1],self.weight)

    def move(self, speed, checker=None):
        direction = self.direction
        r = math.radians(direction)
        dx = math.sin(r) * speed
        dy = math.cos(r) * speed
        newPos = (dx,dy)
        self.pos += newPos