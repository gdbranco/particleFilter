import random
class Room(object):
    # 0 Empty
    # 1 Occupied
    # 2 Occupied and has beacon on it
    def __init__(self, size, pattern):
        self.size = size
        self.pattern = pattern
    def __str__(self):
        s = ""
        s += str(self.size[0]) + "x" + str(self.size[1])
        for i in range(self.size[0]):
            s += ""
            for j in range(self.size[1]):
                s += str(self.pattern[i][j]) + " "
        return s
    def randomFreePos(self):
        while True:
            pos = self.randomPos()
            if self.freePos(pos):
                return pos
    def randomPos(self):
        x = random.uniform(0, self.size[1])
        y = random.uniform(0, self.size[0])
        return (x, y)
    def freePos(self, pos):
        if(pos[0] < 0 or pos[1] < 0 or pos[0] > self.size[1] or pos[1] > self.size[0]):
            return False
        int_pos = (int(pos[0]),int(pos[1]))
        return self.pattern[int_pos[1]][int_pos[0]] == 0


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

if __name__ == "__main__":
    main()