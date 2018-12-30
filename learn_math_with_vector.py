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
robot = None
is_busy = False

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
    correct_answer = str(x + y)
    answer = json.loads(request.data.decode("utf-8"))
    if answer == correct_answer:
        msg = 'Correct!'
    else:
        msg = 'Wrong'
    create_image(msg)
    print(msg)
    robot.conn.run_soon(robot_display_img())
    robot.say_text(msg)
    return ''


def create_image(msg):
    global img
    W, H = (184,96)
    fnt = ImageFont.truetype('../static/fonts/Roboto-Bold.ttf', 48)
    img = Image.new("RGBA",(W,H),color = (0, 0, 0))
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(msg, font=fnt)
    draw.text(((W-w)/2,(H-h)/2-5), msg, font=fnt, fill=(0, 220, 135))
 

def create_sum():
    global x,y
    x = random.randint(1,10)
    y = random.randint(1,10)
    msg = str(x) + ' + ' + str(y)
    return msg

async def robot_display_img():
    global robot
    if robot != None:
        image_data = img.getdata()
        pixel_bytes = anki_vector.screen.convert_pixels_to_screen_data(image_data, 184, 96)
        await robot.screen.set_screen_with_image_data(pixel_bytes, 0.0, 1)
        await robot.screen.set_screen_with_image_data(pixel_bytes, 4.0, 1)
        time.sleep(5)


def run():
    global robot

    # thread = Thread(target=flask_socket_helpers.run_flask, args=(None, app))
    # thread.start()

    _sum = create_sum()
    create_image(_sum)

    with anki_vector.robot.Robot() as robot:
        robot.behavior.set_head_angle(degrees(45.0))
        robot.behavior.set_lift_height(0.0)
        robot.conn.run_coroutine(robot_display_img())

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