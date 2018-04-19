import math
import random
import pygame
from config import *

Vector2D = pygame.math.Vector2

class Particle(object):
    def __init__(self, pos, color = None, radius = 5, weight = 1):
        self.pos = Vector2D(pos)
        self.vel = Vector2D(0,0)
        self.direction = random.uniform(0, 360)
        self.acc = Vector2D(math.cos(math.radians(self.direction)), math.sin(math.radians(self.direction)))
        self.weight = random.uniform(0, 1)
        self.color = color
        self.radius = radius

    def __str__(self):
        return "({}, {}) - {}".format(self.pos[0],self.pos[1],self.weight)

    def getRect(self):
        return pygame.Rect(self.pos[0]-self.radius, self.pos[1]-self.radius, self.radius*2, self.radius*2)

    def reflect(self, new_pos, room):
        normal = self.acc
        #REFLECT OF BOUNDS OF SCREEN
        if(new_pos[0]-(self.radius/room.BLOCK_WIDTH) <= 0 or new_pos[0]+(self.radius/room.BLOCK_WIDTH) >= room.size[1]):
            normal[0] = -normal[0]
        elif(new_pos[1]-(self.radius/room.BLOCK_HEIGHT) <= 0 or new_pos[1]+(self.radius/room.BLOCK_HEIGHT) >= room.size[0]):
            normal[1] = -normal[1]
        #REFLECT OF WALLS
        elif(not room.freePos(new_pos)):
            rect = room.getRect(new_pos)
            if(rect.colliderect(self.getRect())):
                print("reflect")
        # elif(not room.freePos(new_pos)):
        #     print(int(new_pos[0]*room.BLOCK_WIDTH), int(new_pos[1]*room.BLOCK_HEIGHT))
        #     print(rect.left, rect.right)
        #     print(rect.top, rect.bottom)
        #     print("reflect")
        #     if((int((new_pos[0]*room.BLOCK_WIDTH))+self.radius) >= rect.left or (int((new_pos[0]*room.BLOCK_WIDTH))-self.radius) <= rect.right):
        #         normal[0] = -normal[0]
        #     else:
        #         normal[1] = -normal[1]
        else:
            print("nothing")
        return normal

    def update(self, dt, room):
        old_pos = self.pos
        old_direction = self.direction
        #self.direction = math.degrees(math.atan(self.acc[1]/self.acc[0]))
        #self.direction = self.direction + 180 if self.direction < 0 else self.direction
        if(self.acc.length() > MAX_ACC):
            self.acc.scale_to_length(MAX_ACC)
        self.vel += self.acc
        self.vel *= dt
        if(self.vel.length() > MAX_SPEED):
            self.vel.scale_to_length(MAX_SPEED)
        new_pos = old_pos + self.vel
        self.acc = self.reflect(new_pos, room)
        self.pos = new_pos

    def move(self, speed, checker=None):
        direction = self.direction
        r = math.radians(direction)
        dx = math.sin(r) * speed
        dy = math.cos(r) * speed
        newPos = (dx,dy)
        self.pos += newPos