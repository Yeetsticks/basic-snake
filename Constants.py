import pygame

DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT = 500, 500
INTERNAL_SCREEN_WIDTH, INTERNAL_SCREEN_HEIGHT = 20, 20

FPS = 3

COLOUR_PALLET = {
    "Board": (  3,  49,  56),
    "Snake": ( 84, 143, 153),
    "Apple": (126, 196, 207)
}

KEYBINDS = {
    "up":   pygame.K_w, 
    "left": pygame.K_a, 
    "down": pygame.K_s, 
    "right":pygame.K_d
} # WASD

SOUND_PATHS = {
    "up":    "assets/sound/up.mp3",
    "down":  "assets/sound/down.mp3",
    "left":  "assets/sound/left.mp3",
    "right": "assets/sound/right.mp3",
    "eat":   "assets/sound/consumption.mp3",
    "death": "assets/sound/death.mp3"
}