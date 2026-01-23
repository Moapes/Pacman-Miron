class Wall:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y


class Coin:
    def __init__(self, center_x, center_y, value=1):
        self.center_x = center_x
        self.center_y = center_y
        self.value = value