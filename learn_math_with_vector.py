import anki_vector
import random
import time
import asyncio
import logging
import sys
import json
from threading import Thread
from lib import flask_socket_helpers
from anki_vector.util import degrees
from PIL import Image, ImageDraw, ImageFont

try:
    from flask import Flask, render_template, request
except ImportError:
    sys.exit("Cannot import from flask: Do `pip3 install --user flask` to install")

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    logging.warning("Cannot import from PIL: Do `pip3 install --user Pillow` to install")


app = Flask(__name__)
msg = ''
x = 0
y = 0
math_string = ''
robot = None
is_busy = False
questions = 10
current_question = 0
game_type = ''
game_range = 0


@app.route('/')
def index():
    global x, y
    return render_template(
        'index.html'
    )


@app.route('/answer', methods=['POST'])
def answer_eval():
    global is_busy
    global math_string
    global current_question
    global game_type

    if game_type == '+':
        correct_answer = str(x + y)
    elif game_type == '-':
        correct_answer = str(x - y)
    elif game_type == '*':
        correct_answer = str(x * y)

    answer = json.loads(request.data.decode("utf-8"))
    if answer == correct_answer:
        msg = 'Correct!'
        color = (0, 220, 135)
        math_string = create_math_calculation()
        current_question = current_question + 1
    else:
        msg = 'Wrong'
        color = (180, 0, 0)
    create_image(msg, color)
    print(msg)
    is_busy = False
    time.sleep(0.4) # make sure any displayed image is removed
    robot.conn.run_soon(robot_display_img())
    robot.say_text(msg)
    time.sleep(1.5)
    if current_question >= questions:
        is_busy = False
        current_question = 0
        robot_action('finished')
        return 'done'
    else: 
        ask_question(msg)
        return ''


@app.route('/game_start', methods=['POST'])
def game_start():
    global robot
    global math_string
    global game_type
    global game_range

    msg = json.loads(request.data.decode("utf-8"))
    game_type = msg['type']
    game_range = msg['range']
    math_string = create_math_calculation()
    ask_question(math_string)
    return game_type


@app.route('/again', methods=['POST'])
def again():
    global current_question
    current_question = 0
    ask_question(create_math_calculation())
    return ''


def robot_finished():
    print('finished animation triggered')
    play_list = [
        'anim_vc_alrighty_01',
        'anim_eyecontact_giggle_01_head_angle_20',
        'anim_timer_emote_01',
        'anim_referencing_giggle_01',
        'anim_referencing_smile_01'
    ]
    play = play_list[random.randint(0, len(play_list) - 1)]
    print(play)
    robot.anim.play_animation(play)
    time.sleep(3)
    robot.behavior.set_head_angle(degrees(45.0))
    robot.behavior.set_lift_height(0.0)


def robot_started():
    print('started animation triggered')
    robot.say_text("I love math, let's play!")
    robot.behavior.set_head_angle(degrees(45.0))
    robot.behavior.set_lift_height(0.0)


def robot_action(action):
    global robot
    if action == 'finished':
        thread = Thread(target=robot_finished)
    if action == 'started':
        thread = Thread(target=robot_started)
    thread.start()


def ask_question(msg):
    global is_busy

    is_busy = False
    time.sleep(0.4)
    create_image(math_string, (255,255,255))
    robot.conn.run_soon(robot_display_img())
    if game_type == '-':
        msg = str(x) + ' minus ' + str(y)
    else:
        msg = str(x) + ' ' + game_type + ' ' + str(y)
    robot.say_text(msg)


def create_image(msg, color=(0, 220, 135)):
    global img
    global questions
    global current_question

    progress = str(current_question) + '/' + str(questions)
    W, H = (184,96)
    fnt1 = ImageFont.truetype('../static/fonts/Roboto-Bold.ttf', 48)
    fnt2 = ImageFont.truetype('../static/fonts/Roboto-Bold.ttf', 18)
    img = Image.new("RGBA",(W,H),color = (0, 0, 0))
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(msg, font=fnt1)
    draw.text(((W-w)/2,(H-h)/2-5), msg, font=fnt1, fill=(color))
    draw.text((5,5), progress, font=fnt2, fill=(255,255,255))
 

def create_math_calculation():
    global x,y
    global game_type
    global game_range

    if game_type == '+':
        x = random.randint(0, game_range)
        y_range = game_range - x
    elif game_type == '-':
        x = random.randint(1,int(game_range*1.5))
        if x > game_range:
            x = x - int(game_range/2)
        y_range = x
    elif game_type == '*':
        x = random.randint(1, game_range)
        y_range = random.randint(1, game_range)
    y = random.randint(0, y_range)

    msg = str(x) + ' ' + game_type + ' ' + str(y)
    return msg

async def robot_display_img():
    global robot
    global is_busy
    if robot != None:
        is_busy = True
        image_data = img.getdata()
        pixel_bytes = anki_vector.screen.convert_pixels_to_screen_data(image_data, 184, 96)
        robot.screen.set_screen_to_color(anki_vector.color.off, duration_sec=0.0)
        while is_busy:
            await robot.screen.set_screen_with_image_data(pixel_bytes, 0.1)


def run():
    global robot

    with anki_vector.robot.Robot() as robot:
        robot_action('started')
        flask_socket_helpers.run_flask(None, app)


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt as e:
        sys.exit("Program aborted: %s" % e)
    except anki_vector.exceptions.VectorNotFoundException as e:
        # Test server mode without active Vector
        print('test mode')
        flask_socket_helpers.run_flask(None, app)
    except anki_vector.exceptions.VectorConnectionException as e:
        sys.exit("A connection error occurred: %s" % e)