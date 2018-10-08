import sys, random, math, time
from datetime import datetime
from pygame.locals import *
import pygame

# Global constants
# Sprite Coords thing www.spritecow.com
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)
timer = -1
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)

# Screen dimensions
W, H = 1280, 720
FPS = 60

done = False

pygame.init()
size = [W, H]  # Set the height and width of the screen
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Jeffventures")

clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):

    def __init__(self, image):
        super().__init__()

        self.speed = 4  # Normal Speed is 4
        self.jumpmultiplier = 9.9  # Normal Jump is 9.9

        self.boost = False
        self.lives = 6  # NORM IS 6
        self.time = None
        self.ground = -85

        # Set speed vector of player:
        self.change_x = 0
        self.change_y = 0

        self.level = None
        self.lvlno = None
        self.direction = "R"
        self.timerspeed = -1
        self.timerjump = -1

        self.heartsimgs = []
        self.sprite_sheet = spritesheet("sprites/hearts.png", 112, 32)
        self.loadlivesimg()

        self.walking_frames_l = []
        self.walking_frames_r = []

        self.noclip = False

        self.sprite_sheet = spritesheet(image, 384, 864)
        self.loadSpriteSheet()

        self.score = 0
        self.prevscore = -1

        # Set the starting image
        self.image = self.walking_frames_r[0]
        self.rect = self.image.get_rect()

    def loadSpriteSheet(self):
        # Right Facing Spritse
        image = self.sprite_sheet.get_image(9, 124, 74, 62)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(106, 124, 74, 62)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(202, 124, 74, 62)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(298, 124, 74, 62)
        self.walking_frames_r.append(image)

        # Left Facing Sprites.
        image = pygame.transform.flip(self.walking_frames_r[0], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[1], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[2], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[3], True, False)
        self.walking_frames_l.append(image)

    def loadlivesimg(self):
        image = self.sprite_sheet.get_image(0, 0, 36, 32)
        self.heartsimgs.append(image)
        image = self.sprite_sheet.get_image(37, 0, 36, 32)
        self.heartsimgs.append(image)
        image = self.sprite_sheet.get_image(76, 0, 36, 32)
        self.heartsimgs.append(image)

    def hearts(self):
        if self.lives == 6:
            screen.blit(self.heartsimgs[0], (1100, 10))
            screen.blit(self.heartsimgs[0], (1133, 10))
            screen.blit(self.heartsimgs[0], (1164, 10))
        if self.lives == 5:
            screen.blit(self.heartsimgs[0], (1100, 10))
            screen.blit(self.heartsimgs[0], (1133, 10))
            screen.blit(self.heartsimgs[1], (1164, 10))
        if self.lives == 4:
            screen.blit(self.heartsimgs[0], (1100, 10))
            screen.blit(self.heartsimgs[0], (1133, 10))
            screen.blit(self.heartsimgs[2], (1164, 10))
        if self.lives == 3:
            screen.blit(self.heartsimgs[0], (1100, 10))
            screen.blit(self.heartsimgs[1], (1133, 10))
            screen.blit(self.heartsimgs[2], (1164, 10))
        if self.lives == 2:
            screen.blit(self.heartsimgs[0], (1100, 10))
            screen.blit(self.heartsimgs[2], (1133, 10))
            screen.blit(self.heartsimgs[2], (1164, 10))
        if self.lives == 1:
            screen.blit(self.heartsimgs[1], (1100, 10))
            screen.blit(self.heartsimgs[2], (1133, 10))
            screen.blit(self.heartsimgs[2], (1164, 10))
        if self.lives <= 0:
            screen.blit(self.heartsimgs[2], (1100, 10))
            screen.blit(self.heartsimgs[2], (1133, 10))
            screen.blit(self.heartsimgs[2], (1164, 10))
            self.killed()

    def update(self):
        if self.lvlno == 1:
            self.ground = -70
        if self.lvlno == 2:
            self.ground = -55
        else:
            self.ground

        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

        pos = self.rect.x + self.level.world_shift
        if self.direction == "R":
            frame = (pos // 20) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]
        elif self.direction == "L":
            frame = (pos // 20) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]
        elif self.direction == "M" and self.lastdirection == "R":
            self.image = self.walking_frames_r[2]
        elif self.direction == "M" and self.lastdirection == "L":
            self.image = self.walking_frames_l[2]

        # Checking if the player hits a platform on the x axis
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        # Checking if the player hits an enemy
        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for enemy in enemy_hit_list:
            # This checks if the player hits the enemy on the x axis and the player reacts my being moved 100px
            if self.change_x > 0:
                self.rect.right = enemy.rect.left
            if self.change_x < 0:
                self.rect.left = enemy.rect.right
            if self.rect.left == enemy.rect.right:
                self.lives -= 1
                self.rect.x += 100
            if self.rect.right == enemy.rect.left:
                self.lives -= 1
                self.rect.x -= 100

        # Move up/down
        self.rect.y += self.change_y

        # Checking if the player hits a platform on the y axis
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom


            # Stop our vertical movement
            self.change_y = 0

            if isinstance(block, MovingPlatform):
                self.rect.x += block.change_x

        coin_hit_list = pygame.sprite.spritecollide(self, self.level.coin_list, True)
        self.prevscore = self.score
        for coin in coin_hit_list:
            # This checks if we have hit a coin if so we gain 100 points
            if self.change_x > 0:
                self.score = self.score + 100
            elif self.change_x < 0:
                self.score = self.score + 100
            elif self.change_y > 0:
                self.score = self.score + 100
            elif self.change_y < 0:
                self.score = self.score + 100
        # Checking if the player hits a speed coin
        speed_hit_list = pygame.sprite.spritecollide(self, self.level.speed_list, True)
        for speed in speed_hit_list:
            if self.change_x > 0:
                self.speed = 8
                self.timerspeed = datetime.now()
            elif self.change_x < 0:
                self.speed = 8
                self.timerspeed = datetime.now()
            elif self.change_y > 0:
                self.speed = 8
                self.timerspeed = datetime.now()
            elif self.change_y < 0:
                self.speed = 8
                self.timerspeed = datetime.now()
        # Checking if the player hits a jump coin
        jump_hit_list = pygame.sprite.spritecollide(self, self.level.jump_list, True)
        for jump in jump_hit_list:
            if self.change_x > 0:
                self.jumpmultiplier = 14
                self.timerjump = datetime.now()
            elif self.change_x < 0:
                self.jumpmultiplier = 14
                self.timerjump = datetime.now()
            elif self.change_y > 0:
                self.jumpmultiplier = 14
                self.timerjump = datetime.now()
            elif self.change_y < 0:
                self.jumpmultiplier = 14
                self.timerjump = datetime.now()
        # Checking if the player hits an enemy on the y axis
        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for enemy in enemy_hit_list:
            # Checks if the player hits the top of the enemy on the y axis and the enemy will disapear if the player does
            if self.change_y > 0:
                pygame.sprite.Sprite.kill(enemy)
                self.score += 250

        # Timers for both powerups and how long they last
        if self.timerjump != -1:
            value = (datetime.now() - self.timerjump).total_seconds()
            #print("jump: "+str(value))
            if value > 5:
                self.jumpmultiplier = 9.9
                self.timerjump = -1

        if self.timerspeed != -1:
            value1 = (datetime.now() - self.timerspeed).total_seconds()
            #print("speed: "+str(value1))
            if value1 > 5:
                self.speed = 4
                self.timerspeed = -1


    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

        # Check if we are on the ground.
        if self.rect.y >= H - self.rect.height + self.ground and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = H - self.rect.height + self.ground

    # Player movement:
    # When user hits space bar or the up arrow
    def jump(self):
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= H + self.ground:
            self.change_y = -self.jumpmultiplier

    def go_left(self):
        # When the user hits the left arrow
        self.direction = "L"
        self.lastdirection = self.direction
        self.change_x = -self.speed

    def go_right(self):
        # When the user hits the right arrow
        self.direction = "R"
        self.lastdirection = self.direction
        self.change_x = self.speed

    def stop(self):
        # When the user is not using the keyboard
        self.direction = "M"
        self.change_x = 0

    # This is called when the player has no more lives
    def killed(self):
        killed = True
        pygame.mixer.music.stop()
        killedscreen = pygame.image.load("backgrounds/died.png")
        screen.fill(WHITE)
        screen.blit(killedscreen, (0, 0))
        while killed:
            for event in pygame.event.get():
                # print(event)
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    killed = False
            button("Try Again!", 287, 500, 135, 65, GREEN, bright_green, chooseyourdog)
            button("Back To Menu!", 860, 500, 135, 65, RED, bright_red, startScreen)
            disclaimer()
            pygame.display.update()
        startScreen()


class Enemy(pygame.sprite.Sprite):
    # Enemy
    def __init__(self, boundl, boundr):
        # Call the parent's constructor
        super().__init__()

        self.change_x = 0
        self.change_y = 0

        self.boundary_top = 0
        self.boundary_bottom = 0
        self.boundary_left = boundl
        self.boundary_right = boundr

        self.level = None
        self.player = None

        self.direction = 1

        self.walking_frames_l = []
        self.walking_frames_r = []


class Android(Enemy):
    def __init__(self,x,y,boundl,boundr):
        Enemy.__init__(self,boundl,boundr)
        self.sprite_sheet = spritesheet("sprites/android.png", 494, 361)
        self.loadSpriteSheet()

        # Set the image the enemy starts with
        self.image = self.walking_frames_r[0]

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def loadSpriteSheet(self):
        # Loading in sprites facing right
        image = self.sprite_sheet.get_image(21, 14, 26, 36)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(106, 14, 22, 36)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(100, 72, 38, 37)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(106, 135, 22, 36)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(104, 195, 24, 36)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(100, 253, 36, 37)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(104, 316, 30, 36)
        self.walking_frames_r.append(image)
        # Loading in sprites facing right and changed to face left

        image = pygame.transform.flip(self.walking_frames_r[0], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[1], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[2], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[3], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[4], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[5], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[6], True, False)
        self.walking_frames_l.append(image)

    def update(self):
        # Move left/right
        self.rect.x += self.change_x

        pos = self.rect.x
        if self.direction == 1:
            frame = (pos // 20) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]
        elif self.direction == -1:
            frame = (pos // 20) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]

        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
                self.player.lives -= 1
                self.player.rect.x -= 100
            elif self.change_x > 0:
                # Otherwise if we are moving left, do the opposite
                self.player.rect.left = self.rect.right
                self.player.lives -= 1
                self.player.rect.x += 100
        # Move up/down
        self.rect.y += self.change_y

        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        # check the boundaries and see if we need to reverse direction
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1
            self.direction *= -1

class BossAndroid(Enemy):
    def __init__(self,x,y,boundl,boundr):
        Enemy.__init__(self, boundl, boundr)
        self.sprite_sheet = spritesheet("sprites/androidboss.png", 4940, 3610)
        self.loadSpriteSheet()

        # Set the image the enemy starts with
        self.image = self.walking_frames_r[0]

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def loadSpriteSheet(self):
        # Loading in sprites facing right
        image = self.sprite_sheet.get_image(210, 140, 260, 360)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(1060, 140, 220, 360)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(1000, 720, 380, 370)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(1060, 1350, 220, 360)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(1040, 1950, 240, 360)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(1000, 2530, 360, 370)
        self.walking_frames_r.append(image)
        image = self.sprite_sheet.get_image(1040, 3160, 300, 360)
        self.walking_frames_r.append(image)
        # Loading in sprites facing right and changed to face left

        image = pygame.transform.flip(self.walking_frames_r[0], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[1], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[2], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[3], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[4], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[5], True, False)
        self.walking_frames_l.append(image)
        image = pygame.transform.flip(self.walking_frames_r[6], True, False)
        self.walking_frames_l.append(image)

    def update(self):

        # Move left/right
        self.rect.x += self.change_x

        pos = self.rect.x
        if self.direction == 1:
            frame = (pos // 20) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]
        elif self.direction == -1:
            frame = (pos // 20) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]

        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
                self.player.lives -= 1
                self.player.rect.x -= 100
            elif self.change_x > 0:
                # Otherwise if we are moving left, do the opposite
                self.player.rect.left = self.rect.right
                self.player.lives -= 1
                self.player.rect.x += 100
        # Move up/down
        self.rect.y += self.change_y

        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        # check the boundaries and see if we need to reverse direction
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1
            self.direction *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, colour):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(colour)

        self.rect = self.image.get_rect()

class MovingPlatform(Platform):
    # Platform that moves
    change_x = 0
    change_y = 0

    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0

    player = None

    level = None

    def update(self):


        # Move left/right
        self.rect.x += self.change_x

        # See if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # If we are moving right, set our right side
            # to the left side of the item we hit
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            else:
                # Otherwise if we are moving left, do the opposite.
                self.player.rect.left = self.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # Reset our position based on the top/bottom of the object.
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        # Check the boundaries and see if we need to reverse
        # direction.
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1


class Drop(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = None
        self.frames = []

    def update(self):
        frame = 0
        self.image = self.frames[frame]


class Coin(Drop):

    def __init__(self,  x, y):
        Drop.__init__(self)

        self.sprite_sheet = spritesheet("sprites/coins.png", 508, 64)
        self.loadSprite()

        # Set the image the player starts with
        self.image = self.frames[0]
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def loadSprite(self):
        # Loading in sprites facing right
        image = self.sprite_sheet.get_image(0, 0, 60, 64)
        self.frames.append(image)


class SpeedBoost(Drop):

    def __init__(self, x, y):
        Drop.__init__(self)

        self.sprite_sheet = spritesheet("sprites/speed.png", 60, 60)
        self.loadSprite()

        # Set the image the player starts with
        self.image = self.frames[0]
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def loadSprite(self):
        # Loading in sprites facing right
        image = self.sprite_sheet.get_image(0, 0, 60, 60)
        self.frames.append(image)


class JumpBoost(Drop):

    def __init__(self, x, y):
        Drop.__init__(self)

        self.sprite_sheet = spritesheet("sprites/jump.png", 60, 60)
        self.loadSprite()

        # Set the image the player starts with
        self.image = self.frames[0]
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def loadSprite(self):
        # Loading in sprites facing right
        image = self.sprite_sheet.get_image(0, 0, 60, 60)
        self.frames.append(image)


class Level(object):
    # Super class to contain the base of each level

    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.coin_list = pygame.sprite.Group()
        self.speed_list = pygame.sprite.Group()
        self.jump_list = pygame.sprite.Group()
        self.player = player
        self.colour = GREEN
        # Background image
        self.background = None

        # How far this world has been scrolled left/right
        self.world_shift = 0
        self.level_limit = -1000

    # Update everything on this level
    def update(self):
        self.platform_list.update()
        self.coin_list.update()
        self.speed_list.update()
        self.jump_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        # Draw the background
        screen.fill(WHITE)
        screen.blit(self.background, (self.world_shift // 6, 0))
        # Draw all the sprite lists that we have

        self.platform_list.draw(screen)
        self.coin_list.draw(screen)
        self.speed_list.draw(screen)
        self.jump_list.draw(screen)
        # Drraw enemy list
        self.enemy_list.draw(screen)

    def shift_world(self, shift_x):
        # When the player moves the background with the player
        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the platform list and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for coin in self.coin_list:
            coin.rect.x += shift_x
        # Go through all the enemy list and shift
        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for speed in self.speed_list:
            speed.rect.x += shift_x

        for jump in self.jump_list:
            jump.rect.x += shift_x


# Create platforms for the level
class Level_01(Level):

    def __init__(self, player):

        # Call the parent constructor
        Level.__init__(self, player)
        self.colour = GREEN
        self.background = pygame.image.load("backgrounds/level_1.png")

        self.level_limit = -1900

        # Array with width, height, x, and y of platform
        # 4D array use
        level = [[210, 70, 200, 520],
                 [210, 70, 600, 420],
                 [500, 70, 1440, 420],
                 [210, 70, 1100, 520],
                 [210, 70, 1120, 300],
                 [100, 30, 1700, 300],
                 [210, 70, 2200, 120]
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1], self.colour)
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block = MovingPlatform(70, 40, self.colour)
        block.rect.x = 1350
        block.rect.y = 280
        block.boundary_left = 1350
        block.boundary_right = 1600
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        block1 = MovingPlatform(100, 40, self.colour)
        block1.rect.x = 1850
        block1.rect.y = 220
        block1.boundary_left = 1850
        block1.boundary_right = 2000
        block1.change_x = 1
        block1.player = self.player
        block1.level = self
        self.platform_list.add(block1)

        block3 = MovingPlatform(100, 10, self.colour)
        block3.rect.x = 1850
        block3.rect.y = 600
        block3.boundary_left = 1850
        block3.boundary_right = 2000
        block3.change_x = 1
        block3.player = self.player
        block3.level = self
        self.platform_list.add(block3)

        block2 = MovingPlatform(70, 70, self.colour)
        block2.rect.x = 2100
        block2.rect.y = 300
        block2.boundary_top = 100
        block2.boundary_bottom = 650
        block2.change_y = -1
        block2.player = self.player
        block2.level = self
        self.platform_list.add(block2)
        # 2D array use
        coins = [[100, 500],
                 [800, 330],
                 [1500, 330]
                 ]

        for coin in coins:
            pickup = Coin(coin[0], coin[1])
            self.coin_list.add(pickup)

        speed = SpeedBoost( 500, 500)
        self.speed_list.add(speed)

        jump = JumpBoost(1120, 100)
        self.jump_list.add(jump)

        enemy = Android(1120, 265, 1120, 1230)
        enemy.player = self.player
        enemy.level = self
        enemy.change_x = 1
        self.enemy_list.add(enemy)

        #x,y, boundl, boundr
        enemy2 = Android(2200, 585, 2200, 2700)
        enemy2.player = self.player
        enemy2.level = self
        enemy2.change_x = 1
        self.enemy_list.add(enemy2)

        enemy3 = Android(1440, 386, 1440,1910)
        enemy3.player = self.player
        enemy3.level = self
        enemy3.change_x = 1
        self.enemy_list.add(enemy3)


# Create platforms for the level
class Level_02(Level):

    def __init__(self, player):

        # Call the parent constructor
        Level.__init__(self, player)
        self.background = pygame.image.load("backgrounds/level_2.png")
        self.colour = BLACK
        self.level_limit = -2000

        # Array with type of platform, and x, y location of the platform.
        level = [[600, 70, 200, 525],
                 [600, 70, 200, 385],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 [400, 70, 1575, 500],
                 [400, 70, 1575, 200],
                 [400, 70, 2100, 100]
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1], self.colour)
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block = MovingPlatform(70, 70, self.colour)
        block.rect.x = 2000
        block.rect.y = 200
        block.boundary_top = 200
        block.boundary_bottom = 680
        block.change_y = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        coins = [[100, 500],
                 [800, 330],
                 [1500, 330],
                 [1575, 125],
                 [1640, 125],
                 [1705, 125],
                 [1770, 125]
                 ]

        for coin in coins:
            pickup = Coin(coin[0], coin[1])
            self.coin_list.add(pickup)

        jump = JumpBoost(750, 200)
        self.jump_list.add(jump)

class Level_03(Level):

    def __init__(self, player):

        # Call the parent constructor
        Level.__init__(self, player)
        self.colour = GREEN
        self.background = pygame.image.load("backgrounds/level_3.png")

        self.level_limit = -2000

        # Array with width, height, x, and y of platform
        # 4D array use
        level = [[210, 70, 500, 520],
                 [210, 70, 600, 400]
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1], self.colour)
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)


        # 2D array use
        coins = [[1600, 595],
                 [1700, 595],
                 [1800, 595],
                 [1900, 595],
                 [2000, 595]
                 ]

        for coin in coins:
            pickup = Coin(coin[0], coin[1])
            self.coin_list.add(pickup)

        speed = SpeedBoost(200, 500)
        self.speed_list.add(speed)

        jump = JumpBoost(400, 600)
        self.jump_list.add(jump)

        enemy2 = BossAndroid(800, 316, 800, 1500)
        enemy2.player = self.player
        enemy2.level = self
        enemy2.change_x = 1
        self.enemy_list.add(enemy2)




class spritesheet(object):
    # This class grabs images from a spritesheet
    sprite_sheet = None

    def __init__(self, file_name, new_width, new_height):
        # File is passed in with potential different dimentions
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name)
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet, (new_width, new_height))

    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """

        # Create a new blank image
        image = pygame.Surface([width, height]).convert()

        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))

        # Assuming black works as the transparent color
        image.set_colorkey(BLACK)

        # Return the image
        return image

# This is the main title screen:
def startScreen():
    intro = True
    pygame.mixer.music.stop()
    menuscreen = pygame.image.load("backgrounds/startmenu.png")
    screen.fill(WHITE)
    screen.blit(menuscreen, (0, 0))
    while intro:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                intro = False
        button("Go Walkies!", 287, 335, 115, 50, GREEN, bright_green, controls)
        button("Leave!", 860, 335, 115, 50, RED, bright_red, exit)
        # button("Scoreboard",W/2,H/2,115,50,GREEN,bright_green,scoreboard)
        disclaimer()
        pygame.display.update()
    exit()

# Character Selection Screen:
def chooseyourdog():
    dog = True
    choosedog = pygame.image.load("backgrounds/choosedog.png")
    pygame.mixer.music.stop()
    screen.fill(WHITE)
    screen.blit(choosedog, (0, 0))
    while dog:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                dog = False
        button("Jeff!",225,475,100,50,WHITE,GREY, game, "sprites/dog1.png")
        button("Steve!", 565, 475, 100, 50, WHITE, GREY, game, "sprites/dog2.png")
        button("Bob!", 880, 475, 100, 50, WHITE, GREY, game, "sprites/dog3.png")
        disclaimer()
        pygame.display.update()
    controls()


def controls():
    control = True
    cntrl = pygame.image.load("backgrounds/control.png")
    pygame.mixer.music.stop()
    screen.fill(WHITE)
    screen.blit(cntrl, (0, 0))
    while control:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                control = False

        button("Next!", 225, 550, 100, 50, WHITE, GREY, chooseyourdog)
        disclaimer()
        pygame.display.update()
    startScreen()



# This is used for the text displayed on the screen
def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()


def hud_display(text, coord):
    smallText = pygame.font.Font('C:\Windows\Fonts\ARLRDBD.TTF', 40)
    TextSurf, TextRect = text_objects(text, smallText)
    TextRect.center = coord
    screen.blit(TextSurf, TextRect)


def button(msg, x, y, w, h, colour, hovercolour, action=None, parameter=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, hovercolour, (x, y, w, h))

        if click[0] == 1 and action != None and parameter != None:
            action(parameter)
        elif click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(screen, colour, (x, y, w, h))

    smallText = pygame.font.SysFont("comicsansms", 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    screen.blit(textSurf, textRect)

# This is a small disclaimer i added
def disclaimer():
    myfont = pygame.font.SysFont("monospace", 16)
    disclaimertext = myfont.render("Copyright, 2018, Jonathan Kane", 1, (0, 0, 0))
    screen.blit(disclaimertext, (5, 700))

# This tells the user what version of the game they are using
def build():
    myfont = pygame.font.SysFont("monospace", 16)
    disclaimertext = myfont.render("Jeffventures Beta 1.2", 1, (0, 0, 0))
    screen.blit(disclaimertext, (0, 700))

# I could not use just pygame quit because there was a delay when exiting so i addded the sys package to prevent the delay
def exit():
    pygame.quit()
    sys.exit()

# This displays the scoreboard and call other functions
def scoreboard(score=None):
    scores = True
    pygame.mixer.music.stop()
    scoreboard = pygame.image.load("backgrounds/scoreboard.png")
    screen.fill(WHITE)
    filename = "Scores/scores.txt"
    screen.blit(scoreboard, (0, 0))
    if (score != None):
        writetofile(filename, score)
    names, scores = readfile(filename)
    names, scores = sort(names, scores)
    displayscores(names, scores)

    while scores:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                scores = False
        button("Next!", 1000, 600, 100, 50, WHITE, GREY, startScreen)
        disclaimer()
        pygame.display.update()
    startScreen()

# Places of the scores on the screen
def displayscores(names, scores):
    diff = 175
    x, y = 105, 280
    #print("\n Text File Names:")
    namesorscore("Name", (105, 230))
    namesorscore("Score", (105 + diff, 230))
    for n in range(0, len(names)):
        #print(names[n])
        #print(scores[n])
        if (n == 8):
            x, y = 555, 280
            namesorscore("Name", (555, 230))
            namesorscore("Score", (555 + diff, 230))
        elif (n == 16):
            x, y = 1005, 280
            namesorscore("Name", (1005, 230))
            namesorscore("Score", (1005 + diff, 230))
        elif (n > 21):
            return
        namesorscore(names[n], (x, y))
        namesorscore(str(scores[n]), (x + diff, y))
        y += 50

# Draws the scores to the display
def namesorscore(message, coord):
    text = smallText = pygame.font.Font('C:\Windows\Fonts\ARLRDBD.TTF', 40)
    TextSurf, TextRect = text_objects(message, text)
    TextRect.center = coord
    screen.blit(TextSurf, TextRect)
    pygame.display.update()

# Writes a names and score to a file with a comma
def writetofile(filename, score):
    output_file = open(filename, "a")
    msg = "Please Enter You're Name?"
    name = ""
    true = True
    while true:
        try:  # https://docs.python.org/2/tutorial/errors.html
            name = str(input(msg))
            if name != "":
                true = False
        except (KeyboardInterrupt, SyntaxError):
            print("Please enter a valid name")
    output_file.write(name + "," + str(score) + '\n')
    output_file.close()

# Reads a file and splits names and scores via a comma into two arrays(lists)
def readfile(filename):
    # Read the lines of a file into an array
    # So that each line of data is very easy to process
    text_file = open(filename, "r")
    data = text_file.readlines()

    names = [""] * len(data)
    scores = [0] * len(data)

    for loop in range(len(data)):
        data[loop] = data[loop][0:-1]
        x = data[loop].rfind(",")
        names[loop] = data[loop][:x]
        scores[loop] = int(data[loop][x + 1:])

    """
        For the testing of reading the text file into the interpreter:
        print("\n Text File Names:")
        for n in range(0,len(names)):
            print(names[n])
        print("\n Text File Scores:")
        for s in range(0,len(scores)):
            print(scores[s])
        """
    text_file.close()
    return names, scores


def sort(names, scores):
    for place in range(0, len(scores)):
        score = scores[place]
        name = names[place]
        pos = place
        while pos > 0 and scores[pos - 1] < score:
            scores[pos] = scores[pos - 1]
            names[pos] = names[pos - 1]
            pos -= 1
        scores[pos] = score
        names[pos] = name
    return names, scores


#-----------------------Main Function------------------------------#

def game(sprite):
    # Create the player
    P = Player(sprite)
    # Background Music
    song = pygame.mixer.music.load("8bit.ogg")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.25)

    # Create all the levels
    lvl_list = []
    lvl_list.append(Level_01(P))
    lvl_list.append(Level_02(P))
    lvl_list.append(Level_03(P))

    # Set the current level
    current_lvl_no = 0
    current_lvl = lvl_list[current_lvl_no]

    sprite_list = pygame.sprite.Group()
    P.level = current_lvl

    # Sets initial coords for player
    P.rect.x = 0
    P.rect.y = 400

    myfont = pygame.font.SysFont("monospace", 25)
    sprite_list.add(P)

    done = False

    def score():
        #if P.score > P.prevscore:
        #    print("Score: " + str(P.score))
        hud_display(str(P.score), (50, 26))

        if timer != -1:
            P.time = (pygame.time.get_ticks() - timer) / 1000
            P.time = str(P.time)
            P.time = P.time[0:4]
            hud_display(str(P.time), (660, 26))

    timer = pygame.time.get_ticks()
    # -----------------------------Main Program Loop--------------------------------#
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                done = True

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    P.go_left()
                if event.key == pygame.K_RIGHT:
                    P.go_right()
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    P.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and P.change_x <= 0:
                    P.stop()
                if event.key == pygame.K_RIGHT and P.change_x >= 0:
                    P.stop()
        # Update the player.
        sprite_list.update()

        # Update items in the level
        current_lvl.update()

        # If the player gets near the right side, shift the world left (-x)
        if P.rect.right >= 500:
            diff = P.rect.right - 500
            P.rect.right = 500
            current_lvl.shift_world(-diff)

        # If the player gets near the left side, shift the world right (+x)
        if P.rect.left <= 0:
            diff = 0 - P.rect.left
            P.rect.left = 0
            if P.change_x < 0:
                P.change_x = 0
            if P.change_x <= 0:
                diff = 0
            current_lvl.shift_world(diff)

        # If the player gets to the end of the level, go to the next level
        current_position = P.rect.x + current_lvl.world_shift
        if current_position < current_lvl.level_limit:
            if current_lvl_no < len(lvl_list) - 1:
                P.rect.x = 120
                scoreboard_lvl = current_lvl_no
                current_lvl_no += 1
                P.lvlno = current_lvl_no
                current_lvl = lvl_list[current_lvl_no]
                P.level = current_lvl

            else:
                # The game will quit if done is True
                timer = -1
                P.time = float(P.time)
                if P.time <= 16:
                    P.score += 2500
                if P.time > 16 and P.time <= 20:
                    P.score += 1750
                if P.time > 20 and P.time <= 25:
                    P.score += 500
                else:
                    P.score += 100
                scoreboard(P.score)


        current_lvl.draw(screen)
        sprite_list.draw(screen)
        P.hearts()
        score()
        build()

        # Limit to 60 frames per second
        clock.tick(FPS)

        pygame.display.flip()

    # Exits Game
    startScreen()


if __name__ == "__main__":
    startScreen()