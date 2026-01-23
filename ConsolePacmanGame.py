import Characters
import Objects
import random

class ConsolePacmanGame:
    def __init__(self, level_map):
        self.level_map = level_map
        self.height = len(level_map)
        self.width = len(level_map[0])

        self.walls = []
        self.coins = []
        self.ghosts = []
        self.player = None

        self.start_x = 0
        self.start_y = 0

        self.setup()

    def setup(self):
        for y, row in enumerate(reversed(self.level_map)):
            for x, cell in enumerate(row):
                if cell == "#":
                    self.walls.append(Objects.Wall(x, y))
                elif cell == ".":
                    self.coins.append(Objects.Coin(x, y))
                elif cell == "P":
                    self.player = Characters.Player(x, y)
                    self.start_x = x
                    self.start_y = y
                elif cell == "G":
                    self.ghosts.append(Characters.Enemy(x, y))

    # -------------------------
    # Rendering
    # -------------------------
    def render(self):
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        for wall in self.walls:
            grid[wall.center_y][wall.center_x] = "#"

        for coin in self.coins:
            grid[coin.center_y][coin.center_x] = "."

        for ghost in self.ghosts:
            grid[ghost.center_y][ghost.center_x] = "G"

        grid[self.player.center_y][self.player.center_x] = "P"

        print("\n" + "=" * (self.width + 2))
        for row in reversed(grid):
            print("|" + "".join(row) + "|")
        print("=" * (self.width + 2))
        print(f"Score: {self.player.score} | Lives: {self.player.lives}")

    # -------------------------
    # Helpers
    # -------------------------
    def is_wall(self, x, y):
        return any(w.center_x == x and w.center_y == y for w in self.walls)

    def get_coin_at(self, x, y):
        for coin in self.coins:
            if coin.center_x == x and coin.center_y == y:
                return coin
        return None

    def get_ghost_at(self, x, y):
        for ghost in self.ghosts:
            if ghost.center_x == x and ghost.center_y == y:
                return ghost
        return None

    # -------------------------
    # Player Movement
    # -------------------------
    def handle_player_move(self, direction):
        moves = {"w": (0, 1), "s": (0, -1), "a": (-1, 0), "d": (1, 0)}
        if direction not in moves:
            return

        dx, dy = moves[direction]
        new_x = self.player.center_x + dx
        new_y = self.player.center_y + dy

        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            return
        if self.is_wall(new_x, new_y):
            return

        self.player.center_x = new_x
        self.player.center_y = new_y

        coin = self.get_coin_at(new_x, new_y)
        if coin:
            self.player.score += coin.value
            self.coins.remove(coin)

    # -------------------------
    # Ghost Movement
    # -------------------------
    def move_ghosts(self):
        for ghost in self.ghosts:
            if random.random() < 0.3:
                ghost.pick_new_direction()

            new_x = ghost.center_x + ghost.change_x
            new_y = ghost.center_y + ghost.change_y

            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                continue
            if self.is_wall(new_x, new_y):
                continue

            ghost.center_x = new_x
            ghost.center_y = new_y

            if ghost.center_x == self.player.center_x and ghost.center_y == self.player.center_y:
                self.player.lives -= 1
                print("👻 רוח תפסה אותך! חיים -1")
                self.reset_player_position()

    def reset_player_position(self):
        self.player.center_x = self.start_x
        self.player.center_y = self.start_y

    # -------------------------
    # Game State
    # -------------------------
    def is_game_over(self):
        if self.player.lives <= 0:
            print("GAME OVER – נגמרו החיים.")
            return True
        if not self.coins:
            print("YOU WIN – אספת את כל המטבעות!")
            return True
        return False

    # -------------------------
    # Main Loop
    # -------------------------
    def run(self):
        print("ברוך הבא לפקמן קונסול!")
        print("w/a/s/d לזוז | q לצאת")

        while True:
            self.render()
            if self.is_game_over():
                break

            command = input("לאן לזוז? ").strip().lower()
            if command == "q":
                print("יציאה מהמשחק.")
                break

            self.handle_player_move(command)
            self.move_ghosts()