import random
import pygame
import math
import config
import sys
import heapq

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

    def d2Beacons(self, pos):
        distance = float("inf")
        for beacon in self.beacons:
            d = math.hypot(beacon[0]-pos[0]//config.BLOCK_WIDTH, beacon[1]-pos[1]//config.BLOCK_HEIGHT)
            if(d < distance):
                distance = d
        return Noise.add_noise(1, distance)

    def h(self, source, dest):
        return math.hypot(source[0]-dest[0],source[1]-dest[1])

    def reconstruct_path(self, camefrom, current):
        total_path = []
        total_path.append(current)
        while(current in camefrom.keys()):
            current = camefrom[current]
            total_path.append(current)
        return list(reversed(total_path))

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
                return self.reconstruct_path(camefrom, current)

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
    def freePos(self, pos):
        if(pos[0] < 0 or pos[1] < 0 or pos[0] >= self.size[1] or pos[1] >= self.size[0]):
            return False
        int_pos = (int(pos[0]),int(pos[1]))
        return self.pattern[int_pos[1]][int_pos[0]] == 0
    
    def getBlock(self, pos):
        return (int(pos[1]), int(pos[0]))


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
    print(lab.astar((0,13),(2,0)))

if __name__ == "__main__":
    main()