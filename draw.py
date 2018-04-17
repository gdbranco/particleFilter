import pygame
import math
from room import Room
from particle import Particle

COLOR_BG = (45, 45, 45)
COLOR_EMPTY = (255, 255, 255)
COLOR_OCCUPIED = (0, 0, 0)
COLOR_BEACON = (0, 0, 255)
COLOR_PARTICLE = (255, 0, 0)
WORLD_SIZE = (14, 11)
TEXT_COLOR = (255, 255, 255)
SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280
BLOCK_HEIGHT = math.ceil(SCREEN_HEIGHT / WORLD_SIZE[1])
BLOCK_WIDTH = math.ceil(SCREEN_WIDTH / WORLD_SIZE[0])
FPS = 60
PLAYING = 1
PARTICLE_COUNT = 2000
class Draw:
    def __init__(self):
        pygame.display.set_caption("Particle Filter Demo")
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.playing = 1
        self.room = Room((11,14), ((0,0,0,0,1,1,1,1,1,1,1,1,0,0),
                         (0,1,1,0,1,0,0,0,0,0,0,0,0,0),
                         (0,1,1,0,1,0,0,0,0,0,0,0,1,1),
                         (0,1,1,0,1,0,0,0,0,0,0,0,0,1),
                         (0,1,1,0,1,0,0,0,0,0,0,0,0,1),
                         (0,0,0,0,1,0,0,0,0,0,0,0,0,1),
                         (1,1,1,0,1,1,1,1,1,1,0,0,0,1),
                         (0,0,1,0,1,1,1,1,1,1,0,0,0,1),
                         (0,0,1,0,0,0,0,0,0,0,0,0,0,1),
                         (0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                         (0,0,1,0,0,1,1,1,1,1,1,1,1,1)))
        self.world = pygame.Rect((0,0), self.room.size)
        self.particles = [Particle(self.room.randomFreePos()) for i in range(PARTICLE_COUNT)]
    
    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, BLOCK_WIDTH):
            pygame.draw.line(self.screen, TEXT_COLOR, (x,0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, BLOCK_HEIGHT):
            pygame.draw.line(self.screen, TEXT_COLOR, (0, y), (SCREEN_WIDTH, y))

    def draw_room(self):
        for i in range(self.room.size[0]):
            for j in range(self.room.size[1]):
                if self.room.pattern[i][j] == 0:
                    pygame.draw.rect(self.screen, COLOR_EMPTY, pygame.Rect(j*BLOCK_WIDTH, i*BLOCK_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT))

    def draw_particles(self):
        for particle in self.particles:
            pygame.draw.circle(self.screen, COLOR_PARTICLE, (int(particle.pos[0]*BLOCK_WIDTH), int(particle.pos[1]*BLOCK_HEIGHT)), 5, 5)

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.draw_grid()
        self.draw_room()
        self.draw_particles()
    
    def update(self, dt):
        pass

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


def main():
    pygame.init()
    Draw().play()
    pygame.quit()

if __name__ == "__main__":
    main()