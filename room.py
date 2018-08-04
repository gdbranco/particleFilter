import random
import pygame
import math
import config
import sys
import heapq
import numpy as np
from scipy.misc import comb
from noise import Noise
class Room(object):
    # 0 Empty
    # 1 Occupied
    # 2 Occupied and has beacon on it
    def __init__(self, size, pattern):
        self.size = size
        self.pattern = pattern
        config.BLOCK_WIDTH = round(config.SCREEN_WIDTH / self.size[1])
        config.BLOCK_HEIGHT = round(config.SCREEN_HEIGHT / self.size[0])
        config.START_POS = (14*config.BLOCK_WIDTH + config.BLOCK_WIDTH/2,0 * config.BLOCK_HEIGHT + config.BLOCK_HEIGHT/2)
        self.beacons = []
        self.walls = []
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                if(self.pattern[j][i]==2):
                    self.beacons.append((i,j))
                if(self.pattern[j][i]!=0):
                    self.walls.append((i,j))

    def __str__(self):
        s = ""
        s += str(self.size[0]) + "x" + str(self.size[1])
        for i in range(self.size[0]):
            s += "\n"
            for j in range(self.size[1]):
                s += str(self.pattern[i][j]) + " "
        return s

    def getRect(self, pos):
        x = pos[0]
        y = pos[1]
        x = int(x*config.BLOCK_WIDTH)
        y = int(y*config.BLOCK_HEIGHT)
        return pygame.Rect(x,y, config.BLOCK_WIDTH, config.BLOCK_HEIGHT)

    def d2Beacons(self, pos, noise):
        distance = []
        for beacon in self.beacons:
            d = math.hypot(beacon[0]*config.BLOCK_WIDTH-pos[0], beacon[1]*config.BLOCK_HEIGHT-pos[1])
            if noise:
                distance.append(Noise.add_noise(19, d))
            else:
                distance.append(d)
        return np.array(distance)

    def h(self, source, dest):
        return math.hypot(source[0]-dest[0],source[1]-dest[1])

    def reconstruct_path(self, camefrom, current, source):
        total_path = []
        total_path.append((current[1]*config.BLOCK_WIDTH + config.BLOCK_WIDTH/2, current[0]*config.BLOCK_HEIGHT + config.BLOCK_HEIGHT/2))
        while(current in camefrom.keys()):
            current = camefrom[current]
            total_path.append((current[1]*config.BLOCK_WIDTH + config.BLOCK_WIDTH/2, current[0]*config.BLOCK_HEIGHT + config.BLOCK_HEIGHT/2))

        total_path = list(reversed(total_path))
        # bezier_path = self.bezier_curve(total_path,50)
        # for i, p in enumerate(bezier_path):
        #     search_pos = (p[0]//config.BLOCK_WIDTH,p[1]//config.BLOCK_HEIGHT)
        #     if(not self.freePos((search_pos[1],search_pos[0]))):
        #         bezier_path[i] = self.closestFreePos(((search_pos[1], search_pos[0])))
        total_path = self.catmull_rom(total_path)
        return total_path
    def astar(self, source, dest):
        opens = []
        closeds = set()
        camefrom = {}
        gscore = {}    
        gscore[source] = 0
        heapq.heappush(opens, (self.h(source, dest), source))
        while(len(opens)):
            current = heapq.heappop(opens)[1]
            if(current == dest):
                return self.reconstruct_path(camefrom, current, source)

            closeds.add(current)
            neighbors = [(current[0]+1,current[1]), # S
                         (current[0]+1,current[1]-1), # SW
                         (current[0],current[1]-1), # W
                         (current[0]-1,current[1]-1), # NW
                         (current[0]-1,current[1]), # N
                         (current[0]-1,current[1]+1), #NE
                         (current[0],current[1]+1), # E
                         (current[0]+1,current[1]+1)] # SE
            # print("current: ", current)
            for n in neighbors:
                # print("n: ", n)
                # print("valid: ", self.isValidSpot(n))
                # input()
                if n in closeds or not self.freePos((n[1],n[0])):
                    continue
                
                t_gscore = gscore[current] + 1
                if(t_gscore >= gscore.get(n, float("inf"))):
                    continue
                
                camefrom[n] = current
                gscore[n] = t_gscore
                f = gscore[n] + self.h(n, dest)
                if n not in opens:
                    heapq.heappush(opens, (f, n))
        return set()

    def randomFreePos(self):
        while True:
            pos = self.randomPos()
            if self.freePos(pos):
                pos = list(pos)
                pos[0] *= config.BLOCK_WIDTH
                pos[1] *= config.BLOCK_HEIGHT
                return pos

    def randomPos(self):
        x = random.uniform(0, self.size[1])
        y = random.uniform(0, self.size[0])
        return (x, y)

    def closestFreePos(self, pos):
        neighbors = [(pos[0]+1,pos[1]), # S
                     #(pos[0]+1,pos[1]-1), # SW
                     (pos[0],pos[1]-1), # W
                     #(pos[0]-1,pos[1]-1), # NW
                     (pos[0]-1,pos[1]), # N
                     #(pos[0]-1,pos[1]+1), #NE
                     (pos[0],pos[1]+1)] # E
                     #(pos[0]+1,pos[1]+1)] # SE
        distance = float("inf")
        closest = None
        for n in enumerate(neighbors):
            if(not self.freePos((n[1], n[0]))):
                continue
            d = abs(pos[0] - n[0]) - abs(pos[1] - n[1])
            if(d < distance):
                distance, closest = d, n
        return (closest[1]*config.BLOCK_WIDTH + config.BLOCK_WIDTH/2, closest[0]*config.BLOCK_HEIGHT + config.BLOCK_HEIGHT/2)
        
    def freePos(self, pos):
        if(pos[0] < 0 or pos[1] < 0 or pos[0] >= self.size[1] or pos[1] >= self.size[0]):
            return False
        int_pos = (int(pos[0]),int(pos[1]))
        return self.pattern[int_pos[1]][int_pos[0]] == 0
    
    def getBlock(self, pos):
        return (int(pos[1]), int(pos[0]))

    def bernstein_poly(self, n, i, t):
        n-=1
        return comb(n, i) * ( t**i ) * (1 - t)**(n-i)

    def bezier_curve(self, points, nTimes=1000):

        nPoints = len(points)
        xPoints = np.array([p[0] for p in points])
        yPoints = np.array([p[1] for p in points])

        t = np.linspace(0.0, 1.0, nTimes)

        polynomial_array = np.array([self.bernstein_poly(nPoints, i, t) for i in range(0, nPoints)])
        xvals = np.dot(xPoints, polynomial_array)
        yvals = np.dot(yPoints, polynomial_array)

        return list(zip(xvals, yvals))

    def catmull_rom(self, P):
        cat_list = []
        for j in range( 1, len(P)-2 ): 
            for t in range( 10 ):
                p = self.spline_4p( t/10.0, P[j-1], P[j], P[j+1], P[j+2] )
                cat_list.append(p)
        cat_list.append(P[-2])
        cat_list.append(P[-1])
        cat_list.insert(0, P[0])
        return cat_list

    def spline_4p(self, t, p_1, p0, p1, p2 ):
            # wikipedia Catmull-Rom -> Cubic_Hermite_spline
            # 0 -> p0,  1 -> p1,  1/2 -> (- p_1 + 9 p0 + 9 p1 - p2) / 16
        # assert 0 <= t <= 1
        return tuple((
            t*((2-t)*t - 1)       * np.array(p_1)
            + (t*t*(3*t - 5) + 2) * np.array(p0)
            + t*((4 - 3*t)*t + 1) * np.array(p1)
            + ((t-1)*t**2)        * np.array(p2) ) / 2)
def main():
    lab = Room((11,14), ((0,0,0,0,1,1,1,1,1,1,1,1,0,0),
                         (0,1,1,1,1,1,1,1,1,1,0,0,0,0),
                         (0,1,1,1,1,1,1,0,0,0,0,1,1,1),
                         (0,1,1,1,1,1,0,0,0,0,0,0,1,1),
                         (0,1,1,1,1,1,0,0,0,0,0,0,1,1),
                         (0,0,0,0,1,1,1,1,1,0,0,0,1,1),
                         (1,1,1,0,1,1,1,1,1,0,0,0,1,1),
                         (0,0,1,0,1,1,0,0,0,0,0,0,1,1),
                         (0,0,1,0,0,0,0,0,0,0,0,0,1,1),
                         (0,0,0,0,0,0,0,1,1,1,1,1,1,1),
                         (0,0,1,0,0,1,1,1,1,1,1,1,1,1)))
    print(lab)
    path = lab.astar((0,13),(2,0))
    print(path)
if __name__ == "__main__":
    main()