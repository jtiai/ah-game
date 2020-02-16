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
    "music/bouncing-around-in-pixel-town.mp3",
    "music/carefree-days-in-groovyville.mp3",
    "music/city-of-tomorrow.mp3",
    "music/pelican-bay-tiki-party.mp3",
    "music/trouble-in-a-digital-city.mp3",
)
GAME_OVER_SONG = "music/cyber-teen.mp3"
HIGH_SCORES = [(idx * 10, "JANU") for idx in range(20, 0, -1)]

HIGHSCORE_SCROLL_TOP_Y = 200
HIGHSCORE_SCROLL_HEIGHT = 160