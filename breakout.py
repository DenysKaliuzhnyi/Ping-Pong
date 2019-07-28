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

assert os.path.isfile('sound_effects/brick_hit.wav')


class Breakout(Game):
    def __init__(self):
        Game.__init__(self, 'Breakout', c.screen_width, c.screen_height, c.background_image, c.frame_rate)
        self.sound_effects = {name: pygame.mixer.Sound(sound) for name, sound in c.sounds_effects.items()}
        self.reset_effect = None
        self.effect_start_time = None
        self.score = 0
        self.lives = c.initial_lives
        self.start_level = False
        self.paddle1 = None
        self.paddle2 = None
        self.ball = None
        self.menu_buttons = []
        self.is_game_running = False
        self.create_objects()
        self.points_per_brick = 1

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
        self.score_label = TextObject(c.score_offset,
                                      c.status_offset_y,
                                      lambda: f'SCORE: {self.score}',
                                      c.text_color,
                                      c.font_name,
                                      c.font_size)
        self.objects.append(self.score_label)
        self.lives_label = TextObject(c.lives_offset,
                                      c.status_offset_y,
                                      lambda: f'LIVES: {self.lives}',
                                      c.text_color,
                                      c.font_name,
                                      c.font_size)
        self.objects.append(self.lives_label)

    def create_ball(self):
        # speed = (0, c.ball_speed)
        # self.ball = Ball(c.screen_width-c.ball_radius*2,
        #                  c.screen_height-c.ball_radius*2,
        #                  c.ball_radius,
        #                  c.ball_color,
        #                  speed)
        speed = (random.choice([-1, 1]) * random.randint(4, 4), c.ball_speed)
        self.ball = Ball(c.screen_width // 2,
                         c.screen_height // 2,
                         c.ball_radius,
                         c.ball_color,
                         speed)
        self.objects.append(self.ball)

    def create_paddles(self):
        paddle1 = Paddle(c.screen_width - c.paddle_width,
                         c.screen_height // 2,
                         c.paddle_width,
                         c.paddle_height,
                         c.paddle_color,
                         c.paddle_speed)
        self.keydown_handlers[pygame.K_UP].append(paddle1.handle)
        self.keydown_handlers[pygame.K_DOWN].append(paddle1.handle)
        self.keyup_handlers[pygame.K_UP].append(paddle1.handle)
        self.keyup_handlers[pygame.K_DOWN].append(paddle1.handle)
        self.paddle1 = paddle1
        self.objects.append(self.paddle1)

        paddle2 = Paddle(0,
                         c.screen_height // 2,
                         c.paddle_width,
                         c.paddle_height,
                         c.paddle_color,
                         c.paddle_speed)
        self.keydown_handlers[pygame.K_w].append(paddle2.handle)
        self.keydown_handlers[pygame.K_s].append(paddle2.handle)
        self.keyup_handlers[pygame.K_w].append(paddle2.handle)
        self.keyup_handlers[pygame.K_s].append(paddle2.handle)
        self.paddle2 = paddle2
        self.objects.append(self.paddle2)

    def handle_ball_collisions(self):
        def intersect(obj, ball):
            deep = 3
            edges = dict(left=Rect(obj.left-deep, obj.top, deep, obj.height),
                         right=Rect(obj.right, obj.top, deep, obj.height),
                         top=Rect(obj.left, obj.top+deep, obj.width, deep),
                         bottom=Rect(obj.left, obj.bottom, obj.width, deep))
            collisions = set(edge for edge, rect in edges.items() if ball.bounds.colliderect(rect))
            if not collisions:
                return None

            if len(collisions) == 1:
                return list(collisions)[0]

            if 'top' in collisions:
                if ball.centery >= obj.top:
                    return 'top'
                if ball.centerx < obj.left:
                    return 'left'
                else:
                    return 'right'

            if 'bottom' in collisions:
                if ball.centery >= obj.bottom:
                    return 'bottom'
                if ball.centerx < obj.left:
                    return 'left'
                else:
                    return 'right'

        def repulse(paddle, ball):
            s = ball.speed
            edge = intersect(paddle, self.ball)
            if edge is None:
                return
            self.sound_effects['paddle_hit'].play()
            if edge in ('left', 'right'):
                speed_x = -s[0]
                speed_y = s[1]
                if paddle.moving_up:
                    speed_x -= 1
                elif paddle.moving_down:
                    speed_x += 1
                ball.speed = speed_x, speed_y
            elif edge == 'top':
                if s[1] >= 0:
                    ball.speed = (s[0], -s[1])
                    paddle.ignore = "up"
            elif edge == 'bottom':
                if s[1] <= 0:
                    ball.speed = (s[0], -s[1])
                    paddle.ignore = "down"

        repulse(self.paddle1, self.ball)
        repulse(self.paddle2, self.ball)

        s = self.ball.speed
        # Hit floor
        if self.ball.bottom > c.screen_height:
            self.ball.speed = (s[0], -s[1])

        # Hit ceiling
        if self.ball.top < 0:
            self.ball.speed = (s[0], -s[1])

        # Hit wall
        if self.ball.left < 0 or self.ball.right > c.screen_width:
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
