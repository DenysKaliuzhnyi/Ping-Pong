import colors

screen_width = 800
screen_height = 600
background_image = 'images/background.jpg'

frame_rate = 90

ball_speed = 4
ball_radius = 8
ball_color = colors.GREEN

paddle_width = 20
paddle_height = 80
paddle_color = colors.ALICEBLUE
paddle_speed = 6

text_color = colors.YELLOW1
font_name = 'Arial'
font_size = 20

lives_left_offset_x = 10
lives_left_offset_y = 10
lives_right_offset_x = screen_width - 105
lives_right_offset_y = 10

effect_duration = 20

sounds_effects = dict(
    brick_hit='sound_effects/brick_hit.wav',
    effect_done='sound_effects/effect_done.wav',
    paddle_hit='sound_effects/paddle_hit.wav',
    level_complete='sound_effects/level_complete.wav',
)

message_duration = 2

button_text_color = colors.WHITE,
button_normal_back_color = colors.INDIANRED1
button_hover_back_color = colors.INDIANRED2
button_pressed_back_color = colors.INDIANRED3

menu_offset_x = 20
menu_offset_y = 300
menu_button_w = 80
menu_button_h = 50
