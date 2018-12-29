import anki_vector
import random
import time
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
    msg = 'triggered'
    if answer == correct_answer:
        msg = 'Yay, correct!'
    else:
        msg = 'No, wrong'
    create_image(msg)
    print(msg)
    robot_display_img()


def create_image(msg):
    global img
    W, H = (184,96)
    fnt = ImageFont.truetype('/Library/Fonts/Hind-Bold.ttf', 48)
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

def robot_display_img():
    global robot
    if robot != None:
        image_data = img.getdata()
        pixel_bytes = anki_vector.screen.convert_pixels_to_screen_data(image_data, 184, 96)
        robot.conn.release_control()
        time.sleep(1)
        robot.conn.request_control()
        robot.screen.set_screen_with_image_data(pixel_bytes, 4.0)
        time.sleep(5)


def robot_connect_prepare():
    global robot
    with anki_vector.robot.Robot() as robot:
        robot.behavior.set_head_angle(degrees(45.0))
        robot.behavior.set_lift_height(0.0)
        robot_display_img()


def run():
    global robot

    _sum = create_sum()
    create_image(_sum)

    thread = Thread(target=flask_socket_helpers.run_flask, args=(None, app))
    thread.start()

    robot_connect_prepare()

    while True:
        pass


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