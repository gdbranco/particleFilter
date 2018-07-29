class PathPlanning(object):
    def __init__(self):
        self.point_list = None

    def save_movement(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.point_list, f)

    def load_movement(self, filename):
        with open(filename) as f:
            point_list = json.load(f)
        self.point_list = point_list