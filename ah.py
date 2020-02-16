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
import json
import pygame as pg
import ptext
import sys

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE_SCREEN, GAME, GAME_OVER, GAME_COUNTDOWN, GAME_AREA, BLACK, \
    AMBER, FONT_NAME, SONGS, GAME_OVER_SONG, HIGH_SCORES, HIGHSCORE_SCROLL_TOP_Y, HIGHSCORE_SCROLL_HEIGHT

# Initialize Pygame
pg.init()
screen = pg.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT) #, pg.FULLSCREEN | pg.SCALED
)

ptext.DEFAULT_FONT_NAME = FONT_NAME

SOUNDS = {
    "pick": pg.mixer.Sound("sfx/pick.ogg"),
    "bubble": pg.mixer.Sound("sfx/bubble.ogg"),
    "end": pg.mixer.Sound("sfx/end.ogg"),
    "player": pg.mixer.Sound("sfx/player.ogg"),
}

END_MUSIC = pg.USEREVENT + 2

BUBBLE_IMAGE = pg.image.load("gfx/normal_ball.png").convert_alpha()
BUBBLE_IMAGE.set_colorkey(BLACK)
SPECIAL_IMAGE = pg.image.load("gfx/special.png").convert_alpha()
SPECIAL_IMAGE.set_colorkey(BLACK)


def vec_to_int(vector):
    return tuple(map(int, vector))


class Bubble:
    def __init__(self, pos, lifetime):
        self.lifetime = lifetime
        self.liferemaining = lifetime
        self.image = BUBBLE_IMAGE
        self.rect = self.image.get_rect(center=pos)
        self.scaled_rect = self.rect.copy()
        self.angle = random.uniform(0, 360)
        self.rotation = random.uniform(-2.0, 2.0)

    def update(self, delta_time):
        self.angle += self.rotation
        self.liferemaining -= delta_time
        if self.liferemaining <= 0:
            return False
        return True

    def draw(self, surface):
        scale = self.liferemaining / self.lifetime
        img = pg.transform.rotozoom(self.image, self.angle, scale)
        self.scaled_rect = img.get_rect(center=self.rect.center)
        surface.blit(img, self.scaled_rect)

    def play_sound(self):
        SOUNDS["pick"].play()

    def do_action(self, context):
        context.score += max(int(self.liferemaining / self.lifetime * 20), 1)

    def check_collision(self, rect):
        return self.scaled_rect.colliderect(rect)


class Powerup(Bubble):
    def __init__(self, pos, lifetime):
        super().__init__(pos, lifetime)
        self.image = SPECIAL_IMAGE

    def play_sound(self):
        SOUNDS["pick"].play()

    def do_action(self, context):
        context.time_remaining += random.randint(5, 15) * 1000


class Player:
    MIN_DIST = 10
    MAX_DIST = 20

    def __init__(self):
        self.images = [
            pg.image.load("gfx/slimeball_100.png").convert_alpha(),
            pg.image.load("gfx/slimeball_80.png").convert_alpha(),
            pg.image.load("gfx/slimeball_64.png").convert_alpha(),
            pg.image.load("gfx/slimeball_51.png").convert_alpha(),
            pg.image.load("gfx/slimeball_40.png").convert_alpha(),
        ]
        self.pos = [pg.Vector2() for _ in range(5)]
        self.vec = pg.Vector2()
        self.vec_dt = pg.Vector2()

    @property
    def rect(self):
        return self.images[0].get_rect(center=(vec_to_int(self.pos[0])))

    def set_pos(self, x, y):
        self.pos[0].xy = (x, y)
        self.pos[1].xy = (x + 18, y)
        self.pos[2].xy = (x + 28, y)
        self.pos[3].xy = (x + 38, y)
        self.pos[4].xy = (x + 48, y)

    def update(self, target_vec, speed):
        self.pos[0] += target_vec * speed
        rect = self.images[0].get_rect(center=vec_to_int(self.pos[0]))

        if rect.left < GAME_AREA.left + 2:
            targt_vec.x = -target_vec.x
            self.pos[0] += target_vec * speed
            rect.centerx = int(self.vec.x)
        if rect.right > GAME_AREA.right - 2:
            target_vec.x = -target_vec.x
            self.pos[0] += target_vec * speed
            rect.centerx = int(self.vec.x)
        if rect.top < GAME_AREA.top + 2:
            target_vec.y = -target_vec.y
            self.pos[0] += target_vec * speed
            rect.centery = int(self.vec.y)
        if rect.bottom > GAME_AREA.bottom - 2:
            target_vec.y = -target_vec.y
            self.pos[0] += target_vec * speed
            rect.centery = int(self.vec.y)
        for i in range(1, 5):
            tgt = self.pos[i-1]
            src = self.pos[i]
            src = src.lerp(tgt, 0.1)
            dst = tgt - src
            length = dst.length()  # Bad square root...
            if length > self.MAX_DIST:
                dst2 = pg.Vector2(dst)
                dst.scale_to_length(self.MAX_DIST)
                src += dst2 - dst
            elif length < self.MIN_DIST:
                dst2 = pg.Vector2(dst)
                dst.scale_to_length(self.MIN_DIST)
                src += dst2 - dst

            self.pos[i] = src
        return target_vec

    def draw(self, surface):
        rect = self.images[0].get_rect()
        for image, vec in zip(reversed(self.images), reversed(self.pos)):
            rect.center = vec_to_int(vec)
            surface.blit(image, rect)


class Context:
    def __init__(self, initial=None):
        initial = initial or {}
        for k, v in initial.items():
            setattr(self, k, v)


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pg.time.Clock()

        self.songs = SONGS[:]
        self.song_index = 0
        pg.mixer.music.set_endevent(END_MUSIC)
        pg.mixer.music.load(self.songs[self.song_index])
        pg.mixer.music.play()
        pg.display.set_caption("ÄH!")

        self.player = Player()

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

        self.high_scores = HIGH_SCORES
        self.load_highscores()

        self.state = None
        self.context = self.title_start(None)

    def load_highscores(self):
        highscore_file = os.path.join(os.path.expanduser('~'), 'Saved Games', 'AH Game', "highscore.json")
        if not os.path.isfile(highscore_file):
            self.save_highscores()
        with open(highscore_file, "rt") as f:
            self.high_scores = json.loads(f.read())


    def save_highscores(self):
        save_path = os.path.join(os.path.expanduser('~'), 'Saved Games', 'AH Game')
        save_file = os.path.join(save_path, "highscore.json")
        os.makedirs(save_path, exist_ok=True)
        with open(save_file, "wt+") as f:
            f.write(json.dumps(self.high_scores, indent=4))

    # Title screen
    def title_start(self, old_context):
        self.state = TITLE_SCREEN
        context = Context()
        context.done = False
        context.name, context.name_pos = ptext.draw("ÄH!", midtop=(SCREEN_WIDTH // 2, 20), color=AMBER, fontsize=150, surf=None)
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
        surface.blit(context.name, context.name_pos)
        ptext.draw(
            "CLICK MOUSE BUTTON\nTO BEGIN",
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            color=AMBER,
            fontsize=40,
        )
        ptext.draw(
            "You are the green worm trying to catch the appearing\n"
            + "bubbles by clicking towards them with your mouse.\n"
            + "The faster you click, the faster your worm moves.\n"
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
        initial_pos = (random.randint(90, 550), random.randint(70, 410))
        context.src_vec = pg.Vector2(initial_pos)
        context.player.set_pos(*initial_pos)
        context.score = 0
        context.bubbles = []
        context.next_bubble = random.randint(1500, 5000)
        context.time_remaining = 30000
        context.speed_factor = 0.98
        context.tgt_vec = pg.Vector2()
        context.speed = 0.0
        context.old_speed = 0.0
        context.dst_vec = pg.Vector2()
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
            # Spawn a new bubble
            # Make sure that new bubble doesn't overlap existing
            # bubbles and is not near vicinity of the player
            bubble_class = Bubble
            if random.randint(0, 10) == 0:
                bubble_class = Powerup
            accepted = False
            x, y = 0, 0
            while not accepted:
                accepted = True
                x = random.randint(50, 590)
                y = random.randint(50, 430)
                new_vec = pg.Vector2((x, y))
                # Check distance other bubbles
                for bubble in context.bubbles:
                    bubble_vec = pg.Vector2(bubble.rect.center)
                    if new_vec.distance_squared_to(bubble_vec) < 1600:
                        # Bubble too close to another bubble
                        accepted = False
                        break
                if new_vec.distance_squared_to(context.player.vec) < 3600:
                    accepted = False
            new_bubble = bubble_class((x, y), random.randint(1000, 7000))
            context.bubbles.append(new_bubble)
            SOUNDS["bubble"].play()

        context.src_vec += context.tgt_vec * context.speed
        context.tgt_vec = context.player.update(context.tgt_vec, context.speed)
        cur_vec = context.player.pos[0]
        dist_squared = context.dst_vec.distance_squared_to(cur_vec)
        if dist_squared <= 2:
            context.speed_factor = 0.9
        if context.speed > 0:
            context.speed *= context.speed_factor
            if context.speed < 0.06:
                context.speed = 0

        for bubble in context.bubbles[:]:
            if bubble.check_collision(context.player.rect):
                # Player hit the bubble
                bubble.play_sound()
                bubble.do_action(context)
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
            SOUNDS["player"].stop()
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
        context.player.draw(surface)
        #surface.blit(context.player, context.player_rect)

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
        context.is_high_score = context.score >= self.high_scores[-1][0]
        context.high_score_name = ""

        if not context.is_high_score:
            self.gameover_highscores(context)

        return context

    def gameover_highscores(self, context):
        txt = ""
        for score, name in self.high_scores:
            txt += f"{score:04}  {name}\n"
        tmp_img, _ = ptext.draw(
            txt, topleft=(0, 0), fontsize=18, color=AMBER, surf=None
        )

        size = tmp_img.get_size()
        size = (size[0], size[1] + 159)  # This needs to be one pixel less to avoid small glitch
        highscore_img = pg.Surface(size)
        rect = tmp_img.get_rect()
        context.highscore_height = rect.height
        highscore_img.blit(tmp_img, dest=rect)
        rect.y = rect.height
        rect.height = 159
        highscore_img.blit(tmp_img, dest=rect)
        context.highscore_img = highscore_img
        context.highscore_rect = pg.Rect((0, 0), (rect.width, HIGHSCORE_SCROLL_HEIGHT))
        context.highscore_top = 0

        # Highscore faders
        out_fader = pg.Surface((rect.width, 20), pg.SRCALPHA)
        for f in range(20, 0, -1):
            out_fader.fill((0, 0, 0, f * (255 / 20)), ((0, 20 - f), (rect.width, 1)))

        in_fader = pg.transform.flip(out_fader, False, True)

        context.out_fader = out_fader
        context.out_fader_rect = out_fader.get_rect()
        context.out_fader_rect.midtop = (SCREEN_WIDTH // 2, HIGHSCORE_SCROLL_TOP_Y)
        context.in_fader = in_fader
        context.in_fader_rect = in_fader.get_rect()
        context.in_fader_rect.midbottom = (SCREEN_WIDTH // 2, HIGHSCORE_SCROLL_TOP_Y + HIGHSCORE_SCROLL_HEIGHT)

    def gameover_event(self, context, event):
        if context.count < 50000 and event.type == pg.MOUSEBUTTONDOWN:
            context.count = 0
        if context.is_high_score and event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                context.high_score_name = context.high_score_name[:-1]
                return
            if event.key == pg.K_RETURN:
                self.high_scores.append((context.score, context.high_score_name))
                self.high_scores.sort(key=lambda x: x[0], reverse=True)
                self.high_scores = self.high_scores[:-1]
                context.is_high_score = False
                self.save_highscores()
                self.gameover_highscores(context)
                return
            if event.unicode.isalnum() and len(context.high_score_name) < 8:
                context.high_score_name += event.unicode.upper()

    def gameover_update(self, context, delta_time):
        context.count -= delta_time
        if not context.is_high_score:
            context.highscore_top += 0.5
            context.highscore_rect.top = int(context.highscore_top)
            if context.highscore_rect.top >= context.highscore_height:
                context.highscore_top = 0

        if context.count < context.end_jingle_start:
            context.end_jingle_start = -9999
            SOUNDS["end"].play()
        if context.count < context.end_jingle_stop:
            context.end_jingle_stop = -9999
            pg.mixer.music.load(GAME_OVER_SONG)
            pg.mixer.music.play()
            pg.mixer.music.set_endevent(END_MUSIC)

        if context.count <= 0:
            pg.mixer.music.fadeout(500)
            return self.title_start

    def gameover_draw(self, context, surface):
        ptext.draw(
            "GAME OVER",
            center=(SCREEN_WIDTH // 2, 60),
            color=AMBER,
            fontsize=60,
        )
        surf, pos = ptext.draw(
            f"SCORE: {context.score:05}", midtop=(SCREEN_WIDTH // 2, 150), fontsize=18, color=AMBER,
        )
        if context.is_high_score:
            ptext.draw("YOU MADE HIGH SCORE!\nENTER YOUR NAME BELOW:", midtop=(SCREEN_WIDTH // 2, 100), fontsize=18,
                       color=AMBER)
            rect = surf.get_rect(topleft=pos)
            rect.right += 10
            ptext.draw(
                f"{context.high_score_name}\u258E", topleft=rect.topright, fontsize=18, color=AMBER
            )
        else:
            surface.blit(context.highscore_img, dest=(SCREEN_WIDTH // 2 - context.highscore_rect.width // 2, HIGHSCORE_SCROLL_TOP_Y), area=context.highscore_rect)
            surface.blit(context.out_fader, dest=context.out_fader_rect)
            surface.blit(context.in_fader, dest=context.in_fader_rect)

        if context.count < 50000:
            ptext.draw("PRESS MOUSE BUTTON TO RESTART", midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 5), fontsize=18, color=AMBER)

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
    Game(screen=screen).game_loop()
