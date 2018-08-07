import pygame
import math
import numpy as np
import json

# My stuff
import config
from room import Room
from noise import Noise
from particle import Particle
from resample import Resample
import random

def gaussian_kernel(x, sigma):
    # http://www.stat.wisc.edu/~mchung/teaching/MIA/reading/diffusion.gaussian.kernel.pdf.pdf
    g = (math.e ** -(x ** 2 / (2 * sigma **2))) * (1 / math.sqrt(math.pi * 2) * sigma)
    # g = (math.e ** -(x ** 2 / (2 * sigma **2)))
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

        return (m_x, m_y)


def trilaterar(p1, p2, p3, d1, d2, d3):
    p2p1Distance = ((p2[0]-p1[0])**2 + (p2[1] - p1[1])**2)**(1/2)
    exx = (p2[0]-p1[0])/p2p1Distance
    exy = (p2[1]-p1[1])/p2p1Distance

    i = exx*(p3[0]-p1[0]) + exy * (p3[1]-p1[1])
    iexx = p3[0]-p1[0]-i*exx
    iexy = p3[1]-p1[1]-i*exy
    eyx = (iexx)/(iexx**2 + iexy**2)**(1/2)
    eyy = (iexy)/(iexx**2 + iexy**2)**(1/2)

    j = eyx*(p3[0]-p1[0])+eyy*(p3[1]-p1[1])

    x = (d1**2 - d2**2 + p2p1Distance**2)/(2*p2p1Distance)
    y = (d1**2 - d3**2 + i**2 + j**2)/(2*j) - i*x/j

    fx = p1[0] + x*exx + y*eyx
    fy = p1[1] + x*exy + y*eyy

    return (fx, fy)

class Draw:
    def __init__(self, fload, fsave, flog):
        pygame.display.set_caption("Particle Filter Demo")
        pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
        if config.LOAD:
            self.load_file = fload
        if config.SAVE:
            self.save_file = fsave
        if config.LOG:
            self.log_file = open(flog, 'w', newline='')
            self.log_file.write("x_sim, y_sim, e_x_sim, e_y_sim, error_sim, x_real, y_real, e_x_real, e_y_real, error_real\n")
        self.font = pygame.font.SysFont('Arial', 30)
        self.help = False
        self.set_conf = False
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
        self.min_error = float('inf')
        self.max_error = float('-inf')
    
    def reset(self, p=1):
        if(p):
            #self.person = Particle(self.room.randomFreePos(), (0, 255, 0), 10)    
            self.point_list = [] if not config.LOAD else load_movement(self.load_file)
            self.person = Particle(config.START_POS, (0, 255, 0), 10)
            self.person.target = False if self.point_list == [] else True
            self.path = False if self.point_list == [] else True
            self.set_conf = False if self.point_list == [] else True
        self.particles = [Particle(self.room.randomFreePos()) for i in range(config.PARTICLE_COUNT)]
        self.mparticle = Particle(self.room.randomFreePos(), config.COLOR_MPARTICLE, 10)

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

    def draw_help(self, pos, estimative):
        error = math.hypot(pos[0]-estimative[0], pos[1]-estimative[1])
        pygame.draw.rect(self.screen, config.COLOR_EMPTY, pygame.Rect(int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.70), 500, 200))
        if config.POSITIONING_METHODS_INDEX in [config.PF, config.EPF]:
            self.draw_text("Resampling Method: {}".format(config.RESAMPLE[config.RESAMPLE_INDEX]), (int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.71)))
        self.draw_text(f"Person: {pos}", (int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.75)))
        self.draw_text(f"Estimative: {estimative}", (int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.79)))
        self.draw_text(f"Error: {error}", (int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.83)))
        self.draw_text(f"Min Error: {self.min_error}",(int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.87)))
        self.draw_text(f'Max Error: {self.max_error}',(int(config.SCREEN_WIDTH*0.6), int(config.SCREEN_HEIGHT*0.91)))

    def draw_particles(self):
        if config.POSITIONING_METHODS_INDEX in [config.PF, config.EPF]:
            for particle in self.particles:
                particle.draw(self.screen)
        self.person.draw(self.screen)
        if self.set_conf:
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
           self.draw_help(self.person.pos, self.mparticle.pos)
        if(self.path):
           self.draw_path()

    def log(self, pos, estimative):
        error_pixels = math.hypot(pos[0]-estimative[0], pos[1]-estimative[1])
        pos_converted = ((pos[0]*9.3)/1280, (pos[1]*6.82)/720)
        estimative_converted = ((estimative[0]*9.3)/1280, (estimative[1]*6.82)/720)
        error_converted = math.hypot(pos_converted[0]-estimative_converted[0], pos_converted[1]-estimative_converted[1])
        self.log_file.write(f"{pos[0]}, {pos[1]}, {estimative[0]}, {estimative[1]}, {error_pixels}, {pos_converted[0]}, {pos_converted[1]}, {estimative_converted[0]}, {estimative_converted[1]}, {error_converted}\n")

    def update(self):
        # UPDATE STUFF
        move_vector, keep_alive = self.person.update(self.room, self.point_list)
        p_d = self.person.read_sensor(self.room, noise=True)
        if config.POSITIONING_METHODS_INDEX == config.PF:
            self.update_particleFilter(p_d)
            for p in self.particles:
                p.follow(move_vector)
            self.mparticle.pos = meanEstimative(self.particles)
        elif config.POSITIONING_METHODS_INDEX == config.EPF:
            self.update_evoParticleFilter(p_d)
            for p in self.particles:
                p.follow(move_vector)
            self.mparticle.pos = meanEstimative(self.particles)
        else:
            self.update_trilateration(p_d)
        if(not keep_alive and config.LOAD):
            self.log_file.close()
            exit()
        error = math.hypot(self.person.pos[0]-self.mparticle.pos[0], self.person.pos[1]-self.mparticle.pos[1])
        if(self.max_error < error):
            self.max_error = error
        if(self.min_error > error):
            self.min_error = error

    def update_trilateration(self, p_d):
        beacons = self.room.pixel_beacons
        self.mparticle.pos = trilaterar(beacons[0],beacons[1],beacons[2], p_d[0], p_d[1],p_d[2])

    def update_particleFilter(self, p_d):
        for particle in self.particles:
            if(self.room.freePos((particle.pos[0]//config.BLOCK_WIDTH,particle.pos[1]//config.BLOCK_HEIGHT))):
                pt_d = particle.read_sensor(self.room, noise=False)
                errors = abs(p_d - pt_d)
                particle.weight = gaussian_kernel(errors.mean(), config.GAUSSIAN_SIGMA)
            else:
                particle.weight = 0
        
        # RESAMPLE STUFF
        new_particles = []
        pesos = np.asarray([particle.weight for particle in self.particles])
        norm_pesos = (pesos - pesos.min()) / (pesos.max() - pesos.min())
        dist = Resample(norm_pesos)
        indices = dist.pick(config.RESAMPLE[config.RESAMPLE_INDEX])

        # MUTATE STUFF
        for i in indices:
            new = Particle(self.particles[i].pos, noise=True)
            if(self.room.freePos((new.pos[0]//config.BLOCK_WIDTH,new.pos[1]//config.BLOCK_HEIGHT))):
                d = new.read_sensor(self.room, False)
                errors = abs(p_d - d)
                new.weight = gaussian_kernel(errors.mean(), config.GAUSSIAN_SIGMA)
            else:
                new.weight = 0
            new_particles.append(new)
        self.particles = new_particles
        for p in self.particles:
            p.color = p.w2color(p.weight)

    def update_evoParticleFilter(self, p_d):
        new_particles = []
        for k in range(config.NUM_GENERATIONS):
            # SELECTION
            for particle in self.particles:
                if(self.room.freePos((particle.pos[0]//config.BLOCK_WIDTH, particle.pos[1]//config.BLOCK_HEIGHT))):
                    pt_d = particle.read_sensor(self.room, noise=False)
                    errors = abs(p_d - pt_d)
                    particle.weight = gaussian_kernel(errors.mean(), config.GAUSSIAN_SIGMA)
                else:
                    particle.weight = 0

            pesos = np.asarray([particle.weight for particle in self.particles])
            norm_pesos = (pesos - pesos.min()) / (pesos.max() - pesos.min())
            dist = Resample(norm_pesos)
            indices = dist.pick(config.RESAMPLE[config.RESAMPLE_INDEX])

            # CROSSOVER + MUTATION
            new_particles = []
            i=0
            j=len(self.particles)-1
            while i<j:
                mutation_prob1 = random.randint(0,10)
                mutation_prob2 = random.randint(0,10)
                child1 = Particle((self.particles[indices[i]].pos[0],self.particles[indices[j]].pos[1]), noise=False if mutation_prob1 > 1 else True)
                child2 = Particle((self.particles[indices[j]].pos[0],self.particles[indices[i]].pos[1]), noise=False if mutation_prob2 > 1 else True)
                i+=1
                j-=1
                new_particles.append(child1)
                new_particles.append(child2)
            self.particles = new_particles

        for p in self.particles:
            pt_d = p.read_sensor(self.room, noise=False)
            errors = abs(p_d - pt_d)
            p.weight = gaussian_kernel(errors.mean(), config.GAUSSIAN_SIGMA)
            p.color = p.w2color(p.weight)

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
                    if(config.SAVE and self.point_list != []):
                        save_movement(self.point_list, self.save_file)
                    self.person.target = True
                    self.path = True
            if self.playing == config.PLAYING:
                self.update()
                self.draw()
                if config.LOG:
                    self.log(self.person.pos, self.mparticle.pos)
            pygame.display.update()
            self.clock.tick(config.FPS)

def main(fload, fsave, flog):
    pygame.init()
    Draw(fload, fsave, flog).play()
    pygame.quit()

def save_movement(point_list, filename):
    with open(filename, 'w') as f:
        json.dump(point_list, f)

def load_movement(filename):
    with open(filename) as f:
        x = json.load(f)
    if(config.REVERSE_PATH):
        x = list(reversed(x))
    x += list(reversed(x))[1:]
    return x

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--save", help="Saves current movement list",type=str)
    parser.add_argument("-l","--load", help="Loads to current movement list",type=str)
    parser.add_argument("-log","--log",help="Logs statistics about current movement list", type=str)
    parser.add_argument("-pm","--pmethod",help="Select positioning method", type=str)
    parser.add_argument("-pa","--particle_amount", help="Amount of particles in each scenario", type=int)
    #parser.add_argument("-rv","--reverse", help="Reverse path in scenario", action="store_true")
    args = parser.parse_args()
    if args.save is not None:
        config.SAVE = True
    if args.load is not None:
        config.LOAD = True
    if args.log is not None:
        config.LOG = True
    if args.pmethod is not None:
        if args.pmethod == config.POSITIONING_METHODS[config.PF]:
            config.POSITIONING_METHODS_INDEX = config.PF
        elif args.pmethod == config.POSITIONING_METHODS[config.EPF]:
            config.POSITIONING_METHODS_INDEX = config.EPF
        else:
            config.POSITIONING_METHODS_INDEX = config.TRI
    # if args.reverse:
    #     config.REVERSED_PATH = True
    main(args.load, args.save, args.log)