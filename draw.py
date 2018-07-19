import pygame
import math

# My stuff
import config
from room import Room
from noise import Noise
from particle import Particle
from resample import Resample


def w_gauss(a, b):
    sigma2 = .9 ** 2
    error = (a - b) ** 2
    g = math.e ** -(error ** 2 / (2 * sigma2))
    return g

def meanEstimative(particles):
        m_x, m_y, m_count = 0, 0, 0
        for p in particles:
            m_count += p.weight
            m_x += p.pos[0] * p.weight
            m_y += p.pos[1] * p.weight
        if m_count == 0:
            return Particle((-1, -1), (0,0,0)), False
        m_x /= m_count
        m_y /= m_count
        
        m_count = 0
        for p in particles:
            if math.hypot(p.pos[0]-m_x,p.pos[1]-m_y) < config.MIN_DIST:
                m_count += 1
        return Particle((m_x, m_y),(255,255,0), 10), m_count > config.PARTICLE_COUNT * 0.95

class Draw:
    def __init__(self):
        pygame.display.set_caption("Particle Filter Demo")
        pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
        self.font = pygame.font.SysFont('Arial', 30)
        self.help = False
        self.set_conf = False
        self.path = False
        self.point_list = []
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
        self.reset()
    
    def reset(self, p=1):
        if(p):
            self.person = Particle((14*config.BLOCK_WIDTH + config.BLOCK_WIDTH/2,0 * config.BLOCK_HEIGHT + config.BLOCK_HEIGHT/2), (0, 255, 0), 10)
            self.path = False
        self.conf = False
        self.particles = [Particle(self.room.randomFreePos()) for i in range(config.PARTICLE_COUNT)]
        self.mparticle = [Particle(self.room.randomFreePos(), config.COLOR_MPARTICLE, 10)]

    def draw_grid(self):
        for x in range(0, config.SCREEN_WIDTH, config.BLOCK_WIDTH):
            pygame.draw.line(self.screen, config.TEXT_GRID, (x,0), (x, config.SCREEN_HEIGHT))
        for y in range(0, config.SCREEN_HEIGHT, config.BLOCK_HEIGHT):
            pygame.draw.line(self.screen, config.TEXT_GRID, (0, y), (config.SCREEN_WIDTH, y))

    def draw_room(self):
        for i in range(self.room.size[1]):
            for j in range(self.room.size[0]):
                if self.room.pattern[j][i] == 0:
                    pygame.draw.rect(self.screen, config.COLOR_EMPTY, pygame.Rect(i*config.BLOCK_WIDTH, j*config.BLOCK_HEIGHT, config.BLOCK_WIDTH, config.BLOCK_HEIGHT))
                elif(self.room.pattern[j][i] == 2):
                    pygame.draw.rect(self.screen, config.COLOR_BEACON, pygame.Rect(i*config.BLOCK_WIDTH, j*config.BLOCK_HEIGHT, config.BLOCK_WIDTH, config.BLOCK_HEIGHT))
                else:
                    pygame.draw.rect(self.screen, config.COLOR_WALL, pygame.Rect(i*config.BLOCK_WIDTH, j*config.BLOCK_HEIGHT, config.BLOCK_WIDTH, config.BLOCK_HEIGHT))


    def draw_text(self, text, p):
        self.screen.blit(self.font.render(text, 1, config.TEXT_COLOR), p)

    def draw_help(self):
        pygame.draw.rect(self.screen, config.COLOR_EMPTY, pygame.Rect(int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.70), 500, 200))
        self.draw_text("Resampling Method: {}".format(config.RESAMPLE[config.RESAMPLE_INDEX]), (int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.71)))
        self.draw_text("Person: {}".format(self.person.pos), (int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.75)))
        self.draw_text("Estimative: {}".format(self.mparticle.pos), (int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.79)))
        self.draw_text("Error: {}".format(math.hypot(self.person.pos[0]-self.mparticle.pos[0], self.person.pos[1]-self.mparticle.pos[1])), (int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.83)))

    def draw_particles(self):
        for particle in self.particles:
            particle.draw(self.screen)
        self.person.draw(self.screen)
        if self.conf or self.set_conf:
            self.mparticle.draw(self.screen)

    def draw_path(self):
        if(len(self.point_list) > 1):
            pygame.draw.lines(self.screen, (255, 0, 0), False, self.point_list, 5)

    def draw(self):
        self.screen.fill(config.COLOR_BG)
        self.draw_room()
        self.draw_particles()
        self.draw_grid()
        if(self.help):
            self.draw_help()
        if(self.path):
            self.draw_path()

    def update(self):
        p_d = self.person.read_sensor(self.room)
        somaPeso = 0
        for particle in self.particles:
            if(self.room.freePos((particle.pos[0]//config.BLOCK_WIDTH,particle.pos[1]//config.BLOCK_HEIGHT))):
                pt_d = Noise.add_noise(2, particle.read_sensor(self.room))
                particle.weight = sorted(w_gauss(p_d, pt_d))[0]
                somaPeso += particle.weight
            else:
                particle.weight = 0
            particle.color = particle.w2color(particle.weight)
        
        # RESAMPLE STUFF
        new_particles = []
        pesos = [particle.weight for particle in self.particles]
        dist = Resample(pesos, somaPeso)
        indices = dist.pick(config.RESAMPLE[config.RESAMPLE_INDEX])
        # CROSSOVER STUFF
        # MUTATE STUFF
        for i in indices:
            new_particles.append(Particle(self.particles[i].pos, noise=True))
        self.particles = new_particles
        # UPDATE STUFF
        self.mparticle, self.conf = meanEstimative(self.particles)
        move_vector = self.person.update(self.room, self.point_list)
        for p in self.particles:
           p.follow(move_vector)

    def handle_input(self, e):
        if(e.key == pygame.K_r): # Restart Everyhing
            self.reset()
        elif(e.key == pygame.K_LSHIFT): # Restart particles
            self.reset(p=0)
        elif(e.key == pygame.K_s): # Change selection type
            config.RESAMPLE_INDEX = (config.RESAMPLE_INDEX + 1) % len(config.RESAMPLE)
        elif(e.key == pygame.K_h): # HELP
            self.help = not self.help
        elif(e.key == pygame.K_c):
            self.set_conf = not self.set_conf
            
    def play(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                elif e.type == pygame.KEYDOWN:
                    self.handle_input(e)
                elif e.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    dest = (pos[0]//config.BLOCK_WIDTH, pos[1]//config.BLOCK_HEIGHT)
                    source = (self.person.pos[0]//config.BLOCK_WIDTH, self.person.pos[1]//config.BLOCK_HEIGHT)
                    self.point_list = self.room.astar((source[1],source[0]), (dest[1],dest[0]))
                    self.person.target = 1
                    self.path = True
            if self.playing == config.PLAYING:
                self.update()
                self.draw()
            pygame.display.update()

def main():
    pygame.init()
    Draw().play()
    pygame.quit()

if __name__ == "__main__":
    main()