import random
import pygame
from Constants import *

pygame.init()

class Canvas:
    '''Handles Window Display'''
    def __init__(self):
        self.window = pygame.display.set_mode((DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT), pygame.RESIZABLE)
        self.screen = pygame.Surface((INTERNAL_SCREEN_WIDTH, INTERNAL_SCREEN_HEIGHT))

        self.update_scale()


    def update_scale(self):
        '''
        Calculates the scale required from the internal screen to the window.

        Outputs to self.scale

        (Requires self.window and self.screen)
        '''
        win_x, win_y = self.window.get_size()
        screen_x, screen_y = self.screen.get_size()

        ratio = screen_x / screen_y # Makes it 1:ratio

        # Multiplying both sides by ratio means it *should* be 1:1, allowing direct comparison.
        if win_x <= (win_y * ratio):
            self.scale = win_x/screen_x

        else:
            self.scale = win_y/screen_y


    def update(self):
        '''Passes internal screen to the window, ensuring it's displayed correctly.'''
        scaled_screen = pygame.transform.scale_by(self.screen, self.scale) # Scaling
        self.scaled_screen_rect = scaled_screen.get_rect()
        self.scaled_screen_rect.center = self.window.get_rect().center # Centering

        self.window.blit(scaled_screen, self.scaled_screen_rect) # Blitting
        pygame.display.flip()
        
class State:
    '''State Class, used for easily switching and grouping behaviours within the program.'''
    def __init__(self, canvas:Canvas):
        self.canvas = canvas
        self.done = False
        self.nextState = None # nextState of None means Application will close when done

    def update(self):
        '''Hook Method'''
        pass

    def handle_event(self, event):
        pass

class Snake(State):
    '''The Main Game State Class'''

    class PlayerBit(pygame.sprite.Sprite):
        def __init__(self, pos, image):
            super().__init__()
            self.image = image
            self.rect = pygame.Rect(pos, self.image.get_size())
            self.dead = False
            if self.rect.x < 0 or self.rect.y < 0:
                self.dead = True
            if self.rect.x >= INTERNAL_SCREEN_WIDTH or self.rect.y >= INTERNAL_SCREEN_HEIGHT:
                self.dead = True
    class Player(pygame.sprite.Group):
            def __init__(self, image):
                super().__init__()
                self.playerbits = []
                self.direction = "left"
                self.image = image
                self.eating = 0

            def addPlayerBit(self, pos):
                newBit = Snake.PlayerBit(pos, self.image)
                newBit.add(self)
                self.playerbits.insert(0, newBit)
        
            def move(self, direction):
                currentX, currentY = self.playerbits[0].rect.topleft 

                if direction == "left":
                    self.addPlayerBit((currentX-1, currentY))

                if direction == "right":
                    self.addPlayerBit((currentX+1, currentY))
                    
                if direction == "up":
                    self.addPlayerBit((currentX, currentY-1))
                    
                if direction == "down":
                    self.addPlayerBit((currentX, currentY+1))


                if self.eating <= 0:
                    self.playerbits[-1].kill()
                    self.playerbits.pop(-1)
                else:
                    self.eating -= 1
            
    class Apples(pygame.sprite.Group):
        pass
    class Apple(pygame.sprite.Sprite):
        def __init__(self, pos, image):
            super().__init__()
            self.image = image
            self.rect = pygame.Rect(pos, self.image.get_size())
    
    def __init__(self, canvas:Canvas):
        super().__init__(canvas)
        self.nextState = Menu
        self.inputed = False

        self.snake_surface = pygame.Surface((1, 1))
        self.snake_surface.fill(COLOUR_PALLET["Snake"])
        self.apple_surface = pygame.Surface((1, 1))
        self.apple_surface.fill(COLOUR_PALLET["Apple"])  

        # Load all sounds into Sound Class
        self.sounds = {key: pygame.mixer.Sound(SOUND_PATHS[key]) for key in SOUND_PATHS}    

        self.player = self.Player(self.snake_surface)  
        self.player.addPlayerBit((INTERNAL_SCREEN_WIDTH//2, INTERNAL_SCREEN_HEIGHT//2))

        self.apples = self.Apples()
        self.placeApple()

    def update(self):
        self.inputed = False # Resetting input limit
        # Move
        self.player.move(self.player.direction)

        # Apple Eating
        chomps = pygame.sprite.groupcollide(self.player, self.apples, dokilla=False, dokillb=True)

        for chomped in chomps: 
            for _ in chomps[chomped]: # Iterates for every collided apple
                self.placeApple()
                self.player.eating += 1
                self.playSound("eat")


        # Self Collision
        collisions = [sprite for sprite in pygame.sprite.spritecollide(self.player.playerbits[0], self.player, False) if sprite != self.player.playerbits[0]]

        if collisions:
            self.player.playerbits[0].dead = True

        # Death 
        for bit in self.player.sprites():
            if bit.dead:
                self.playSound("death")
                self.done = True

        # Render
        self.canvas.screen.fill(COLOUR_PALLET["Board"])
        self.player.draw(self.canvas.screen)
        self.apples.draw(self.canvas.screen)
        self.canvas.update()

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.QUIT: # Quiting
            self.nextState = None
            self.done = True

        if event.type == pygame.WINDOWRESIZED: # Resize
            self.canvas.update_scale()

        if event.type == pygame.KEYDOWN and not self.inputed: # Inputs (limited to one per frame)
            for key in KEYBINDS:
                if event.key == KEYBINDS[key]:

                    # Checking for viable direction
                    if (self.player.direction != key):
                        keys = [key for key in KEYBINDS]
                        if self.player.direction == keys[list(keys).index(key)-2]: # Checks opposite direction
                            continue
                        self.player.direction = key
                        self.playSound(key)
                        self.inputed = True

    def placeApple(self):
        x = random.randint(0, INTERNAL_SCREEN_WIDTH-1)
        y = random.randint(0, INTERNAL_SCREEN_HEIGHT-1)

        self.apples.add(self.Apple((x, y), self.apple_surface))

    def playSound(self, sound):
        self.sounds[sound].play()

class Menu(State):
    class Button(pygame.sprite.Sprite):
        
        def __init__(self, width, height, x=0, y=0, centerX = False, centerY = False, text = "Play"):
            '''
            Creates a button with given width and height. 
            
            centerX and centerY overwrite the x and y position
            '''
            
            self.rect = pygame.Rect(x, y, width, height)

            if centerX:
                self.rect.centerx = INTERNAL_SCREEN_WIDTH//2
            if centerY:
                self.rect.centery = INTERNAL_SCREEN_HEIGHT//2

            self.render(text)


        def render(self, text):
            '''Creates the surface/image of the button'''

            self.image = pygame.Surface(self.rect.size)
            self.image.fill(COLOUR_PALLET["Board"])

            self.font = pygame.font.SysFont("Ariel", 14)
            self.text = self.font.render(text, False, COLOUR_PALLET["Apple"])
            text_pos = self.text.get_rect()
            text_pos.center = self.rect.center
            self.image.blit(self.text, text_pos)

        def draw(self, surface:pygame.Surface):
            surface.blit(self.image, self.rect)
            
    def __init__(self, canvas):
        super().__init__(canvas)
        self.nextState = Snake

        self.button = self.Button(20, 20, centerX=True, centerY=True)

    def update(self):
        self.button.draw(self.canvas.screen)
        self.canvas.update()

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.QUIT:
            self.nextState = None
            self.done = True
        if event.type == pygame.MOUSEBUTTONUP:
            x = (event.pos[0] - self.canvas.scaled_screen_rect.left) / self.canvas.scale
            y = (event.pos[1] - self.canvas.scaled_screen_rect.top) / self.canvas.scale
            print(f"{x}, {y}")
            if self.button.rect.collidepoint(x, y):
                self.done = True

        


running = True

clock = pygame.time.Clock()
canvas = Canvas()
current_state = Menu(canvas)

while running:
     
    if current_state.done:
        # Program Exiting
        if current_state.nextState == None:
            running = False
            break

        # State Switching
        current_state = current_state.nextState(canvas)


    for event in pygame.event.get():
        current_state.handle_event(event)

    current_state.update()

    clock.tick(FPS)