import math
import random
import pygame
from config import *

Vector2D = pygame.math.Vector2

def add_noise(level, *coords):
    return [x + random.uniform(-level, level) for x in coords]

def add_some_noise(*coords):
    return add_noise(0.1, *coords)

class Particle(object):
    def __init__(self, pos, color = None, radius = 5, weight = 1, noise = False):
        if noise:
            pos[0], pos[1] = add_some_noise(pos[0],pos[1])
        self.pos = Vector2D(pos)
        self.vel = Vector2D(0,0)
        self.direction = random.uniform(0, 360)
        self.acc = Vector2D(math.cos(math.radians(self.direction)), math.sin(math.radians(self.direction)))
        self.weight = random.uniform(0, 1)
        self.color = color
        if(color is None):
            self.color = self.w2color(self.weight)
        self.radius = radius

    def __str__(self):
        return "({}, {}) - {}".format(self.pos[0],self.pos[1],self.weight)

    def read_sensor(self, room):
        return room.d2NearestBeacon(self.pos)

    def w2color(self, weight):
        return (int(weight*255), 0, int((1-weight)*255))

    def getRect(self, room):
        return pygame.Rect((self.pos[0]*room.BLOCK_WIDTH)-self.radius, (self.pos[1]*room.BLOCK_HEIGHT)-self.radius, self.radius*2, self.radius*2)

    def draw(self, screen, room):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]*room.BLOCK_WIDTH), int(self.pos[1]*room.BLOCK_HEIGHT)), self.radius, 0)

    def bounce_bounds(self, pos, room):
        normal = self.acc
        if(int(pos[0]*room.BLOCK_WIDTH)-self.radius <= 0 or int(pos[0]*room.BLOCK_WIDTH)+self.radius >= room.size[1]*room.BLOCK_WIDTH):
            normal[0] *= -1
        elif(int(pos[1]*room.BLOCK_HEIGHT)-self.radius <= 0 or int(pos[1]*room.BLOCK_HEIGHT)+self.radius >= room.size[0]*room.BLOCK_HEIGHT):
            normal[1] *= -1
        return normal

    def bounce_walls(self, pos, room):
        #base on https://gamedev.stackexchange.com/questions/61705/pygame-colliderect-but-how-do-they-collide
        normal = self.acc
        rect = room.getRect(pos)
        me = self.getRect(room)
        ar = math.atan2(me.centery - me.top, me.right - me.centerx) # half of the angle of the right side
        # construct the corner angles into an array to search for index such that the index indicates direction
        # this is normalized into [0, 2π] to make searches easier (no negative numbers and stuff) 
        dirint = [ 2*ar, math.pi, math.pi+2*ar, 2*math.pi]
        # calculate angle towars the center of the other rectangle, + ar for normalization into
        ad = math.atan2(me.centery - rect.centery, rect.centerx - me.centerx) + ar
        # again normalization, sincen atan2 ouputs values in the range of [-π,π]
        if ad < 0:
            ad = 2*math.pi + ad
        # search for the quadrant we are in and return it
        for i in range(len(dirint)):
            if ad < dirint[i]:
                dir = i
                break
        if(dir == 0 or dir == 2):
            normal[0]*=-1
        else:
            normal[1]*=-1
        return normal

    def reflect(self, pos, room):
        #REFLECT OF BOUNDS OF SCREEN
        normal = self.bounce_bounds(pos, room)
        #REFLECT OF WALLS
        if(not room.freePos(pos)):
            normal = self.bounce_walls(pos, room)
        return normal

    def update(self, dt, room):
        old_pos = self.pos
        old_direction = self.direction
        #self.direction = math.degrees(math.atan(self.acc[1]/self.acc[0]))
        #self.direction = self.direction + 180 if self.direction < 0 else self.direction
        self.acc = self.reflect(old_pos, room)
        if(self.acc.length() > MAX_ACC):
            self.acc.scale_to_length(MAX_ACC)
        self.vel += self.acc
        self.vel *= dt
        if(self.vel.length() > MAX_SPEED):
            self.vel.scale_to_length(MAX_SPEED)
        new_pos = old_pos + self.vel
        self.pos = new_pos

    def follow(self, dt, new_acc):
        self.vel += new_acc
        self.vel *= dt
        self.pos += self.vel