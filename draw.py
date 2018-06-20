import pygame
import math
from room import Room
from particle import Particle
import random
import numpy as np
import bisect
import config

sigma2 = 0.9 ** 2
def w_gauss(a, b):
    error = a - b
    g = math.e ** -(error ** 2 / (2 * sigma2))
    return g

#Multimonial resample is not good will create new methods for this
class Resample(object):
    import numpy as np
    def __init__(self, state, norm):
        self.state = np.asarray(state)
        self.state = self.state / norm if norm else self.state
        self.cumsum = self.state.cumsum()
        self.cumsum[-1] = 1 # garantir que a soma termina em 1
    def pick(self, type="multinomial"):
        if(type=="multinomial"):
            self.state = sorted(self.state)
            return np.searchsorted(self.cumsum, np.random.random(len(self.state)))
        elif(type=="systematic"):
            N = len(self.state)
            # DIVIDIR EM N PARTES SELECIONANDO O MESMO RANDOM PARA TODOS
            posicoes = (np.random.random(N) + range(N)) / N
            indices = np.zeros(N, int)
            i, j = 0, 0
            while(i<N):
                if(posicoes[i] < self.cumsum[j]):
                    indices[i] = j
                    i+=1
                else:
                    j+=1
            return indices
        elif(type=="stratified"):
            N = len(self.state)
            # DIVIDIR EM N PARTES SELECIONANDO UM RANDOM PARA CADA PARTE
            posicoes = (np.random.random() + np.arange(N)) / N
            indices = np.zeros(N, int)
            i, j = 0, 0
            while(i<N):
                if(posicoes[i] < self.cumsum[j]):
                    indices[i] = j
                    i+=1
                else:
                    j+=1
            return indices
        else: # residual
            pass
def estimate(particles):
    m_x, m_y, m_count = 0, 0, 0
    for p in particles:
        m_count += p.weight
        m_x += p.pos[0] * p.weight
        m_y += p.pos[1] * p.weight

    if m_count == 0:
        return Particle((-1, -1), (0,0,0)), False

    m_x /= m_count
    m_y /= m_count
    # Now compute how good that mean is -- check how many particles
    # actually are in the immediate vicinity
    m_count = 0
    for p in particles:
        if math.hypot(p.pos[0]-m_x,p.pos[1]-m_y) < config.MIN_DIST:
            m_count += 1
    return Particle((m_x, m_y),(255,255,0), 10), m_count > config.PARTICLE_COUNT * 0.95

class Draw:
    def __init__(self):
        pygame.display.set_caption("Particle Filter Demo")
        self.window = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.playing = 1
        self.conf = False
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
        self.mparticle = [Particle(self.room.randomFreePos(), (255, 255, 0), 10)]
    
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
            particle.draw(self.screen)
        self.person.draw(self.screen)
        if self.conf:
            self.mparticle.draw(self.screen)

    def draw(self):
        self.screen.fill(config.COLOR_BG)
        self.draw_room()
        self.draw_particles()
        self.draw_grid()

    def update(self, dt):
        p_d = self.person.read_sensor(self.room)
        somaPeso = 0
        for particle in self.particles:
            if(self.room.freePos((particle.pos[0]//config.BLOCK_WIDTH,particle.pos[1]//config.BLOCK_HEIGHT))):
                pt_d = particle.read_sensor(self.room)
                particle.weight = w_gauss(p_d, pt_d)
                somaPeso += particle.weight
            else:
                particle.weight = 0
            particle.color = particle.w2color(particle.weight)
        
        # RESAMPLE STUFF
        new_particles = []
        pesos = [particle.weight for particle in self.particles]
        dist = Resample(pesos, somaPeso)
        indices = dist.pick(config.RESAMPLE)
        for i in indices:
            new_particles.append(Particle(self.particles[i].pos, noise=True))
        self.particles = new_particles
        #update stuff
        self.mparticle, self.conf = estimate(self.particles)
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
    # r = Resample([1,2,3,4,5], 15)
    # print(r.pick("systematic"))
    # print(r.pick("stratified"))
    # print(r.pick())