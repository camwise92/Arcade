import os
import pygame
from os import listdir
from os.path import isfile, join, dirname, abspath
import sys


pygame.init()
pygame.mixer.init()

# Integration to group project: Import the scoreboard_manager module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scoreboard_manager import update_scoreboard

# Get the directory of the current script
script_dir = dirname(abspath(__file__))

# Define the paths to the assets directory
assets_dir = join(script_dir, "assets")
sounds_dir = join(assets_dir, "Sounds")

# Load sound files using the constructed paths
fruit_sound = pygame.mixer.Sound(join(sounds_dir, "gain_point.wav"))
hit_sound = pygame.mixer.Sound(join(sounds_dir, "lose_point.wav"))
game_over_sound = pygame.mixer.Sound(join(sounds_dir, "game_over.wav"))
finish_level_sound = pygame.mixer.Sound(join(sounds_dir, "level_up.wav"))
trampoline_sound = pygame.mixer.Sound(join(sounds_dir, "boing.wav"))

pygame.font.init()

pygame.display.set_caption("Sen's Adventure") # title of the window

WIDTH, HEIGHT = 1000, 800 # This is a good size for 2k, if coding in smaller monitor might need to reduce
FPS = 60
PLAYER_VEL = 4.5 # how fast the player will move across the screen

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF) # create the pygame window with double buffering to help flickering

def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    # Combine the directory paths to form the full path to the sprite sheets
    script_dir = dirname(abspath(__file__))
    path = join(script_dir, "assets", dir1, dir2)
    
    # Get a list of all files in the directory
    images = [f for f in listdir(path) if isfile(join(path,f))]
    
    # Dictionary to store all the sprites
    all_sprites = {}

    for image in images:
        try:
            # Load the sprite sheet image
            sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() 
        except pygame.error as e:
            continue

        # List to store individual sprites
        sprites = []
        
        # Extract individual sprites from the sprite sheet
        for i in range(sprite_sheet.get_width() // width):
            # Create a new surface for each sprite
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            
            # Define the rectangle area to extract from the sprite sheet
            rect = pygame.Rect(i * width, 0, width, height)
            
            # Blit (copy) the sprite from the sprite sheet to the surface
            surface.blit(sprite_sheet, (0, 0), rect)
            
            # Scale the sprite and add it to the list
            sprites.append(pygame.transform.scale2x(surface))

        base_name = image.replace(".png", "")

        if direction:
            all_sprites[base_name + "_right"] = sprites
            all_sprites[base_name + "_left"] = flip(sprites)
        else:
            all_sprites[base_name] = sprites

    return all_sprites

def get_block(size):
    """
    Load a block image from the "assets/Terrain/Terrain.png" file, extract a specific block from the image,
    and scale it to the desired size.

    Args:
        size (int): The desired size (width and height) of the block.

    Returns:
        pygame.Surface: A scaled pygame.Surface object representing the block.
    """
    script_dir = dirname(abspath(__file__)) # Get the directory of the current script
    path = join(script_dir, "assets", "Terrain", "Terrain.png") # Construct the path to the terrain image
    image = pygame.image.load(path).convert_alpha() # Load the image and convert it to have per-pixel alpha transparency

    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32) # Create a new surface with the specified size and alpha transparency
    rect = pygame.Rect(96, 0, size, size) # Define the rectangle area to extract from the terrain image (the block)

    surface.blit(image, (0, 0), rect) # Blit (copy) the extracted block from the terrain image to the new surface

    return pygame.transform.scale2x(surface) # Scale the surface by 2x and return it

class Player(pygame.sprite.Sprite): 
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "Sen", 32, 32, True)
    ANIMATION_DELAY = 6 # the delay between the animation frames

    def __init__(self, x, y , width, height):
        """
        self.rect - creates a pygame.Rect object, which is used to represent the position and size of the object in the game.
        self.x_vel and self.y_vel: variables store the objects velocity in the x and y directions.
        self.mask: This will be used for advanced collision detection 
        self.direction: This tracks the direction the object is facing or moving 
        self.animation_count: This is used to cycle through animation frames for the object.
        self.call_count = 0 - This is used to track how long the object has been falling for.
        """
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)  
        self.x_vel = 0 
        self.y_vel = 0 
        self.mask = None
        self.direction = "left" 
        self.animation_count = 0 
        self.fall_count = 0 
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.score = 0 # initialise the score
        self.fast_descent_triggered = False

    def jump(self):
        self.y_vel = -self.GRAVITY * 8 # jump velocity, its negative so we go up, but within loop() we have gravity constantly applied to bring us down
        self.animation_count = 0 
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0 # we want to remove the gravity as we are jumping (only if its the first jump we are making) - we are going to add double jump too
        
    def move(self, dx, dy):
        """
        dx and dy: These parameters represent the amount by which the object should move in the x and y directions, respectively.
        dx: Change in the x-direction (positive = right, negative = left).
        dy: Change in the y-direction (positive = down, negative = up).
        self.rect.x and self.rect.y: x and y coordinates of the object's pygame.Rect. Updating these values changes the object's position on the screen.
        """
        self.rect.x += dx
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0
        self.score -= 1 # if we hit a trap we lose a point
    
    def collect_fruit(self, points):
        self.score += points # if we collect a fruit we gain a point
    
    def move_left(self, vel):
        """
        Set the horizontal velocity to a negative value to move the object left.
        A negative velocity means the object's x-coordinate will decrease over time.
        Check if the object's current direction is not already "left".
        Update the direction to "left".
        Reset the animation counter to 0. This ensures the animation starts from the first frame when the direction changes.
        """
        self.x_vel = -vel 
        if self.direction != "left": 
            self.direction = "left" 
            self.animation_count = 0 
                                    
    def move_right(self, vel):
        """
        Set the horizontal velocity to a positive value to move the object right.
        A positive velocity means the object's x-coordinate will increase over time.
        Then uses the same process as move_left()
        """
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def fast_descent(self):
        if not self.fast_descent_triggered:
            self.y_vel = self.GRAVITY * 10 # if we press down we want to fall faster
            self.fast_descent_triggered = True

    def loop(self, fps):
        """
        This tells us how long we've been falling to then know how much we should be accelarating, to emulate the acceleration due to gravity.
        Using value 1 so the falling isnt incredibly slow at first
        Call the "move" method to update the object's position based on its current velocity.
        """
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY) 
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1 
        self.update_sprite()
    
    def landed(self):
        self.fall_count = 0 # reset the fall count to 0 when the player lands
        self.y_vel = 0 # stop the player from falling when they land
        self.jump_count = 0 

    def hit_head(self):
        self.count = 0
        self.y_vel = 0  

    def update_sprite(self):
        """ 
        Method is responsible for updating the player's sprite based on its current state, such as whether it is idle or running, and which direction it is facing.
        Determine which sprite sheet to use based on the player's horizontal velocity
        If x_vel is 0, the player is idle, so the sprite_sheet is set to "idle".
        If x_vel is not 0, the player is running, so the sprite_sheet is set to "run".
        """
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2: # this makes it so we need to have enough distance from graound before gravity kicks in otherwise the character glitches when idle
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        """
        Constructs the name of the sprite sheet by combining the sprite_sheet (either "idle" or "run") with the player's current direction (self.direction), resulting in names like "idle_left", "idle_right", "run_left", or "run_right".
        Retrieve the list of sprites corresponding to the constructed sprite_sheet_name from the SPRITES dictionary.
        Calculate the sprite_index by dividing the animation_count by the ANIMATION_DELAY and taking the remainder when divided by the length of the sprites list. This ensures the sprite_index cycles through the sprites list.
        Update the player's sprite to the sprite at the sprite_index in the sprites list.
        Increment the animation_count by 1 to cycle through the sprites.
        Call the update method to update the player's rect and mask based on the new sprite.

        """    
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        """
        Bound of our character is always adjusted based upon the sprite we are using
        Mask is mapping of all of the pixels that exist in the sprite, then allowing us to perform pixel perfect collision
        """
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
        """
        Base class which defines the properties we need for valid sprite. It inherits from the pygame.sprite.Sprite class, which means that Object is a type of sprite.
        The __init__ method initializes the object's position, dimensions, and name.
        The draw method renders the object's sprite onto the game window.
        """
        def __init__(self, x, y, width, height, name=None):
            super().__init__()
            self.rect = pygame.Rect(x, y, width, height)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA) # when we change the image, the draw will auto draw it on the screen 
            self.width = width
            self.height = height
            self.name = name

        def draw(self, win, offset_x):
            # Renders the player's sprite onto the game window
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class MovingPlatform(Block):
    def __init__(self, x, y, size, move_range, speed, direction="horizontal"):
        super().__init__(x, y, size)
        self.start_x = x
        self.start_y = y
        self.move_range = move_range
        self.speed = speed
        self.direction = direction
        self.moving_forward = True

    def move(self):
        if self.direction == "horizontal":
            if self.moving_forward:
                self.rect.x += self.speed
                if self.rect.x >= self.start_x + self.move_range:
                    self.moving_forward = False
            else:
                self.rect.x -= self.speed
                if self.rect.x <= self.start_x:
                    self.moving_forward = True
        elif self.direction == "vertical":
            if self.moving_forward:
                self.rect.y += self.speed
                if self.rect.y >= self.start_y + self.move_range:
                    self.moving_forward = False
            else:
                self.rect.y -= self.speed
                if self.rect.y <= self.start_y:
                    self.moving_forward = True

    def loop(self):
        self.move()

class Fire(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0 
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"
    
    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class SpikeHead(Object):
    ANIMATION_DELAY = 3
    
    def __init__(self, x, y, width=54, height=52):
        super().__init__(x, y, width, height, "spike_head")
        self.spike_head = load_sprite_sheets("Traps", "Spike Head", width, height)
        self.image = self.spike_head["idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "idle"
    
    def hit(self):
        self.animation_name = "hit"
        self.animation_count = 0

    def loop(self):
        sprites = self.spike_head[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Spikes(Object):
    def __init__(self, x, y, width=16, height=16):
        """
        Initialize the Spikes object.

        Args:
            x (int): The x-coordinate of the spike.
            y (int): The y-coordinate of the spike.
            width (int): The width of the spike.
            height (int): The height of the spike.
        """
        super().__init__(x, y, width, height, "spikes")
        try:
            script_dir = dirname(abspath(__file__))  # Get the directory of the current script
            image_path = join(script_dir, "assets", "Traps", "Spikes", "Idle.png")  # Construct the path to the spike image
            self.image = pygame.image.load(image_path).convert_alpha()  # Load the image and convert it to have per-pixel alpha transparency
            self.image = pygame.transform.scale2x(self.image)  # Scale the image by 2
            self.mask = pygame.mask.from_surface(self.image)
        except pygame.error as e:
            print(f"Error loading spike image {e}")

    def loop(self):
        pass

class Fruit(Object):
    def __init__(self, x, y, width, height, fruit_name, scale_factor=2):
        """
        Initialize the Fruit object.

        Args:
            x (int): The x-coordinate of the fruit.
            y (int): The y-coordinate of the fruit.
            width (int): The width of the fruit.
            height (int): The height of the fruit.
            fruit_name (str): The name of the fruit (e.g., "Melon").
            scale_factor (int): The factor by which to scale the fruit image.
        """
        super().__init__(x, y, width, height, "fruit")
        self.fruit_name = fruit_name
        try:
            script_dir = dirname(abspath(__file__))  # Get the directory of the current script
            image_path = join(script_dir, "assets", "Items", "Fruits", f"{fruit_name}.png")  # Construct the path to the fruit image
            self.image = pygame.image.load(image_path).convert_alpha()  # Load the image and convert it to have per-pixel alpha transparency
            self.image = pygame.transform.scale(self.image, (int(width * scale_factor), int(height * scale_factor)))  # Scale the image

            # Load the collected image
            collected_image_path = join(script_dir, "assets", "Items", "Fruits", "Collected.png")
            self.collected_image = pygame.image.load(collected_image_path).convert_alpha()
            self.collected_image = pygame.transform.scale(self.collected_image, (int(width * scale_factor), int(height * scale_factor)))  # Scale the collected image

            self.mask = pygame.mask.from_surface(self.image)
        except pygame.error as e:
            print(f"Error loading fruit image {e}")
        self.collected = False

    def collect(self):
        self.image = self.collected_image
        self.collected = True

class Trampoline(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width=28, height=28):
        super().__init__(x, y, width * 2, height * 2, "trampoline")
        self.trampoline = load_sprite_sheets("Traps", "Trampoline", width, height)
        self.image = pygame.transform.scale2x(self.trampoline["Idle"][0])
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle"

    def activate(self):
        self.animation_name = "Jump"
        self.animation_count = 0

    def loop(self):
        sprites = self.trampoline[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_name = "Idle"
            self.animation_count = 0

class ExitDoor(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        """
        Initialize the ExitDoor object.

        Args:
            x (int): The x-coordinate of the exit door.
            y (int): The y-coordinate of the exit door.
            width (int): The width of the exit door.
            height (int): The height of the exit door.
        """
        super().__init__()
        try:
            script_dir = dirname(abspath(__file__))  # Get the directory of the current script
            image_path = join(script_dir, "assets", "Items", "Checkpoints", "Level", "Exit_door.png")  # Construct the path to the exit door image
            self.image = pygame.image.load(image_path).convert_alpha()  # Load the image and convert it to have per-pixel alpha transparency
            self.image = pygame.transform.scale(self.image, (width * 3, height * 3))  # Scale the image
            self.rect = self.image.get_rect(topleft=(x, y))
            self.mask = pygame.mask.from_surface(self.image)
            self.name = "exit_door"  # Add the name attribute
        except pygame.error as e:
            print(f"Error loading exit door image: {e}")

    def draw(self, window, offset_x):
        """
        Draw the exit door on the screen.

        Args:
            window (pygame.Surface): The surface to draw on.
            offset_x (int): The horizontal offset for scrolling.
        """
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

        
"""
def get_player_name():
    name = ""
    font = pygame.font.SysFont(None, 72)
    input_box = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 50, 400, 100)
    active = True

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode

        window.fill((0, 0, 0))
        prompt_surface = font.render("Please input your name:", True, (255, 255, 255))
        window.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT // 2 - 150))
        txt_surface = font.render(name, True, (255, 255, 255))
        window.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        pygame.draw.rect(window, (255, 255, 255), input_box, 2)
        pygame.display.flip()

    return name
"""   
def get_background(name): 
    """
    Load the background image from the "assets/Background" directory.
    The join function is used to create a path that works across different operating systems.
    get_rect() method returns a pygame.Rect object with the dimensions of the image. We extract the width and height of the tile.
    The nested loops calculate how many tiles are needed to cover the screen width (WIDTH) and height (HEIGHT).
    The + 1 ensures that the entire screen is covered, even if the screen dimensions are not perfectly divisible by the tile dimensions.
    The pos variable stores the top-left corner position of each tile.
    These positions are stored in the tiles list.
    The function returns the tiles list (positions of all tiles) and the image (the tile image itself).
    """
    script_dir = dirname(abspath(__file__)) # Get the directory of the current script
    image_path = join(script_dir, "assets", "Background", name) # Construct the path to the image
    image = pygame.image.load(image_path).convert() # Load the image
    _, _, width, height = image.get_rect() # Get the dimensions of the image
    tiles = [] # this will store the positions of the tiles

    for i in range(WIDTH // width + 1): 
        # Uppercase is dimension of screen, lowercase is dimension of tile
        # This will calculate how many tiles are needed to file the screen in width and height
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height) # denotes position of top left hand corner of current tile added to the list
            tiles.append(pos)

    return tiles, image # know what image to use when drawing the tiles

def draw(window, background, bg_image, player, objects, offset_x):
    """
    The blit method is used to draw the bg_image onto the window at the position specified by tile.
    tile is a tuple containing the x and y coordinates of the top-left corner of the tile (e.g., [x, y]).
    The for tile in background loop iterates through all the tile positions stored in the background list.
    This ensures that the entire screen is covered with the background image.
    Updates the display to show the changes blit calls

    """
    window.fill((0, 0, 0)) # Clear the screen with a black color (or any other background color)

    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)
    
    if player is not None:
        player.draw(window, offset_x)

def draw_score(window, score):
    font = pygame.font.SysFont(None, 72)
    score_text = font.render(f"{score:03}", True, (189, 77, 87))  # Render the score in red
    score_rect = score_text.get_rect(topleft=(10, 10))
    window.blit(score_text, score_rect)

def handle_vertical_collision(player, objects, dy):
    """
    Handles if objects collide with the player vertically
    """
    collided_objects = []

    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):  # determines if 2 obj are colliding
            if dy > 0:
                player.rect.bottom = obj.rect.top  # if moving down on the screen then you will be colliding with top of object, so we take top of rect (essentially the characters feet) and make it equal to the top of the object colliding with 
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom  # if moving up on the screen then you will be colliding with bottom of object, so we take bottom of rect (essentially the characters head) and make it equal to the bottom of the object colliding with
                player.hit_head()
                player.y_vel = 0  # Set vertical velocity to zero to prevent sticking

            collided_objects.append(obj)
    return collided_objects  # we want to know what objects we have collided with so we can alter effects (e.g., if collide with fire etc.)

def collide(player, objects, dx):
    player.move(dx, 0) # checks if current vel would they hit a block
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0) # move the character back
    player.update()
    return collided_object
          
def handle_move(player, objects):
    """
    This function is responsible for handling player movement based on keyboard input.
    """
    keys = pygame.key.get_pressed()

    player.x_vel = 0 # so only moves when pressing key
    collide_left = collide(player, objects, -PLAYER_VEL * 2) # checks if we are colliding with anything when moving left
    collide_right = collide(player, objects, PLAYER_VEL * 2) # checks if we are colliding with anything when moving right

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
    if keys[pygame.K_DOWN]:
        player.fast_descent()
    else:
        player.fast_descent_triggered = False

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
            hit_sound.play()
        if obj and obj.name == "spike_head":
            obj.hit()
            player.make_hit()
            hit_sound.play()
        if obj and obj.name == "spikes":
            player.make_hit()
            hit_sound.play()
        if obj and obj.name == "fruit" and not obj.collected:
            points = 10 if obj.fruit_name == "Trophy" else 2  # 10 points for trophy, 2 points for other fruitspoints for other fruits
            player.collect_fruit(points)
            obj.collect()
            objects.remove(obj)
            fruit_sound.play() 
        if obj and obj.name == "trampoline":
            obj.activate()
            player.y_vel = -player.GRAVITY * 12  # Increase jump velocity
            trampoline_sound.play()
        if obj and obj.name == "exit_door":
            player.score += 100
            finish_level_sound.play()
            return True
        
    return False  # Indicate that the player has not reached the exit door

def draw_overlay(window, alpha=128):
    overlay = pygame.Surface((WIDTH, HEIGHT))  # Create a surface with the same size as the window
    overlay.set_alpha(alpha)  # Set the alpha value (0 is fully transparent, 255 is fully opaque)
    overlay.fill((0, 0, 0))  # Fill the surface with black color
    window.blit(overlay, (0, 0))  # Draw the overlay on the window

def draw_welcome_screen(window, background, bg_image):
    draw(window, background, bg_image, None, [], 0)  # Draw the game background
    draw_overlay(window, alpha=128)  # Draw a semi-transparent overlay with 50% opacity
    font = pygame.font.SysFont(None, 72)
    welcome_text = font.render("Welcome to Sen's Adventures", True, (189, 77, 87))
    welcome_rect = welcome_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(welcome_text, welcome_rect)
    pygame.display.update()

def draw_death_message(window):
    draw_overlay(window, alpha=128)  # Draw a semi-transparent overlay with 50% opacity
    font = pygame.font.SysFont(None, 72)
    death_text = font.render("You have crossed the Rainbow Bridge", True, (189, 77, 87))
    death_rect = death_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(death_text, death_rect)
    pygame.display.update()
    pygame.time.delay(2000)  # Pause for 5 seconds before closing the game.
    window.fill((0, 0, 0))  # Clear the screen
    pygame.display.update()

def draw_play_again_message(window):
    window.fill((0, 0, 0))  # Clear the screen

    font = pygame.font.SysFont(None, 72)
    play_again_text = font.render("Do you want to play again? (Y/N)", True, (189, 77, 87))
    play_again_rect = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(play_again_text, play_again_rect)
    pygame.display.update()

def draw_final_score(window, score):
    draw_overlay(window, alpha=128)  # Draw a semi-transparent overlay with 50% opacity
    font = pygame.font.SysFont(None, 72)
    score_text = font.render(f"Final Score: {score:03}", True, (189, 77, 87))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(score_text, score_rect)
    pygame.display.update()

def create_level():
    block_size = 96
    blocks = [
        # Ground Floor
        *[Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)],

        # Platforms
        Block(block_size * 5, HEIGHT - block_size * 3, block_size),
        Block(block_size * 8, HEIGHT - block_size * 5, block_size),
        Block(block_size * 9, HEIGHT - block_size * 5, block_size),
        Block(block_size * 12, HEIGHT - block_size * 7, block_size),
        Block(block_size * 14.5, HEIGHT - block_size * 6, block_size),
        Block(block_size * 16.9, HEIGHT - block_size * 3, block_size),
        Block(block_size * 20.8, HEIGHT - block_size * 5, block_size),
        Block(block_size * 23, HEIGHT - block_size * 6, block_size),
        Block(block_size * 24, HEIGHT - block_size * 6, block_size),
        
        # Moving platforms
        MovingPlatform(block_size * 6, HEIGHT - block_size * 4, block_size, 200, 2, "horizontal"),
        MovingPlatform(block_size * 10, HEIGHT - block_size * 6, block_size, 150, 2, "vertical"),
    ]
    
    # Traps
    fires = [
        Fire(block_size * 12, HEIGHT - block_size - 64, 16, 32),
        Fire(block_size * 11, HEIGHT - block_size - 64, 16, 32),
    ]

    for fire in fires:
        fire.on()   
    
    # Spike Heads
    spike_heads = [
        SpikeHead(block_size * 7, HEIGHT - block_size * 4 - 52, 54, 52),
        SpikeHead(block_size * 13.8, HEIGHT - block_size * 7 - 52, 54, 52),
    ]
    
    # Spikes
    spikes = [
        # increments of .4 put the spikes in a row together
        Spikes(block_size * 2.2, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 2.6, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 3, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 3.4, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 3.8, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 4.2, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 15.4, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 15.8, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 16.2, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 16.6, HEIGHT - block_size - 32, 16, 16),
        Spikes(block_size * 17, HEIGHT - block_size - 32, 16, 16),
    ]

    # Fruits
    fruits = [
        Fruit(block_size * -11, HEIGHT - block_size * 1.5, 32, 32, "Melon"),
        Fruit(block_size * -2.5, HEIGHT - block_size * 1.5, 32, 32, "Strawberry"),
        Fruit(block_size * -3, HEIGHT - block_size * 2, 32, 32, "Strawberry"),
        Fruit(block_size * -3.5, HEIGHT - block_size * 2.5, 32, 32, "Strawberry"),
        Fruit(block_size * -4, HEIGHT - block_size * 3, 32, 32, "Strawberry"),
        Fruit(block_size * -4.5, HEIGHT - block_size * 3.5, 32, 32, "Strawberry"),
        Fruit(block_size * -5, HEIGHT - block_size * 3, 32, 32, "Strawberry"),
        Fruit(block_size * -5.5, HEIGHT - block_size * 2.5, 32, 32, "Strawberry"),
        Fruit(block_size * -6, HEIGHT - block_size * 2, 32, 32, "Strawberry"),
        Fruit(block_size * 2.5, HEIGHT - block_size * 4, 32, 32, "Bananas"),
        Fruit(block_size * 3.5, HEIGHT - block_size * 5, 32, 32, "Bananas"),
        Fruit(block_size * 4.5, HEIGHT - block_size * 6, 32, 32, "Bananas"),
        Fruit(block_size * 8.65, HEIGHT - block_size * 6, 32, 32, "Melon"),
        Fruit(block_size * 11.3, HEIGHT - block_size * 1.5, 32, 32, "Cherries"),
        Fruit(block_size * 12, HEIGHT - block_size * 8, 32, 32, "Cherries"),
        Fruit(block_size * 14.5, HEIGHT - block_size * 6.5, 32, 32, "Bananas"),
        Fruit(block_size * 16, HEIGHT - block_size * 8, 32, 32, "Melon"),
        Fruit(block_size * 16, HEIGHT - block_size * 7, 32, 32, "Melon"),
        Fruit(block_size * 16, HEIGHT - block_size * 6, 32, 32, "Melon"),
        Fruit(block_size * 16, HEIGHT - block_size * 5, 32, 32, "Melon"),
        Fruit(block_size * 20.95, HEIGHT - block_size * 5.65, 32, 32, "Trophy", scale_factor=2),
    ]

    trampoline = [
        Trampoline(99, HEIGHT - block_size - 112, 28, 28),
        Trampoline(1800, HEIGHT - block_size - 112, 28, 28)  # Centered horizontally
    ]

    # Exit Door
    exit_door = ExitDoor(2253, HEIGHT - block_size * 7.4, 64, 64)
    return blocks + fires + spike_heads + spikes + fruits + trampoline + [exit_door]
    
def start(window, player_name):
    game_name = "sens_adventures"
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
             for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]  # creates a floor of blocks
    objects = floor + create_level()
    
    offset_x = 0
    scroll_area_width = 200  # when have 200 px left on the screen, we want to start scrolling
    
    # Show the welcome screen
    draw_welcome_screen(window, background, bg_image)
    finish_level_sound.play()
    pygame.time.delay(2000)  # Display the welcome screen for 3 seconds

    while True:
        run = True
        while run:
            clock.tick(FPS)  # our loop will only run at this speed

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player.jump_count < 2:
                        player.jump()
            
            player.loop(FPS)
            for obj in objects:
                if isinstance(obj, Fire) or isinstance(obj, SpikeHead) or isinstance(obj, MovingPlatform) or isinstance(obj, Spikes):
                    obj.loop()

            reached_exit = handle_move(player, objects)
            draw(window, background, bg_image, player, objects, offset_x)
            draw_score(window, player.score)  # Draw the score on the screen

            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel

            # Check if the player falls off the screen
            if player.rect.top > HEIGHT:
                player.score = -1000
                game_over_sound.play()
                draw_death_message(window)
                pygame.time.delay(2000)
                draw_final_score(window, player.score)
                pygame.time.delay(2000)
                draw_play_again_message(window)
                run = False

            if reached_exit:
                draw_final_score(window, player.score)
                pygame.time.delay(2000)  # Display the final score for 2 seconds
                draw_play_again_message(window)
                run = False

            pygame.display.update()  
        
        play_again = True
        while play_again:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    play_again = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        play_again = False
                        break  # Break out of the inner loop to restart the game
                    elif event.key == pygame.K_n:
                        play_again = False
                        update_scoreboard("sens_adventure_game", player_name, player.score)
                        return player.score  # Return the score to the menu

    pygame.quit()
    quit()

if __name__ == "__main__":
    player_name = sys.argv[1] if len(sys.argv) > 1 else "Player"
    start(window, player_name)
