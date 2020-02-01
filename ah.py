# Copyright 2020 Jani Tiainen
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import random
import pygame as pg
import ptext
import sys

# Initialize Pygame
pg.init()

BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))


def get_resource(resource):
    return os.path.join(BUNDLE_DIR, resource)


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

FONT_NAME = get_resource("fonts/RussoOne-Regular.ttf")

ptext.DEFAULT_FONT_NAME = FONT_NAME

SONGS = (
    get_resource("music/bouncing-around-in-pixel-town.mp3"),
    get_resource("music/carefree-days-in-groovyville.mp3"),
    get_resource("music/city-of-tomorrow.mp3"),
    get_resource("music/pelican-bay-tiki-party.mp3"),
    get_resource("music/trouble-in-a-digital-city.mp3"),
)

GAME_OVER_SONG = get_resource("music/cyber-teen.mp3")

SOUNDS = {
    "pick": pg.mixer.Sound(get_resource("sfx/pick.ogg")),
    "bubble": pg.mixer.Sound(get_resource("sfx/bubble.ogg")),
    "end": pg.mixer.Sound(get_resource("sfx/end.ogg")),
    "player": pg.mixer.Sound(get_resource("sfx/player.ogg")),
}

END_MUSIC = pg.USEREVENT + 2


class Bubble:
    def __init__(self, pos, lifetime):
        self.lifetime = lifetime
        self.liferemaining = lifetime
        self.image = pg.Surface((30, 30))
        pg.draw.circle(self.image, AMBER, (15, 15), 15)
        self.rect = self.image.get_rect(center=pos)
        self.scaled_rect = self.rect.copy()

    def update(self, delta_time):
        self.liferemaining -= delta_time
        if self.liferemaining <= 0:
            return False
        return True

    def draw(self, surface):
        # Scale surface
        w, h = self.rect.size
        w = int(w * self.liferemaining / self.lifetime)
        h = int(h * self.liferemaining / self.lifetime)
        img = pg.transform.scale(self.image, (w, h))
        self.scaled_rect = img.get_rect(center=self.rect.center)
        surface.blit(img, self.scaled_rect)

    def get_points(self):
        return max(int(self.liferemaining / self.lifetime * 20), 1)

    def check_collision(self, rect):
        return self.scaled_rect.colliderect(rect)


class Context:
    pass


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN | pg.SCALED
        )
        self.clock = pg.time.Clock()

        self.songs = SONGS[:]
        self.song_index = 0
        pg.mixer.music.set_endevent(END_MUSIC)
        pg.mixer.music.load(self.songs[self.song_index])
        pg.mixer.music.play()
        pg.display.set_caption("ÄH!")

        self.player = pg.Surface((25, 25))
        self.player.fill(GREEN)

        self.game_state = {
            TITLE_SCREEN: (self.title_event, self.title_update, self.title_draw,),
            GAME_COUNTDOWN: (
                self.countdown_event,
                self.countdown_update,
                self.countdown_draw,
            ),
            GAME: (self.game_event, self.game_update, self.game_draw,),
            GAME_OVER: (self.gameover_event, self.gameover_update, self.gameover_draw,),
        }

        self.state = None
        self.context = self.title_start(None)

    # Title screen
    def title_start(self, old_context):
        self.state = TITLE_SCREEN
        context = Context()
        context.done = False
        return context

    def title_event(self, context, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            context.done = True

    def title_update(self, context, delta_time):
        if context.done:
            context.done = False
            return self.countdown_start
        return None

    def title_draw(self, context, surface):
        ptext.draw("ÄH!", midtop=(SCREEN_WIDTH // 2, 20), color=AMBER, fontsize=40)
        ptext.draw(
            "CLICK MOUSE BUTTON\nTO BEGIN",
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            color=AMBER,
            fontsize=40,
        )
        ptext.draw(
            "You are the green box trying to catch the appearing\n"
            + "bubbles by clicking towards them with your mouse.\n"
            + "The faster you click, the faster your player moves.\n"
            + "Be quick, you have only 30 seconds.\n\n"
            + "Press ESC to quit.",
            midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 5),
            color=AMBER,
            fontsize=18,
            align="left",
        )

    # Countdown screen
    def countdown_start(self, old_context):
        self.state = GAME_COUNTDOWN
        context = Context()
        context.count = 4000
        return context

    def countdown_event(self, context, event):
        pass

    def countdown_update(self, context, delta_time):
        context.count -= delta_time
        count = context.count // 1000
        context.text = f"{count}" if count else "GO!"
        if context.count < 0:
            return self.game_start

    def countdown_draw(self, context, surface):
        ptext.draw(
            context.text,
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            color=AMBER,
            fontsize=40,
        )

    # Game screen
    def game_start(self, old_context):
        self.state = GAME
        context = Context()
        context.player = self.player
        player_rect = self.player.get_rect()
        player_rect.centerx = random.randint(70, 570)
        player_rect.centery = random.randint(50, 430)
        context.player_rect = player_rect
        context.src_vec = pg.Vector2(player_rect.center)
        context.score = 0
        context.bubbles = []
        context.next_bubble = random.randint(1500, 5000)
        context.time_remaining = 30000
        context.speed_factor = 0.98
        context.tgt_vec = None
        context.speed = 0.0
        context.old_speed = 0.0
        return context

    def game_event(self, context, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # Move player towards clicked place
            context.dst_vec = pg.Vector2(event.pos)
            tgt_vec = context.dst_vec - context.src_vec
            tgt_vec.normalize_ip()
            context.tgt_vec = tgt_vec
            context.speed_factor = 0.98
            if context.speed <= 5.0:
                context.speed += 0.8

    def game_update(self, context, delta_time):
        context.next_bubble -= delta_time
        if context.next_bubble <= 0:
            context.next_bubble = random.randint(500, 2000)
            x = random.randint(50, 590)
            y = random.randint(50, 430)
            new_bubble = Bubble((x, y), random.randint(1000, 7000))
            context.bubbles.append(new_bubble)
            SOUNDS["bubble"].play()

        if context.tgt_vec:
            context.src_vec += context.tgt_vec * context.speed
            context.player_rect.centerx = int(context.src_vec.x)
            context.player_rect.centery = int(context.src_vec.y)
            cur_vec = pg.Vector2(context.player_rect.center)
            dist_squared = context.dst_vec.distance_squared_to(cur_vec)
            if dist_squared <= 2:
                context.speed_factor = 0.9
            if context.speed > 0:
                context.speed *= context.speed_factor
                if context.speed < 0.06:
                    context.speed = 0
                    context.tgt_vec = None
            if context.player_rect.left < GAME_AREA.left + 2:
                context.tgt_vec.x = -self.game_context.tgt_vec.x
                context.src_vec += context.tgt_vec * context.speed
                context.player_rect.centerx = int(context.src_vec.x)
            if context.player_rect.right > GAME_AREA.right - 2:
                context.tgt_vec.x = -context.tgt_vec.x
                context.src_vec += context.tgt_vec * context.speed
                context.player_rect.centerx = int(context.src_vec.x)
            if context.player_rect.top < GAME_AREA.top + 2:
                context.tgt_vec.y = -context.tgt_vec.y
                context.src_vec += context.tgt_vec * context.game_context.speed
                context.player_rect.centery = int(context.src_vec.y)
            if context.player_rect.bottom > GAME_AREA.bottom - 2:
                context.tgt_vec.y = -context.tgt_vec.y
                context.src_vec += context.tgt_vec * context.speed
                context.player_rect.centery = int(context.src_vec.y)

        for bubble in context.bubbles[:]:
            if bubble.check_collision(context.player_rect):
                # Player hit the bubble
                SOUNDS["pick"].play()
                context.score += bubble.get_points()
                context.bubbles.remove(bubble)
                continue
            if not bubble.update(delta_time):
                # Bubble died
                context.bubbles.remove(bubble)
                continue

        # Player movement sound
        if context.speed > 0:
            if context.old_speed == 0:
                # Movement started
                SOUNDS["player"].play(-1)
            SOUNDS["player"].set_volume(context.speed / 5.0)
        else:
            # Movement stopped
            SOUNDS["player"].stop()

        context.time_remaining -= delta_time
        if context.time_remaining <= 0:
            return self.gameover_start

        context.old_speed = context.speed

    def game_draw(self, context, surface):
        pg.draw.rect(surface, AMBER, GAME_AREA, width=2)
        for bubble in context.bubbles:
            bubble.draw(surface)

        ptext.draw(
            f"SCORE: {context.score:05}", topleft=(5, 5), color=AMBER, fontsize=18,
        )
        ptext.draw(
            f"TIME LEFT: {context.time_remaining // 1000}",
            topleft=(500, 5),
            fontsize=18,
            color=AMBER,
        )
        surface.blit(context.player, context.player_rect)

        # Speedmeter
        spd = int(630 * context.speed / 5.0)
        speed_meter = pg.Rect((5, 445), (spd, 20))
        surface.fill(AMBER, speed_meter)

    # Game over screen
    def gameover_start(self, old_context):
        self.state = GAME_OVER
        context = Context()
        context.count = 60000
        context.score = old_context.score
        context.end_jingle_start = context.count - 250
        context.end_jingle_stop = 60000 - SOUNDS["end"].get_length() * 1000
        context.played_fanfare = False
        pg.mixer.music.set_endevent()
        pg.mixer.music.fadeout(250)
        return context

    def gameover_event(self, context, event):
        if context.count < 50000 and event.type == pg.MOUSEBUTTONDOWN:
            pg.mixer.music.fadeout(500)
            context.count = 0

    def gameover_update(self, context, delta_time):
        context.count -= delta_time
        if context.count < context.end_jingle_start:
            context.end_jingle_start = -1
            SOUNDS["end"].play()
        if context.count < context.end_jingle_stop:
            context.end_jingle_stop = -1
            pg.mixer.music.load(GAME_OVER_SONG)
            pg.mixer.music.play()
            pg.mixer.music.set_endevent(END_MUSIC)

        if context.count <= 0:
            return self.title_start

    def gameover_draw(self, context, surface):
        ptext.draw(
            "GAME OVER",
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            color=AMBER,
            fontsize=60,
        )
        ptext.draw(
            f"SCORE: {context.score:05}", topleft=(5, 5), fontsize=18, color=AMBER,
        )

    def game_loop(self):
        while True:
            delta_time = self.clock.tick(FPS)
            self.screen.fill(BLACK)

            event_handler, update_handler, draw_handler = self.game_state[self.state]

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    sys.exit()

                if event.type == END_MUSIC:
                    self.song_index += 1
                    if self.song_index == len(self.songs):
                        last_song = self.songs[-1]
                        self.songs = self.songs[:-1]
                        random.shuffle(self.songs)
                        self.songs.insert(
                            random.randint(
                                len(self.songs) // 4,
                                len(self.songs) - len(self.songs) // 4 - 1,
                            ),
                            last_song,
                        )
                        self.song_index = 0
                    pg.mixer.music.load(SONGS[self.song_index])
                    pg.mixer.music.play()

                event_handler(self.context, event)

            next_state = update_handler(self.context, delta_time)
            if next_state:
                self.context = next_state(self.context)
                continue  # Restart gameloop

            draw_handler(self.context, self.screen)
            pg.display.flip()


if __name__ == "__main__":
    Game().game_loop()
