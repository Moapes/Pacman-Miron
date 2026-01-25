import random
import arcade
import Characters
import ConsolePacmanGame
import StaticVars



# -------------------------
# Run Game
# -------------------------
if __name__ == "__main__":
    game = ConsolePacmanGame.ConsolePacmanGame(StaticVars.LEVEL_MAP)
    game.run()
