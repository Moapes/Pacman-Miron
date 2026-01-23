import random

class Character:
    def __init__(self, center_x, center_y, speed=1):
        self.center_x = center_x
        self.center_y = center_y
        self.speed = speed
        self.change_x = 0
        self.change_y = 0


# -------------------------
# Player
# -------------------------
class Player(Character):
    def __init__(self, center_x, center_y, speed=1):
        super().__init__(center_x, center_y, speed)
        self.score = 0
        self.lives = 3


# -------------------------
# Enemy (Ghost)
# -------------------------
class Enemy(Character):
    def __init__(self, center_x, center_y, speed=1):
        super().__init__(center_x, center_y, speed)
        self.pick_new_direction()

    def pick_new_direction(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
        self.change_x, self.change_y = random.choice(directions)