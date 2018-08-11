COLOR_BG = (0, 0, 0)
COLOR_WALL = (45, 45, 45)
COLOR_EMPTY = (255, 255, 255)
COLOR_OCCUPIED = (0, 0, 0)
COLOR_BEACON = (0, 0, 255)
COLOR_MPARTICLE = (200, 200, 0)
TEXT_GRID = (242, 242, 242)
TEXT_COLOR = (255, 0, 0)
SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280
BLOCK_WIDTH = -1
BLOCK_HEIGHT = -1
FPS = 30
PLAYING = 1
PARTICLE_COUNT = 250
MAX_SPEED = 5
MAX_ACC = 1
############################################
GAUSSIAN_SIGMA = 2.509
############################################
RESAMPLE = ["multinomial", "systematic", "stratified"]
RESAMPLE_INDEX = 0 % len(RESAMPLE)
POSITIONING_METHODS = ['particleFilter', 'evoParticleFilter', 'trilateration']
POSITIONING_METHODS_INDEX = 0 % len(POSITIONING_METHODS)
PF = 0
EPF = 1
TRI = 2
NUM_GENERATIONS = 1
##############################################
MIN_DIST = 50
START_POS = None
LOAD = False
SAVE = False
LOG = False
REVERSE_PATH = False