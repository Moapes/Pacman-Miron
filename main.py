import random
import arcade
import Characters
import ConsolePacmanGame


LEVEL_MAP = [
    "###########",
    "#P....G...#",
    "#.........#",
    "###########",
]

# -------------------------
# Run Game
# -------------------------
if __name__ == "__main__":
    game = ConsolePacmanGame.ConsolePacmanGame(LEVEL_MAP)
    game.run()
