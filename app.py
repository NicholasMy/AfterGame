from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json
import bisect
import threading

config_filename = "data.json"

app = Flask(__name__)
socket = SocketIO(app)

config = None  # This will be updated in main and always hold the current config
fileLock = threading.Lock()


# Update the config file on disk to reflect the current `config` dictionary
# Also sends updated config to all clients
def writeConfig():
    global config_filename
    if config is not None:
        fileLock.acquire()  # For safe multithreaded access
        emit("message", config, json=True, broadcast=True, include_self=True)
        with open(config_filename, "w") as f:
            json.dump(config, f, indent=2)
        fileLock.release()


# Update `config` to hold the dictionary from a config json file
def readConfig(filename: str):
    global config
    with open(filename) as f:
        config = json.load(f)


# Set the value for one of the selectables. A selectable might be "game" while the option could be "Burnout Paradise"
def set_selectable_option(selectable: str, option: str):
    print("Set selectable {}, {}".format(selectable, option))
    config["selectables"][selectable]["value"] = option


# Update the currently selected item for a selectable category
def add_selectable_option(category: str, new_option: str):
    print("Add selectable option {}, {}".format(category, new_option))
    # Look up which options list this should be inserted into
    options_name = config["selectables"][category]["options"]
    # Insert this element alphabetically with bisect
    # TODO ignore case for insertion location
    bisect.insort(config["selectable_options"][options_name], new_option)
    # Write the update to file
    set_selectable_option(category, new_option)


# Save a barcode preset. The barcode might be "12345678" and the preset will be a json string with all the options of this preset.
def add_preset(barcode: str, preset: str):
    print("Add preset {}, {}".format(barcode, preset))
    parsed_preset = json.loads(preset)
    config["presets"][barcode] = parsed_preset


# Update all relevant selectables to their value from a preset
def load_preset(barcode: str):
    print("Load preset {}".format(barcode))
    this_preset = config["presets"].get(barcode, None)
    if this_preset is None:
        # Invalid preset
        return False
    for selectable, value in this_preset.items():
        print(selectable, value)
        config["selectables"][selectable]["value"] = value
    return True


@app.route('/')
def index():
    return render_template("index.html", data={"config": config})


@socket.on("message")
def handle_message(data):
    print("Got message from client: {}".format(data))
    action = data["action"]
    if action == "add_selectable":
        add_selectable_option(data["selectable_type"], data["value"])
    elif action == "set_selectable":
        set_selectable_option(data["selectable_type"], data["value"])
    elif action == "add_preset":
        add_preset(data["barcode"], data["preset"])
    elif action == "load_preset":
        load_preset(data["barcode"])

    # Any time the user sends something through the socket, we need to update the config
    writeConfig()


@socket.on("connect")
def handle_connect():
    print("Client connected")
    emit("message", config, json=True)


@socket.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@app.route('/static/<path:filename>')
def send_static_file(filename):
    return send_from_directory('static_files', filename)


if __name__ == '__main__':
    readConfig(config_filename)
    # TODO upon starting, anything not in "selectable_order" should have its value emptied
    # add_preset("1234", '{"game": "some preset game", "platform": "some preset platform"}')
    socket.run(app, host="0.0.0.0", port=8080)
