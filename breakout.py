import random
from datetime import datetime, timedelta

import os
import time
import pygame
from pygame.rect import Rect

import config as c
from ball import Ball
from button import Button
from game import Game
from paddle import Paddle
from text_object import TextObject
import colors
import math

assert os.path.isfile('sound_effects/brick_hit.wav')


class Breakout(Game):
    def __init__(self):
        Game.__init__(self, 'Breakout', c.screen_width, c.screen_height, c.background_image, c.frame_rate)
        self.sound_effects = {name: pygame.mixer.Sound(sound) for name, sound in c.sounds_effects.items()}
        self.reset_effect = None
        self.effect_start_time = None
        self.start_level = False
        self.score_left = 0
        self.score_right = 0
        self.score_label_left = None
        self.score_label_right = None
        self.paddle_left = None
        self.paddle_right = None
        self.ball = None
        self.menu_buttons = []
        self.is_game_running = False
        self.create_objects()

    def create_objects(self):
        self.create_paddles()
        self.create_ball()
        self.create_labels()
        self.create_menu()

    def create_menu(self):
        def on_play(button):
            for b in self.menu_buttons:
                self.objects.remove(b)

            self.is_game_running = True
            self.start_level = True

        def on_quit(button):
            self.game_over = True
            self.is_game_running = False
            self.game_over = True

        for i, (text, click_handler) in enumerate((('PLAY', on_play), ('QUIT', on_quit))):
            b = Button(c.menu_offset_x,
                       c.menu_offset_y + (c.menu_button_h + 5) * i,
                       c.menu_button_w,
                       c.menu_button_h,
                       text,
                       click_handler,
                       padding=5)
            self.objects.append(b)
            self.menu_buttons.append(b)
            self.mouse_handlers.append(b.handle_mouse_event)

    def create_labels(self):
        self.score_label_left = TextObject(c.lives_left_offset_x,
                                           c.lives_left_offset_y,
                                           lambda: f'SCORE: {self.score_left}',
                                           c.text_color,
                                           c.font_name,
                                           c.font_size)
        self.objects.append(self.score_label_left)

        self.score_label_right = TextObject(c.lives_right_offset_x,
                                            c.lives_right_offset_y,
                                            lambda: f'SCORE: {self.score_right}',
                                            c.text_color,
                                            c.font_name,
                                            c.font_size)
        self.objects.append(self.score_label_right)

    def create_ball(self):
        # speed = (0, c.ball_speed)
        # self.ball = Ball(c.screen_width-c.ball_radius*2,
        #                  c.screen_height-c.ball_radius*2,
        #                  c.ball_radius,
        #                  c.ball_color,
        #                  speed)
        # spectrum = math.atan((c.screen_height / 2) / (c.screen_width / 2))
        # deg90 = 1.8 / math.pi * 1.5708
        # angle = random.triangular(-spectrum, spectrum)
        # vec_dir = (math.cos(deg90-angle)*c.ball_speed, math.sin(deg90+angle)*c.ball_speed)
        speed = (random.choice([-1, 1]) * c.ball_speed, c.ball_speed/2)
        self.ball = Ball(c.screen_width // 2,
                         c.screen_height // 2,
                         c.ball_radius,
                         c.ball_color,
                         speed)
        self.objects.append(self.ball)

    def create_paddles(self):
        paddle_left = Paddle(c.screen_width - c.paddle_width,
                             c.screen_height // 2,
                             c.paddle_width,
                             c.paddle_height,
                             c.paddle_color,
                             c.paddle_speed)
        self.keydown_handlers[pygame.K_UP].append(paddle_left.handle)
        self.keydown_handlers[pygame.K_DOWN].append(paddle_left.handle)
        self.keyup_handlers[pygame.K_UP].append(paddle_left.handle)
        self.keyup_handlers[pygame.K_DOWN].append(paddle_left.handle)
        self.paddle_left = paddle_left
        self.objects.append(self.paddle_left)

        paddle_right = Paddle(0,
                              c.screen_height // 2,
                              c.paddle_width,
                              c.paddle_height,
                              c.paddle_color,
                              c.paddle_speed)
        self.keydown_handlers[pygame.K_w].append(paddle_right.handle)
        self.keydown_handlers[pygame.K_s].append(paddle_right.handle)
        self.keyup_handlers[pygame.K_w].append(paddle_right.handle)
        self.keyup_handlers[pygame.K_s].append(paddle_right.handle)
        self.paddle_right = paddle_right
        self.objects.append(self.paddle_right)

    def handle_ball_collisions(self):
        def intersect(obj, ball):
            deep = 1
            edges = dict(left=Rect(obj.left-deep, obj.top, deep, obj.height),
                         right=Rect(obj.right, obj.top, deep, obj.height),
                         top=Rect(obj.left, obj.top+deep, obj.width, deep),
                         bottom=Rect(obj.left, obj.bottom, obj.width, deep))
            collisions = set(edge for edge, rect in edges.items() if ball.bounds.colliderect(rect))
            if not collisions:
                return None

            if len(collisions) == 1:
                return list(collisions)[0]

            if 'right' in collisions:
                if ball.centery >= obj.bottom:
                    return 'bottom'
                if ball.centery <= obj.top:
                    return 'top'
                return 'right'

            if 'left' in collisions:
                if ball.centery >= obj.bottom:
                    return 'bottom'
                if ball.centery <= obj.top:
                    return 'top'
                return 'left'

        def repulse(paddle, ball):
            s = ball.speed
            edge = intersect(paddle, ball)
            if edge is None:
                return
            self.sound_effects['paddle_hit'].play()
            if edge in ('left', 'right'):
                speed_x = -s[0]
                speed_y = s[1]
                if paddle.moving_up:
                    speed_y += (1 if s[0] < 0 else -1) * 0.2
                elif paddle.moving_down:
                    speed_y += (-1 if s[0] < 0 else 1) * 0.2
                speed_x += 1 / speed_x
                ball.speed = speed_x, speed_y
            else:  # top or bottom
                ball.speed = (s[0], -s[1])

        repulse(self.paddle_left, self.ball)
        repulse(self.paddle_right, self.ball)

        s = self.ball.speed
        # Hit floor and ceiling
        if self.ball.bottom > c.screen_height or self.ball.top < 0:
            self.ball.speed = (s[0], -s[1])

        # Hit wall
        if self.ball.left < 0 or self.ball.right > c.screen_width:
            if self.ball.left < 0:
                self.score_right += 1
            else:
                self.score_left += 1
            self.objects.remove(self.ball)
            del self.ball
            self.create_ball()

    def update(self):
        if not self.is_game_running:
            return

        if self.start_level:
            self.start_level = False
            self.show_message('GET READY!', centralized=True)

        # Reset special effect if needed
        if self.reset_effect:
            if datetime.now() - self.effect_start_time >= timedelta(seconds=c.effect_duration):
                self.reset_effect(self)
                self.reset_effect = None

        self.handle_ball_collisions()
        super().update()

        if self.game_over:
            self.show_message('GAME OVER!', centralized=True)

    def show_message(self, text, color=colors.WHITE, font_name='Arial', font_size=20, centralized=False):
        message = TextObject(c.screen_width // 2, c.screen_height // 2, lambda: text, color, font_name, font_size)
        self.draw()
        message.draw(self.surface, centralized)
        pygame.display.update()
        time.sleep(c.message_duration)


def main():
    Breakout().run()


if __name__ == '__main__':
    main()
