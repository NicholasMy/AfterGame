from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import json

app = Flask(__name__)
socket = SocketIO(app)

# TODO save this in a file
config = {
    "directory_to_watch": r"C:\OBS",
    "selectable_options": {
        "games": [
            "Burnout Paradise",
            "Forza Motorsport 4",
            "Smash Bros"
        ],
        "platforms": [
            "Xbox 360",
            "Wii",
            "Switch"
        ],
        "players": [
            "Nicholas",
            "Other player",
        ],
    },

    "selectable_order": ["game", "platform"],

    "selectables": {
        "game": {
            "friendly_name": "Game",
            "empty_text": "No Game",
            "value": "Forza Motorsport 4",
            "options": "games"
        },
        "platform": {
            "friendly_name": "Platform",
            "empty_text": "No Platform",
            "value": "Xbox 360",
            "options": "platforms"
        },
    },

    "presets": {
        "somebarcode1": {
            "game": "Burnout Paradise",
            "platform": "Xbox 360",
        },
        "somebarcode2": {
            "game": "Some game without a platform specified",
        }
    },
}


def add_selectable_option(category, new_option):
    print("Add selectable option {}, {}".format(category, new_option))


def add_preset(barcode, preset):
    print("Add preset {}, {}".format(barcode, preset))


def set_selectable(selectable, option):
    print("Set selectable {}, {}".format(selectable, option))


@app.route('/')
def index():
    return render_template("index.html", data={"config": config})


@socket.on("message")
def handle_json(message):
    data = json.loads(message)
    print("Got message from client: {}".format(data))


@socket.on("connect")
def handle_connect():
    print("Client connected")


@socket.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@app.route('/static/<path:filename>')
def send_static_file(filename):
    return send_from_directory('static_files', filename)


if __name__ == '__main__':
    socket.run(app)
