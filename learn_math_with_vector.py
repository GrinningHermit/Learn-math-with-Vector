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
_sum = ''
robot = None
is_busy = False
questions = 3
current_question = 0

@app.route('/')
def index():
    global x, y
    return render_template(
        'index.html',
        sum_x = str(x),
        sum_y = str(y)
    )


@app.route('/answer', methods=['POST'])
def answer_eval():
    global is_busy
    global _sum
    global current_question
    correct_answer = str(x + y)
    answer = json.loads(request.data.decode("utf-8"))
    if answer == correct_answer:
        msg = 'Correct!'
        color = (0, 220, 135)
        _sum = create_sum()
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
    ask_question(msg)
    return ''


@app.route('/again', methods=['POST'])
def again():
    global current_question
    current_question = 0
    ask_question(create_sum())
    return ''


def ask_question(msg):
    global is_busy

    is_busy = False
    time.sleep(0.4)

    if current_question >= questions:
        robot.anim.play_animation('anim_eyecontact_giggle_01_head_angle_20')
        robot.conn.release_control()
        # sys.exit()
        return ''

    create_image(_sum, (255,255,255))
    robot.conn.run_soon(robot_display_img())
    robot.say_text(_sum)


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
 

def create_sum():
    global x,y
    x = random.randint(1,10)
    y = random.randint(1,10)
    msg = str(x) + ' + ' + str(y)
    return msg

async def robot_display_img():
    global robot
    global is_busy
    if robot != None:
        is_busy = True
        image_data = img.getdata()
        pixel_bytes = anki_vector.screen.convert_pixels_to_screen_data(image_data, 184, 96)
        await robot.screen.set_screen_with_image_data(pixel_bytes, 0.0, 1)
        while is_busy:
            await robot.screen.set_screen_with_image_data(pixel_bytes, 0.1, 1)


def run():
    global robot
    global _sum

    # thread = Thread(target=flask_socket_helpers.run_flask, args=(None, app))
    # thread.start()

    _sum = create_sum()
    create_image(_sum, (255,255,255))

    with anki_vector.robot.Robot() as robot:
        robot.say_text("I love math, let's play!")
        robot.behavior.set_head_angle(degrees(45.0))
        robot.behavior.set_lift_height(0.0)
        robot.conn.run_coroutine(robot_display_img())
        robot.say_text(_sum)

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