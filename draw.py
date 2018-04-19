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
        #self.particles = [Particle(self.room.randomFreePos()) for i in range(PARTICLE_COUNT)]
    
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

    def w2color(self, weight):
        return (int(weight*255), 0, int((1-weight)*255))

    def draw_particles(self):
        pygame.draw.circle(self.screen, self.person.color, (int(self.person.pos[0]*self.room.BLOCK_WIDTH), int(self.person.pos[1]*self.room.BLOCK_HEIGHT)), self.person.radius, 10)
        #for particle in self.particles:
        #    pygame.draw.circle(self.screen, self.w2color(particle.weight), (int(particle.pos[0]*self.BLOCK_WIDTH), int(particle.pos[1]*self.BLOCK_HEIGHT)), particle.radius, 5)

    def draw(self):
        self.screen.fill(COLOR_BG)
        #self.draw_grid()
        self.draw_room()
        self.draw_particles()
    
    def update(self, dt):
        self.person.update(dt, self.room)
        #for particle in self.particles:
        #    particle.update(dt)

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