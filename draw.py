import pygame
import math
from room import Room
from particle import Particle
from config import *

class Draw:
    def __init__(self):
        pygame.display.set_caption("Particle Filter Demo")
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.playing = 1
        self.room = Room((11,14),((0,0,0,0,1,1,1,1,1,1,1,1,0,0),
                                  (0,1,1,0,1,0,0,0,0,0,0,0,0,0),
                                  (0,1,1,0,1,0,0,0,0,0,0,0,1,1),
                                  (0,1,1,0,1,0,0,0,0,0,0,0,0,1),
                                  (0,1,1,0,1,0,0,0,0,0,0,0,0,1),
                                  (0,0,0,0,1,0,0,0,0,0,0,0,0,1),
                                  (1,1,1,0,1,1,1,1,1,1,0,0,0,1),
                                  (0,0,1,0,1,1,1,1,1,1,0,0,0,1),
                                  (0,0,1,0,0,0,0,0,0,0,0,0,0,1),
                                  (0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                                  (0,0,1,1,1,1,1,1,1,1,1,1,1,1)))
        self.person = Particle(self.room.randomFreePos(), (0, 255, 0), 10)
        self.particles = [Particle(self.room.randomFreePos()) for i in range(PARTICLE_COUNT)]
    
    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, self.room.BLOCK_WIDTH):
            pygame.draw.line(self.screen, TEXT_COLOR, (x,0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, self.room.BLOCK_HEIGHT):
            pygame.draw.line(self.screen, TEXT_COLOR, (0, y), (SCREEN_WIDTH, y))

    def draw_room(self):
        for i in range(self.room.size[1]):
            for j in range(self.room.size[0]):
                if self.room.pattern[j][i] == 0:
                    pygame.draw.rect(self.screen, COLOR_EMPTY, pygame.Rect(i*self.room.BLOCK_WIDTH, j*self.room.BLOCK_HEIGHT, self.room.BLOCK_WIDTH, self.room.BLOCK_HEIGHT))
                else:
                    pygame.draw.rect(self.screen, COLOR_WALL, pygame.Rect(i*self.room.BLOCK_WIDTH, j*self.room.BLOCK_HEIGHT, self.room.BLOCK_WIDTH, self.room.BLOCK_HEIGHT))

    def draw_particles(self):
        self.person.draw(self.screen, self.room)
        for particle in self.particles:
            particle.draw(self.screen, self.room)

    def draw(self):
        self.screen.fill(COLOR_BG)
        #self.draw_grid()
        self.draw_room()
        self.draw_particles()
    
    def update(self, dt):
        self.person.update(dt, self.room)
        for particle in self.particles:
            particle.follow(dt,self.person.acc)

    def play(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
            if self.playing == PLAYING:
                self.update(dt)
                self.draw()
            pygame.display.update()
            pygame.display.set_caption("pos {}".format(self.person.pos))

def main():
    pygame.init()
    Draw().play()
    pygame.quit()

if __name__ == "__main__":
    main()