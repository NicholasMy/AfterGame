from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json
import threading
import util
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

config_filename = "data.json"

app = Flask(__name__)
socket = SocketIO(app)

config = None  # This will be updated in main and always hold the current config
fileLock = threading.Lock()


# Update the config file on disk to reflect the current `config` dictionary
# Also sends updated config to all clients
def write_config():
    global config_filename
    if config is not None:
        fileLock.acquire()  # For safe multithreaded access
        emit("message", config, json=True, broadcast=True, include_self=True)
        with open(config_filename, "w") as f:
            json.dump(config, f, indent=2)
        fileLock.release()


# Update `config` to hold the dictionary from a config json file
def read_config(filename: str):
    global config
    with open(filename) as f:
        config = json.load(f)


# Send a banner message to the client that resulted in this method being called
# Mostly used to show errors
def send_toast(message, style):
    d = {"message": message, "style": style}
    emit("toast", d, json=True)


# Set the value for one of the selectables. A selectable might be "game" while the option could be "Burnout Paradise"
def set_selectable_option(selectable: str, option: str):
    print("Set selectable {}, {}".format(selectable, option))
    config["selectables"][selectable]["value"] = option


# Update the currently selected item for a selectable category
def add_selectable_option(category: str, new_option: str, update_current_selection=True):
    print("Add selectable option {}, {}".format(category, new_option))
    if new_option == "":
        send_toast('You cannot add an empty string as an option.', "error")
        return
    # Look up which options list this should be inserted into
    options_name = config["selectables"][category]["options"]
    if new_option in config["selectable_options"][options_name]:
        # This already exists, so don't add a duplicate.
        send_toast('"{}" already exists, so a duplicate was not added.'.format(new_option), "error")
    else:
        # This is new, so add it to the options
        # Insert this element alphabetically ignoring case with modified bisect
        util.insort_right(config["selectable_options"][options_name], new_option)
        send_toast('Added "{}".'.format(new_option), "success")
    if update_current_selection:
        set_selectable_option(category, new_option)


# Save a barcode preset. The barcode might be "12345678" and the preset will be a dictionary with all the options of this preset.
def add_preset(barcode: str, preset: dict):
    print("Add preset {}, {}".format(barcode, preset))
    if barcode == "":
        send_toast('You cannot create a preset with an empty barcode.', "error")
    else:
        exists = barcode in config["presets"]
        config["presets"][barcode] = preset
        if exists:
            send_toast('Updated preset "{}".'.format(barcode), "success")
        else:
            send_toast('Created preset "{}".'.format(barcode), "success")


# Update all relevant selectables to their value from a preset
def load_preset(barcode: str):
    print("Load preset {}".format(barcode))
    this_preset = config["presets"].get(barcode, None)
    if this_preset is None:
        # Invalid preset
        send_toast('Unknown preset "{}".'.format(barcode), "error")
    else:
        # Valid preset
        for selectable, value in this_preset.items():
            print(selectable, value)
            config["selectables"][selectable]["value"] = value
        send_toast('Loaded preset "{}".'.format(barcode), "success")


def add_bulk_game(title: str, platform: str, barcodes: list):
    print("Add bulk game", title, platform, barcodes)

    if not (title and platform):
        send_toast('Presets require a title and platform.', "error")
        return

    barcodes.remove("")  # Remove empty strings
    options_name = config["selectables"]["game"]["options"]
    gameExists = title in config["selectable_options"][options_name]
    if not gameExists:
        # Create the game
        add_selectable_option("game", title, update_current_selection=False)
    for barcode in barcodes:
        preset = {"game": title, "platform": platform}
        add_preset(barcode, preset)
    if not gameExists:
        send_toast('Created game "{}" and {} associated preset(s).'.format(title, len(barcodes)), "success")
    else:
        send_toast('The game "{}" already existed. Created/updated {} associated preset(s) for it.'.format(title, len(
            barcodes)), "success")


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
        add_preset(data["barcode"], json.loads(data["preset"]))
    elif action == "load_preset":
        load_preset(data["barcode"])
    elif action == "add_bulk_game":
        add_bulk_game(data["title"], data["platform"], data["barcodes"])

    # Any time the user sends something through the socket, we need to update the config
    write_config()


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


def get_new_filename(original_filename: str) -> str:
    return "todo"
    # TODO implement: generate a new file name from current config values given the original OBS output name


# Renames a file on disk
def rename_file(original_file: str, new_filename: str):
    print("Renaming {} to {}".format(original_file, new_filename))
    # TODO implement


# Runs when a new video file is detected
def new_video_detected(filename: str):
    print("New video file! {}".format(filename))
    # TODO implement some logic here, probalby rename and store the original somewhere


class FileChangeHandler(FileSystemEventHandler):
    # def on_any_event(self, event):
    #     print(self, event)

    def on_modified(self, event):
        print("New remuxed recording ", event)
        path = event.src_path  # C:/OBS\test.mp4
        parent_dir, filename_with_ext = os.path.split(path)  # C:/OBS, test.mp4
        filename, ext = os.path.splitext(filename_with_ext)  # test, .mp4
        print(path, parent_dir, filename_with_ext, filename, ext)
        # TODO determine if this is a video we care about, call new_video_detected if so



if __name__ == '__main__':
    # Load the config from disk
    read_config(config_filename)
    # TODO upon starting, anything not in "selectable_order" should have its value emptied

    # Start the file observer to detect new remuxed recordings ready to rename
    watch_dir = config["recording_settings"]["directory_to_watch"]
    observer = Observer()
    observer.schedule(FileChangeHandler(), watch_dir)
    observer.start()

    # Finally, run dev server
    socket.run(app, debug=True, host="0.0.0.0", port=8080)
