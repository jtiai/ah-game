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

bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

TITLE_SCREEN = 1
GAME = 2
GAME_OVER = 3
GAME_COUNTDOWN = 4

BLACK = (0, 0, 0)
AMBER = (255, 191, 0)
GREEN = (51, 255, 0)

FONT_NAME = os.path.join(bundle_dir, "RussoOne-Regular.ttf")

ptext.DEFAULT_FONT_NAME = FONT_NAME


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


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pg.time.Clock()

        self.state = TITLE_SCREEN
        self.player = pg.Surface((25, 25))
        self.player.fill(GREEN)
        self.player_rect = self.player.get_rect()
        self.src_vec = pg.Vector2(self.player_rect.center)
        self.dst_vec = None
        self.tgt_vec = None
        self.speed = 0

        pg.display.set_caption("ÄH!")

    def title_screen(self):
        in_title_screen = True
        while in_title_screen:
            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                if event.type == pg.MOUSEBUTTONUP:
                    in_title_screen = False

            self.screen.fill(BLACK)
            ptext.draw("ÄH!", midtop=(SCREEN_WIDTH // 2, 20), color=AMBER, fontsize=40)
            ptext.draw("CLICK MOUSE BUTTON\nTO BEGIN", center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), color=AMBER, fontsize=40)
            ptext.draw(
                "You are the green box trying to catch the appearing\n" +
                "bubbles by clicking towards them with your mouse.\n" +
                "The faster you click, the faster your player moves.\n" +
                "Be quick, you have 30 seconds...", midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 5), color=AMBER,
                fontsize=18, align="left"
            )
            pg.display.flip()

    def game_loop(self):
        score = 0
        bubbles = []
        next_bubble = random.randint(1500, 5000)

        game_remaining = 30000
        count_down = 4000
        while True:
            delta_time = self.clock.tick(FPS)
            self.screen.fill(BLACK)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    sys.exit()

                if self.state == GAME:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        # Move player towards clicked place
                        self.dst_vec = pg.Vector2(event.pos)
                        self.tgt_vec = self.dst_vec - self.src_vec
                        self.tgt_vec.normalize_ip()
                        if self.speed <= 5.0:
                            self.speed += 0.8

            if self.state == TITLE_SCREEN:
                self.title_screen()
                self.state = GAME_COUNTDOWN

            if self.state == GAME_COUNTDOWN:
                count = count_down // 1000
                count = f"{count}" if count else "GO!"
                ptext.draw(count, center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), color=AMBER, fontsize=40)
                count_down -= delta_time
                if count_down < 0:
                    count_down = 4000
                    self.state = GAME
                    self.player_rect.centerx = random.randint(70, 570)
                    self.player_rect.centery = random.randint(50, 430)
                    self.src_vec.xy = self.player_rect.center
                    score = 0
                    bubbles = []
                    next_bubble = random.randint(1500, 5000)
                    game_remaining = 30000

            if self.state == GAME_OVER:
                count_down -= delta_time
                if count_down <= 0:
                    self.state = TITLE_SCREEN
                    continue
                ptext.draw("GAME OVER", center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), color=AMBER, fontsize=60)
                ptext.draw(f"SCORE: {score:05}", topleft=(5, 5), fontsize=18, color=AMBER)

            if self.state == GAME:
                game_remaining -= delta_time
                if game_remaining <= 0:
                    self.state = GAME_OVER
                    bubbles = []
                    count_down = 10000
                    continue

                next_bubble -= delta_time
                if next_bubble <= 0:
                    next_bubble = random.randint(500, 2000)
                    x = random.randint(50, 590)
                    y = random.randint(50, 430)
                    new_bubble = Bubble((x, y), random.randint(1000, 7000))
                    bubbles.append(new_bubble)

                if self.tgt_vec:
                    self.src_vec += self.tgt_vec * self.speed
                    self.player_rect.centerx = int(self.src_vec.x)
                    self.player_rect.centery = int(self.src_vec.y)
                    cur_vec = pg.Vector2(self.player_rect.center)
                    dist = self.dst_vec.distance_squared_to(cur_vec)
                    if dist <= 2:
                        self.tgt_vec = None
                        self.speed = 0
                    if self.speed > 0:
                        self.speed *= 0.95
                        if self.speed < 0.05:
                            self.speed = 0
                            self.tgt_vec = None

                for bubble in bubbles[:]:
                    if bubble.check_collision(self.player_rect):
                        # Player hit the bubble
                        score += bubble.get_points()
                        bubbles.remove(bubble)
                        continue
                    if not bubble.update(delta_time):
                        # Bubble died:
                        bubbles.remove(bubble)
                        continue
                    bubble.draw(self.screen)

                # Speed debugging
                # ptext.draw(f"{self.speed:.02f}", topright=(SCREEN_WIDTH-5, 5), fontsize=18, color=AMBER)
                ptext.draw(f"SCORE: {score:05}", topleft=(5, 5), fontsize=18, color=AMBER)
                ptext.draw(f"TIME LEFT: {game_remaining // 1000}", topright=(SCREEN_WIDTH - 5, 5), fontsize=18, color=AMBER)
                self.screen.blit(self.player, self.player_rect)

            pg.display.flip()


if __name__ == "__main__":
    Game().game_loop()
