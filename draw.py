import pygame
import math
from room import Room
from particle import Particle
import random
import bisect
import config

sigma2 = 0.9 ** 2
def w_gauss(a, b):
    error = a - b
    g = math.e ** -(error ** 2 / (2 * sigma2))
    return g

class WeightedDistribution(object):
    def __init__(self, state):
        accum = 0.0
        self.state = [p for p in state if p.weight > 0]
        self.distribution = []
        for x in self.state:
            accum += x.weight
            self.distribution.append(accum)

    def pick(self):
        try:
            return self.state[bisect.bisect_left(self.distribution, random.uniform(0, 1))]
        except IndexError:
            # Happens when all particles are improbable w=0
            return None

def compute_mean_point(particles):
    """
    Compute the mean for all particles that have a reasonably good weight.
    This is not part of the particle filter algorithm but rather an
    addition to show the "best belief" for current position.
    """

    m_x, m_y, m_count = 0, 0, 0
    for p in particles:
        m_count += p.weight
        m_x += p[0] * p.weight
        m_y += p[1] * p.weight

    if m_count == 0:
        return -1, -1, False

    m_x /= m_count
    m_y /= m_count

    # Now compute how good that mean is -- check how many particles
    # actually are in the immediate vicinity
    m_count = 0
    for p in particles:
        if math.hypot(p.x-m_x,p.y-m_y) < 1:
            m_count += 1

    return m_x, m_y, m_count > config.PARTICLE_COUNT * 0.95

class Draw:
    def __init__(self):
        pygame.display.set_caption("Particle Filter Demo")
        self.window = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.playing = 1
        self.room = Room((12,16),((1,0,0,0,0,1,1,1,2,1,1,1,1,0,0,1),
                                  (1,0,1,1,0,1,0,0,0,0,0,0,0,0,0,1),
                                  (1,0,1,1,0,1,0,0,0,0,0,0,0,1,1,1),
                                  (1,0,1,1,0,1,0,0,0,0,0,0,0,0,1,1),
                                  (1,0,1,1,0,1,0,0,0,0,0,0,0,0,1,1),
                                  (1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,1),
                                  (1,1,1,1,0,1,1,1,1,1,1,0,0,0,1,1),
                                  (1,0,0,1,0,1,1,1,1,1,2,0,0,0,1,1),
                                  (1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1),
                                  (1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1),
                                  (1,0,0,1,2,1,1,1,1,1,1,1,1,1,1,1),
                                  (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)))
        self.person = Particle(self.room.randomFreePos(), (0, 255, 0), 10)
        self.particles = [Particle(self.room.randomFreePos()) for i in range(config.PARTICLE_COUNT)]
    
    def draw_grid(self):
        for x in range(0, config.SCREEN_WIDTH, config.BLOCK_WIDTH):
            pygame.draw.line(self.screen, config.TEXT_COLOR, (x,0), (x, config.SCREEN_HEIGHT))
        for y in range(0, config.SCREEN_HEIGHT, config.BLOCK_HEIGHT):
            pygame.draw.line(self.screen, config.TEXT_COLOR, (0, y), (config.SCREEN_WIDTH, y))

    def draw_room(self):
        for i in range(self.room.size[1]):
            for j in range(self.room.size[0]):
                if self.room.pattern[j][i] == 0:
                    pygame.draw.rect(self.screen, config.COLOR_EMPTY, pygame.Rect(i*config.BLOCK_WIDTH, j*config.BLOCK_HEIGHT, config.BLOCK_WIDTH, config.BLOCK_HEIGHT))
                elif(self.room.pattern[j][i] == 2):
                    pygame.draw.rect(self.screen, config.COLOR_BEACON, pygame.Rect(i*config.BLOCK_WIDTH, j*config.BLOCK_HEIGHT, config.BLOCK_WIDTH, config.BLOCK_HEIGHT))
                else:
                    pygame.draw.rect(self.screen, config.COLOR_WALL, pygame.Rect(i*config.BLOCK_WIDTH, j*config.BLOCK_HEIGHT, config.BLOCK_WIDTH, config.BLOCK_HEIGHT))

    def draw_particles(self):
        for particle in self.particles:
            particle.draw(self.screen, self.room)
        self.person.draw(self.screen, self.room)

    def draw(self):
        self.screen.fill(config.COLOR_BG)
        self.draw_room()
        self.draw_particles()
        self.draw_grid()

    def update(self, dt):
        p_d = self.person.read_sensor(self.room)
        nu = 0
        for particle in self.particles:
            if(self.room.freePos((particle.pos[0]//config.BLOCK_WIDTH,particle.pos[1]//config.BLOCK_HEIGHT))):
                pt_d = particle.read_sensor(self.room)
                particle.weight = w_gauss(p_d, pt_d)
                nu += particle.weight
            else:
                particle.weight = 0
            particle.color = particle.w2color(particle.weight)
        
        new_particles = []
        if nu:
            for p in self.particles:
                p.weight /= nu

        dist = WeightedDistribution(self.particles)

        for i in range(len(self.particles)):
            p = dist.pick()
            if p is None:
                new_particle = Particle(self.room.randomFreePos())
            else:
                new_particle = Particle(p.pos, noise=True)
            new_particles.append(new_particle)
        self.particles = new_particles
        #update stuff
        self.person.update(self.room)
        for p in self.particles:
            p.follow(self.person.vel)

    def play(self):
        while True:
            dt = self.clock.tick(config.FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
            if self.playing == config.PLAYING:
                self.update(dt)
                self.draw()
            pygame.display.update()
            pygame.display.set_caption("acc {}".format(self.person.acc))

def main():
    pygame.init()
    Draw().play()
    pygame.quit()

if __name__ == "__main__":
    main()