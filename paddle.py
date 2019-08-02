import pygame

import config as c
from game_object import GameObject


class Paddle(GameObject):
    def __init__(self, x, y, w, h, color, offset):
        GameObject.__init__(self, x, y, w, h)
        self.color = color
        self.offset = offset
        self.moving_up = False
        self.moving_down = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.bounds)

    def handle(self, key):
        if key == pygame.K_UP or key == pygame.K_w:
            self.moving_up = not self.moving_up
        else:
            self.moving_down = not self.moving_down

    def update(self):
        if self.moving_up:
            dy = -(min(self.offset, self.top))
        elif self.moving_down:
            dy = min(self.offset, c.screen_height - self.bottom)
        else:
            return
        self.speed = [0, dy]
        super().update()
