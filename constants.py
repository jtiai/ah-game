import pygame as pg

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60
TITLE_SCREEN = 1
GAME = 2
GAME_OVER = 3
GAME_COUNTDOWN = 4
GAME_AREA = pg.Rect((0, 40), (639, 400))
BLACK = (0, 0, 0)
AMBER = (255, 191, 0)
GREEN = (51, 255, 0)
FONT_NAME = "fonts/notosanshk-black.otf"
SONGS = (
    "music/bouncing-around-in-pixel-town.ogg",
    "music/carefree-days-in-groovyville.ogg",
    "music/city-of-tomorrow.ogg",
    "music/pelican-bay-tiki-party.ogg",
    "music/trouble-in-a-digital-city.ogg",
)
GAME_OVER_SONG = "music/cyber-teen.ogg"
HIGH_SCORES = [(idx * 10, "JANU") for idx in range(20, 0, -1)]

HIGHSCORE_SCROLL_TOP_Y = 200
HIGHSCORE_SCROLL_HEIGHT = 160