import math
import random
import pygame
import config
from noise import Noise

Vector2D = pygame.math.Vector2

class Particle(object):
    def __init__(self, pos, color = None, radius = 5, weight = 1, noise = False):
        posx = pos[0]
        posy = pos[1]
        if noise:
            posx = Noise.add_noise(5, pos[0])
            posy = Noise.add_noise(5, pos[1])
        self.pos = Vector2D((posx,posy))
        self.vel = Vector2D(0,0)
        self.direction = random.uniform(0, 360)
        #self.acc = Vector2D(math.cos(math.radians(self.direction)), math.sin(math.radians(self.direction)))
        self.acc = Vector2D(random.uniform(0, 1), random.uniform(0, 1))
        self.acc *= config.MAX_ACC
        self.acc.rotate_ip(self.direction)
        self.weight = weight if weight != 1 else random.uniform(0,1)
        self.color = color
        self.target = 0
        if(color is None):
            self.color = self.w2color(self.weight)
        self.radius = radius

    def __str__(self):
        return "({}, {}) - {}".format(self.pos[0],self.pos[1],self.weight)

    def read_sensor(self, room):
        return room.d2Beacons(self.pos)

    def w2color(self, weight):
        return (int(weight*255), 0, int((1-weight)*255))

    def getRect(self):
        return pygame.Rect(self.pos[0]-self.radius, self.pos[1]-self.radius, self.radius*2, self.radius*2)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius, 0)

    def bounce_bounds(self, pos, room):
        if(pos[0]-self.radius <= 0 or pos[0]+self.radius >= room.size[1]*config.BLOCK_WIDTH):
            self.vel[0] *= -1
            self.acc[0] *= -1
        elif(pos[1]-self.radius <= 0 or pos[1]+self.radius >= room.size[0]*config.BLOCK_HEIGHT):
            self.vel[1] *= -1
            self.acc[1] *= -1

    def bounce_wall(self, ball, wall):
        # #base on https://gamedev.stackexchange.com/questions/61705/pygame-colliderect-but-how-do-they-
        # ar = math.atan2(ball.centery - ball.top, ball.right - ball.centerx) # half of the angle of the right side
        # # construct the corner angles into an array to search for index such that the index indicates direction
        # # this is normalized into [0, 2π] to make searches easier (no negative numbers and stuff) 
        # dirint = [ 2*ar, math.pi, math.pi+2*ar, 2*math.pi]
        # # calculate angle towars the center of the other rectangle, + ar for normalization into
        # ad = math.atan2(ball.centery - wall.centery, wall.centerx - ball.centerx) + ar
        # # again normalization, sincen atan2 ouputs values in the range of [-π,π]
        # if ad < 0:
        #     ad = 2*math.pi + ad
        # # search for the quadrant we are in and return it
        # for i in range(len(dirint)):
        #     if ad < dirint[i]:
        #         dir = i
        #         break
        # if(dir%2==0):
        #     self.vel[0]*=-1
        #     self.acc[0]*=-1
        # else:
        #     self.vel[1]*=-1
        #     self.acc[1]*=-1

        # Bounce cleanly off a 'floor' - no change in horizontal speed
        if (wall.left < ball.centerx < wall.right):
            vbounce = ball.centery - wall.centery
            hbounce = 0

		# Bounce cleanly off a 'wall' - no change in vertical speed
        elif wall.top < ball.centery < wall.bottom:
            vbounce = 0
            hbounce = ball.centerx - wall.centerx
			
		# Otherwise, bounce off the corner
        else:
            vbounce = ball.centery - wall.centery
            hbounce = ball.centerx - wall.centerx

        if vbounce>0:
            self.vel[1] = abs(self.vel[1])
            self.acc[1] = abs(self.acc[1])
        elif vbounce<0:
            self.vel[1] = -abs(self.vel[1])
            self.acc[1] = -abs(self.acc[1])
        if hbounce>0:
            self.vel[0] = abs(self.vel[0])
            self.acc[0] = abs(self.acc[0])
        elif hbounce<0:
            self.vel[0] = -abs(self.vel[0])
            self.acc[0] = -abs(self.acc[0])

    def reflect(self, pos, room):
        #REFLECT OF BOUNDS OF SCREEN
        self.bounce_bounds(pos, room)
        #REFLECT OF WALLS
        ball = self.getRect()
        for wall in room.walls:
            rWall = room.getRect(wall)
            if(rWall.colliderect(ball)):
                self.bounce_wall(ball, rWall)

    def update(self, room, target_list):
        #self.direction = math.degrees(math.atan(self.acc[1]/self.acc[0]))
        #self.direction = self.direction + 180 if self.direction < 0 else self.direction
        move_vector = None
        if(len(target_list) > 1):
            if(self.target):
                target = target_list[self.target]
                target_vector = target - self.pos
                if(target_vector.length() < 2):
                    self.target += 1
                    if(self.target == len(target_list)):
                        self.target = False
                move_vector = target_vector.normalize()
                self.pos = self.pos + move_vector
        return move_vector, self.target
                
    def follow(self, move_vector):
        if(move_vector is not None):
            self.pos += move_vector