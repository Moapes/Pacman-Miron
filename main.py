import random
import arcade
import math
import Characters
import ConsolePacmanGame
import StaticVars
import pyautogui

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(scale=0.75)
        self.textures = arcade.load_spritesheet("Assets/Images/PlayerAnimation.png")
        self.textures = self.textures.get_texture_grid(size=(32,32),columns=3,count=24)
        self.set_texture(2)  # Start with a closed mouth
        self.nextFrame_timer = 0.0
        self.flicker_timer = 0.0
        self.current_frame = 0 #cycle through colloums 0 , 1 , 2
        self.state = "ALIVE" #is DYING/ALIVE - we will also use that to first show the death animation and only after that we will respawn
        self.death_animation_timer = 0.0
        self.direction = [0, 0] #[1,0] - right, [-1,0] - left, [0,1] - up, [0,-1] - down
        self.next_direction = [0, 0] #[1,0] - right, [-1,0] - left, [0,1] - up, [0,-1] - down
        self.lives = 3
        self.score = 0
        self.speed = 100
        self.starting_center_x = 0
        self.starting_center_y = 0
        self.radious = 16 #size of the radious of the player sprite/hitbox
        self.nickname = ""
        #spawn immunity related
        self.immunity_duration = 0.0
        self.immune = False

    def handle_movement(self, delta_time, game_view):
        move_dist = self.speed * delta_time

        # 1. Tile Center Math
        tile_center_x = (self.center_x // 32) * 32 + 16
        tile_center_y = (self.center_y // 32) * 32 + 16

        dist_to_center = math.dist((self.center_x, self.center_y), (tile_center_x, tile_center_y))

        # 2. Check for 180-degree turn (Instant turn, no center-snap needed)
        # If current direction is [1,0], back is [-1,0]. If next_dir is [-1,0], it's a U-turn.
        is_u_turn = (self.next_direction[0] == -self.direction[0] and
                     self.next_direction[1] == -self.direction[1])

        if is_u_turn and self.next_direction != [0, 0]:
            self.direction = self.next_direction
            # print(f"DEBUG: Player U-Turn to {self.direction}")

        # 3. Handle Normal Turning (Only at tile centers)
        elif dist_to_center <= move_dist:
            # Snap to center before checking walls or stopping
            self.center_x = tile_center_x
            self.center_y = tile_center_y

            # Check if the requested NEXT direction is clear
            if game_view.can_move(self, self.next_direction):
                self.direction = self.next_direction
            # If next is blocked, check if CURRENT path is blocked
            elif not game_view.can_move(self, self.direction):
                self.direction = [0, 0]  # Full stop at wall

        # 4. Final Position Update
        self.center_x += self.direction[0] * move_dist
        self.center_y += self.direction[1] * move_dist

    def update_player(self, delta_time: float = 1/60):
        #handle the immunity flicker effect
        if self.immune:
            self.flicker_timer  += delta_time

            if self.flicker_timer > 0.1:
                self.flicker_timer = 0
                self.alpha = 100 if self.alpha == 255 else 255

        #reset the flickering if the player isn't immune anymore:
        if not self.immune and self.alpha == 100:
            self.alpha = 255

        #handle death animation
        if self.state == "DYING":
            self.nextFrame_timer += delta_time
            #update to the next frame every milisecond
            if self.nextFrame_timer >= 0.1:
                self.nextFrame_timer = 0
                if self.current_frame < 23:
                    self.current_frame += 1
                    if self.current_frame > 23:
                        self.respawn()
                    else:
                        self.set_texture(self.current_frame)
            return

        #handle regular player animation(only if it is moving)
        if self.direction != [0,0]:
            self.nextFrame_timer += delta_time
            if self.nextFrame_timer > 0.1:
                self.nextFrame_timer = 0
                self.current_frame = (self.current_frame + 1) % 3

            base = 0
            if self.direction == [1,0]: base = 0
            elif self.direction == [-1,0]: base = 3
            elif self.direction == [0,1]: base = 6
            elif self.direction == [0,-1]: base = 9

            self.set_texture(base + self.current_frame)

        else:
            base = 0
            if self.direction == [1, 0]:
                base = 0  # Right Row
            elif self.direction == [-1, 0]:
                base = 3  # Left Row
            elif self.direction == [0, 1]:
                base = 6  # Up Row
            elif self.direction == [0, -1]:
                base = 9  # Down Row

            # Set texture to the 'Closed Mouth' (the 3rd frame in the row)
            self.set_texture(base + 2)

            # Reset animation timer so the chomp starts fresh when they move again
            self.animation_timer = 0
            self.current_frame = 0

    def respawn(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = "GAMEOVER"
        else:
            self.state = "ALIVE"
            self.center_x = self.starting_center_x
            self.center_y = self.starting_center_y
            self.direction = [0, 0]
            self.next_direction = [0, 0]
            self.current_frame = 2  # Closed mouth texture
            self.set_texture(self.current_frame)

            # Give the player the immunity
            self.is_immune = True
            self.immunity_timer = 3.0

class Coin(arcade.Sprite):
    def __init__(self):
        super().__init__("Assets/Images/Coin.png", scale=1)

class PowerUp(arcade.Sprite):
    def __init__(self):
        super().__init__("Assets/Images/Coin.png", scale=1.5)

class Ghost(arcade.Sprite):
    def __init__(self,):
        super().__init__(scale=1)
        self.textures = [arcade.load_texture("Assets/Images/NormalGhost.png"),
                        arcade.load_texture("Assets/Images/ScaredGhost.png")]
        self.direction = [1, 0] #[1,0] - right, [-1,0] - left, [0,1] - up, [0,-1] - down
        self.speed = 110
        self.scale = 0.9
        self.starting_center_x = 0
        self.starting_center_y = 0
        self.set_texture(0)
        self.immunity_duration = 0.0
        self.immune = False
        self.flicker_timer = 0.0  # used to flicker every 0.2s

    def handle_movement(self, delta_time, game_view):
        # 1. Calculate the exact center of the current tile
        tile_center_x = (self.center_x // 32) * 32 + 16
        tile_center_y = (self.center_y // 32) * 32 + 16

        # 2. Check if we've reached the center point
        dist_to_center = math.dist((self.center_x, self.center_y), (tile_center_x, tile_center_y))
        move_dist = self.speed * delta_time

        # We only make decisions when at the center
        canTurn = dist_to_center <= move_dist

        if canTurn:
            # SNAP to center to ensure probe accuracy
            self.center_x = tile_center_x
            self.center_y = tile_center_y

            allowed_directions = []
            backward_dir = [-self.direction[0], -self.direction[1]]

            # 3. Use the helper to check all 4 directions
            for direction in StaticVars.DIRECTIONS:
                if game_view.can_move(self, direction):
                    allowed_directions.append(direction)

            # 4. Decision Logic
            if len(allowed_directions) > 1:
                # Filter out the backward direction to prevent ping-ponging
                available_choices = []
                for d in allowed_directions:
                    if d==backward_dir:
                        continue
                    available_choices.append(d)
                if available_choices:
                    self.direction = random.choice(available_choices)
                else:
                    # If the only way is back, take it (Dead end)
                    self.direction = random.choice(allowed_directions)

            elif len(allowed_directions) == 1:
                self.direction = allowed_directions[0]

            else:
                # Emergency: Ghost is inside a wall hitbox
                # print(f"DEBUG: Ghost stuck at {self.center_x}, {self.center_y}")
                self.direction = backward_dir

                # 5. Final Movement Execution
        self.center_x += self.direction[0] * move_dist
        self.center_y += self.direction[1] * move_dist

class Wall(arcade.Sprite):
    def __init__(self):
        super().__init__("Assets/Images/Wall.png", scale=1)

class GameOverView(arcade.View):
    def __init__(self, message, player_score_list):
        super().__init__()
        self.message = message
        self.player_score_list = player_score_list

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        if self.message=="You Won!":
            messageColor = arcade.color.GREEN
        elif self.message=="You Lost!":
            messageColor = arcade.color.RED
        #draw the message - YOU LOST! / YOU WON!
        arcade.draw_text(self.message, self.window.width / 2, self.window.height / 2 + 50,
                         messageColor, font_size=50, anchor_x="center")
        offset = 0
        playerC = 1
        for name, value in self.player_score_list.items():
            arcade.draw_text(f"{name} Final Score: {value[0]}", self.window.width / 2, self.window.height / 2 - offset,
                             arcade.color.WHITE, font_size=20, anchor_x="center")
            offset += 50
            playerC += 1
        arcade.draw_text("Press ESC to Quit", self.window.width / 2, self.window.height / 2 - offset,
                         arcade.color.GRAY, font_size=15, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.exit()

class GameView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.players_score_list = {}# key - player nickname, value - (player score, player lives)
        self.ghost_list = arcade.SpriteList() #sprite batch
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        #power up related properties
        self.powerUp_list = arcade.SpriteList()
        self.powerUp_current_duration = 0.0 #will be in seconds
        #timestamp for ghosts to use
        self.originallyGavenImmunityTimer = 0.0
        self.isPoweredUp = False

        self.player_list = arcade.SpriteList()
        self.gameRunning = True

        #map size for correct player info offset:
        self.mapHeight = 0

    #drawn every frame here:
    def on_draw(self) -> None:
        self.clear()
        if self.gameRunning:
            #print-out the current state of the map
            self.ghost_list.draw()
            self.wall_list.draw()
            self.coin_list.draw()
            self.player_list.draw()
            self.powerUp_list.draw()
            offsetY = self.mapHeight + len(self.players_score_list) * 20 + 20
            for name, value in self.players_score_list.items():
                color = arcade.color.WHITE if value[1] > 0 else arcade.color.RED
                arcade.draw_text(f"{name} ->  score: {value[0]}",10,offsetY,color,14)
                arcade.draw_text(f" lives: {value[1]}",300,offsetY,color,14)#Broken
                offsetY -= 20

    def can_move(self, sprite, direction):
        """Helper to check if a direction is blocked without moving the sprite permanently."""
        if direction == [0, 0]:
            return True

        # Move the sprite slightly in the desired direction to test collision
        sprite.center_x += direction[0] * 16
        sprite.center_y += direction[1] * 16

        hit_wall = arcade.check_for_collision_with_list(sprite, self.wall_list)

        # Move it back immediately
        sprite.center_x -= direction[0] * 16
        sprite.center_y -= direction[1] * 16

        return len(hit_wall) == 0

    #update placement/movement logic here:
    def on_update(self, delta_time: float) -> None:
        #reduce powerUp duration via delta_time
        if self.isPoweredUp:
            self.powerUp_current_duration -= delta_time
            if self.powerUp_current_duration <= 0.0:
                self.isPoweredUp = False
                for ghost in self.ghost_list:
                    ghost.set_texture(0)#return face to normal again
        #for every player we gotta make sure that he can change hes moving direction -
        #we can achieve that by making the move then checking if the player collides with a wall or not
        #we can also check that if the player does not try to change his direction we will check if he can move
        #if there is a wall infront he will stop immediatelly
        for player in self.player_list:
            self.players_score_list[player.nickname] = [player.score,player.lives]
            player.update_player(delta_time)
            if player.state == "DYING":
                player.death_animation_timer += delta_time
                if player.death_animation_timer >= 1.5:
                    player.respawn()
                    player.center_x = player.starting_center_x
                    player.center_y = player.starting_center_y
                    player.death_animation_timer = 0
            #handle loss
            if player.state == "GAMEOVER":
                self.players_score_list[player.nickname] = [player.score,player.lives]
                self.player_list.remove(player)
                if not self.player_list:
                    self.game_over("You Lost!",self.players_score_list)
            #handle spawn immunity
            if player.immune:
                player.immunity_duration -= delta_time
                if player.immunity_duration <= 0.0:
                    player.immune = False

            if player.state == "ALIVE":
                player.handle_movement(delta_time, self)

                #check power pellets collsions:
                powerUp_collisions = arcade.check_for_collision_with_list(player,self.powerUp_list)
                if powerUp_collisions:
                    for powerUp in powerUp_collisions:
                        self.powerUp_current_duration = random.uniform(6.0,8.0)#make up a random duration for the power up
                        self.originallyGavenImmunityTimer = self.powerUp_current_duration #to handle ghost flickering
                        self.isPoweredUp = True
                        self.powerUp_list.remove(powerUp)
                    for ghost in self.ghost_list:
                        ghost.set_texture(1)#make ghost scared


                #apply logic of coins and ghost collisions with the player
                coin_collisions = arcade.check_for_collision_with_list(player,self.coin_list)

                if coin_collisions:
                    for coin in coin_collisions:
                        player.score += StaticVars.SCORE_PER_COIN
                        self.coin_list.remove(coin)
                        if len(self.coin_list) == 0:
                            self.game_over("You Won!",self.players_score_list)

                collisions_with_ghosts = arcade.check_for_collision_with_list(player,self.ghost_list)
                if collisions_with_ghosts:
                    if self.isPoweredUp:
                        for ghost in collisions_with_ghosts:
                            if not ghost.immune:
                                ghost.center_x = ghost.starting_center_x
                                ghost.center_y = ghost.starting_center_y
                                ghost.immune = True
                                ghost.immunity_duration = 3.0
                                player.score += StaticVars.SCORE_PER_GHOST

                    elif not player.immune:
                        player.state = "DYING"
                        player.current_frame = 12
                        player.immune = True
                        player.immunity_duration = 3.0
                        player.death_animation_timer = 0.0

                        # --- GHOST LOGIC GOES HERE ---
        # (Apply the same logic style to your ghosts to keep it consistent!)

        for ghost in self.ghost_list:
            ghost.handle_movement(delta_time, self)

            # spawn immunity handling:
            if ghost.immune:
                ghost.immunity_duration -= delta_time
                if ghost.immunity_duration <= 0.0:
                    ghost.immune = False

            # Ghost flicker warning if power-up is about to end
            if self.isPoweredUp:
                if self.powerUp_current_duration <= 3.0:  # last 3 seconds warning
                    ghost.flicker_timer += delta_time
                    if ghost.flicker_timer >= 0.2:  # toggle every 0.2 seconds
                        ghost.flicker_timer = 0
                        ghost.alpha = 100 if ghost.alpha == 255 else 255
                else:
                    ghost.alpha = 255
                    ghost.flicker_timer = 0
            else:
                ghost.alpha = 255
                ghost.flicker_timer = 0

    #set all the sprites and drawings to batches
    def setup(self) -> None:
        current_center_x, current_center_y = 16,16
        playerC = 0
        #for now animation-less sprites will be initialised
        for line in reversed(StaticVars.LEVEL_MAP):
            #inside here, we will load the text-based map and split them into batches, no drawing yet
            for cell in line:
                if cell == '#':
                    #assign texture
                    wall = Wall()
                    #assign center position
                    wall.center_x, wall.center_y = current_center_x, current_center_y
                    self.wall_list.append(wall)
                    # print("wall spawned at position: ",wall.center_x, wall.center_y)
                if cell == '.':
                    coin = Coin()
                    coin.center_x, coin.center_y = current_center_x, current_center_y
                    self.coin_list.append(coin)
                    # print("coin spawned at position: ",coin.center_x, coin.center_y)
                if cell == 'P':
                    playerC += 1
                    gamePlayer = Player()
                    gamePlayer.center_x, gamePlayer.center_y = current_center_x, current_center_y
                    self.player_list.append(gamePlayer)
                    self.players_score_list[f"Player{playerC}"] = [gamePlayer.score,gamePlayer.lives]
                    gamePlayer.immunity_duration = 3.0
                    gamePlayer.immune = True
                    #mark the players starting point - when he dies he will spawn there
                    gamePlayer.starting_center_x = gamePlayer.center_x
                    gamePlayer.starting_center_y = gamePlayer.center_y
                    gamePlayer.nickname = f"Player{playerC}" #give a player nickname based on the amount of the players
                    # print("player spawned at position: ", gamePlayer.center_x, gamePlayer.center_y)
                if cell == 'G':
                    ghost = Ghost()
                    ghost.center_x, ghost.center_y = current_center_x, current_center_y
                    ghost.starting_center_x = ghost.center_x
                    ghost.starting_center_y = ghost.center_y
                    ghost.immunity_duration = 3.0
                    ghost.immune = True
                    self.ghost_list.append(ghost)
                    # print("ghost spawned at position: ", ghost.center_x, ghost.center_y)
                if cell == 'u':
                    powerup = PowerUp()
                    powerup.center_x, powerup.center_y = current_center_x, current_center_y
                    self.powerUp_list.append(powerup)

                current_center_x += 32
            self.mapHeight += 32
            current_center_y += 32
            current_center_x = 16

    #check what keys the player holds to ensure the player character will move on each direction called
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        line_of_controls = 0#each line represents a control setting for each player 0 - for ARROWS, 1 - for WASD
        for player in self.player_list:
            if symbol == StaticVars.CONTROLS_FOR_PLAYER[line_of_controls][0]:
                player.next_direction = [-1,0]
            elif symbol == StaticVars.CONTROLS_FOR_PLAYER[line_of_controls][1]:
                player.next_direction = [1,0]
            elif symbol == StaticVars.CONTROLS_FOR_PLAYER[line_of_controls][2]:
                player.next_direction = [0,1]
            elif symbol == StaticVars.CONTROLS_FOR_PLAYER[line_of_controls][3]:
                player.next_direction = [0,-1]
            line_of_controls += 1

    def game_over(self,message,player_score_list) -> None:
        # 2. Create the new view
        end_view = GameOverView(message, player_score_list)

        # 3. Tell the window to switch to it
        self.window.show_view(end_view)

def main():
    help(arcade.load_spritesheet)
    # window = arcade.Window(StaticVars.SCREEN_WIDTH, StaticVars.SCREEN_HEIGHT, "Pacman")
    # window = arcade.Window(StaticVars.SCREEN_WIDTH, StaticVars.SCREEN_HEIGHT,title="Pacman")
    game_window = arcade.Window(title="Pacman", fullscreen=True)

    game = GameView()
    game.setup()
    game_window.show_view(game)
    arcade.run()

main()