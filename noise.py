from random import uniform
class Noise(object):
    @staticmethod
    def add_noise(level, x):
        return x + uniform(-level, level)