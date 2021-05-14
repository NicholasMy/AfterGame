from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import json
import bisect

config_filename = "data.json"

app = Flask(__name__)
socket = SocketIO(app)

config = None  # This will be updated in main and always hold the current config


# Update the config file on disk to reflect the current `config` dictionary
def writeConfig():
    global config_filename
    if config is not None:
        with open(config_filename, "w") as f:
            json.dump(config, f, indent=4, sort_keys=True)


# Update `config` to hold the dictionary from a config json file
def readConfig(filename: str):
    global config
    with open(filename) as f:
        config = json.load(f)


def add_selectable_option(category: str, new_option: str):
    print("Add selectable option {}, {}".format(category, new_option))
    # Look up which options list this should be inserted into
    options_name = config["selectables"][category]["options"]
    # Insert this element alphabetically with bisect
    bisect.insort(config["selectable_options"][options_name], new_option)
    # Write the update to file
    writeConfig()


# Save a barcode preset. The barcode might be "12345678" and the preset will be a json string with all the options of this preset.
def add_preset(barcode: str, preset: str):
    print("Add preset {}, {}".format(barcode, preset))
    parsed_preset = json.loads(preset)
    config["presets"][barcode] = parsed_preset
    writeConfig()


# Set the value for one of the selectables. A selectable might be "game" while the option could be "Burnout Paradise"
def set_selectable(selectable: str, option: str):
    print("Set selectable {}, {}".format(selectable, option))
    config["selectables"][selectable]["value"] = option
    # TODO probably broadcast this to all clients
    writeConfig()


@app.route('/')
def index():
    return render_template("index.html", data={"config": config})


@socket.on("message")
def handle_message(message):
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
    readConfig(config_filename)
    # add_preset("1234", '{"game": "some preset game", "platform": "some preset platform"}')
    socket.run(app, port=8080)
