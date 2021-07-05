from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json
import threading
import util
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from CustomPath import CustomPath
import uservariables
import time

CONFIG_FILENAME = "data.json"

app = Flask(__name__)
socket = SocketIO(app, async_mode="threading")  # async_mode needed for background thread emissions

CONFIG = None  # This will be updated in main and always hold the current config
CONFIG_FILE_LOCK = threading.Lock()
MODIFY_CONFIG_LOCK = threading.Lock()


# Update the config file on disk to reflect the current `CONFIG` dictionary
# Also sends updated config to all clients
def write_config():
    global CONFIG_FILENAME
    if CONFIG is not None:
        CONFIG_FILE_LOCK.acquire()  # For safe multithreaded access
        # Special thanks to https://stackoverflow.com/a/30125944 for helping me emit without request context
        SocketIO.emit(socket, "message", CONFIG, json=True, broadcast=True, include_self=True)
        with open(CONFIG_FILENAME, "w") as f:
            json.dump(CONFIG, f, indent=2)
        CONFIG_FILE_LOCK.release()


# Update `CONFIG` to hold the dictionary from a config json file
def read_config(filename: str):
    global CONFIG
    with open(filename) as f:
        CONFIG = json.load(f)


# Send a banner message to the client that resulted in this method being called
# Mostly used to show errors
def send_toast(message: str, style: str):
    d = {"message": message, "style": style}
    emit("toast", d, json=True)


# Set the value for one of the selectables. A selectable might be "game" while the option could be "Burnout Paradise"
def set_selectable_option(selectable: str, option: str):
    print("Set selectable {}, {}".format(selectable, option))
    CONFIG["selectables"][selectable]["value"] = option


# Update the currently selected item for a selectable category
def add_selectable_option(category: str, new_option: str, update_current_selection=True):
    print("Add selectable option {}, {}".format(category, new_option))
    if new_option == "":
        send_toast('You cannot add an empty string as an option.', "error")
        return
    # Look up which options list this should be inserted into
    options_name = CONFIG["selectables"][category]["options"]
    if new_option in CONFIG["selectable_options"][options_name]:
        # This already exists, so don't add a duplicate.
        send_toast('"{}" already exists, so a duplicate was not added.'.format(new_option), "error")
    else:
        # This is new, so add it to the options
        # Insert this element alphabetically ignoring case with modified bisect
        util.insort_right(CONFIG["selectable_options"][options_name], new_option)
        send_toast('Added "{}".'.format(new_option), "success")
    if update_current_selection:
        set_selectable_option(category, new_option)


# Remove a selectable option
def delete_selectable_option(category: str, option: str):
    print("Delete selectable option {}, {}".format(category, option))
    # Look up which options list this should be removed from
    options_name = CONFIG["selectables"][category]["options"]
    if option in CONFIG["selectable_options"][options_name]:
        CONFIG["selectable_options"][options_name].remove(option)
        send_toast('Deleted "{}".'.format(option), "success")
    else:
        send_toast('"{}" didn\'t exist, so it couldn\'t be deleted.'.format(option), "error")


# Save a barcode preset. The barcode might be "12345678" and the preset will be a dictionary with all the options of this preset.
def add_preset(barcode: str, preset: dict):
    print("Add preset {}, {}".format(barcode, preset))
    if barcode == "":
        send_toast('You cannot create a preset with an empty barcode.', "error")
    else:
        exists = barcode in CONFIG["presets"]
        CONFIG["presets"][barcode] = preset
        if exists:
            send_toast('Updated preset "{}".'.format(barcode), "success")
        else:
            send_toast('Created preset "{}".'.format(barcode), "success")


# Update all relevant selectables to their value from a preset
def load_preset(barcode: str):
    print("Load preset {}".format(barcode))
    this_preset = CONFIG["presets"].get(barcode, None)
    # TODO Fuzzy barcode search, try without leading/trailing character and with prepended and appended zero
    if this_preset is None:
        # Invalid preset
        send_toast('Unknown preset "{}".'.format(barcode), "error")
    else:
        # Valid preset
        for selectable, value in this_preset.items():
            CONFIG["selectables"][selectable]["value"] = value
        send_toast('Loaded preset "{}".'.format(barcode), "success")


def add_bulk_game(title: str, platform: str, barcodes: list):
    print("Add bulk game", title, platform, barcodes)

    if not (title and platform):
        send_toast('Presets require a title and platform.', "error")
        return

    barcodes.remove("")  # Remove empty strings
    options_name = CONFIG["selectables"]["game"]["options"]
    gameExists = title in CONFIG["selectable_options"][options_name]
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


# Given a path to a recording, update it to the current config settings
def update_old_recording(current_path: str):
    print("Update old recording: {}".format(current_path))
    # When the user clicks the update button, the server gets the current path of the video to update
    # 1. Find the map containing that current path with linear search, now we have the original file name
    target_recording = None
    target_index = 0  # Track the index for efficient removal
    for recording in CONFIG["recent_recordings"]:
        if recording["current_path"] == current_path:
            target_recording = recording
            break
        target_index += 1

    # If recording not found
    if not target_recording:
        send_toast('Recording not found in data file: {}'.format(current_path), "error")
        return

    # 2. Rename the file to its original name
    rename_success = rename_file(target_recording["current_path"], target_recording["original_path"])
    if not rename_success:
        send_toast('Error renaming old recording: {}'.format(current_path), "error")
        return

    # 3. Delete this entry from recent recordings
    CONFIG["recent_recordings"].pop(target_index)
    send_toast('Updated old recording: {}'.format(current_path), "success")

    # 4. Since it was renamed to the original file name, the file observer will automatically capture it as
    # a new video and rename it properly, no need to do that manually.
    # TODO this might not work if the file is moved to the same directory, maybe need to manually call new_video_detected


@app.route('/')
def index():
    return render_template("index.html", data={"config": CONFIG})


@socket.on("message")
def handle_message(data: dict):
    MODIFY_CONFIG_LOCK.acquire()
    print("Got message from client: {}".format(data))
    action = data["action"]
    if action == "add_selectable":
        add_selectable_option(data["selectable_type"], data["value"])
    elif action == "delete_selectable":
        delete_selectable_option(data["selectable_type"], data["value"])
    elif action == "set_selectable":
        set_selectable_option(data["selectable_type"], data["value"])
    elif action == "add_preset":
        add_preset(data["barcode"], json.loads(data["preset"]))
    elif action == "load_preset":
        load_preset(data["barcode"])
    elif action == "add_bulk_game":
        add_bulk_game(data["title"], data["platform"], data["barcodes"])
    elif action == "update_old_recording":
        update_old_recording(data["path"])

    # Any time the user sends something through the socket, we need to update the config
    write_config()
    MODIFY_CONFIG_LOCK.release()


@socket.on("connect")
def handle_connect():
    emit("message", CONFIG, json=True)


@socket.on("disconnect")
def handle_disconnect():
    pass


@app.route('/static/<path:filename>')
def send_static_file(filename):
    return send_from_directory('static_files', filename)


# Given a file name/path, prevent a space from existing next to a slash
def remove_spaces_around_slashes_in_filename(filename: str):
    need_to_fix: list = ["/ ", " /", "\\ ", " \\"]
    new_filename = filename
    for fix in need_to_fix:
        while fix in new_filename:
            correct_slash = fix.replace(" ", "")
            new_filename = new_filename.replace(fix, correct_slash)
    return new_filename


# Given an OBS output filename, return the new filename with the correct metadata
# Handles replacing user variables
def get_new_filename(original_file: CustomPath) -> str:
    user_vars: dict = uservariables.vars
    parts: list = []  # List of strings to concatenate
    for selectable_name in CONFIG["selectable_order"]:
        selectable = CONFIG["selectables"][selectable_name]
        prefix = selectable["prefix"]
        value = selectable["value"]
        suffix = selectable["suffix"]
        if value:
            if value in user_vars:
                # This is a user variable, so replace its value with the output from the var func
                func = user_vars[value]
                try:
                    value = func(original_file, CONFIG, selectable_name)
                except Exception:
                    # If the uservar raises an exception, don't crash the thread
                    value = "(Error on uservar {})".format(value)
            # Add the prefix and suffix to this value; add that whole string to the parts list
            parts.append("{}{}{}".format(prefix, value, suffix))
    new_filename = " ".join(parts)
    # Build the new file path
    leading_path = original_file.parent_dir
    ext = original_file.ext
    # Combine the parent dir, the new name, and the extension
    new_file_path = os.path.join(leading_path, new_filename) + ext
    # Remove spaces around slashes
    new_file_path = remove_spaces_around_slashes_in_filename(new_file_path)
    # Formalize the path format to match the OS
    final_new_path = CustomPath(new_file_path)
    return final_new_path.path


# Renames a file on disk, absolute paths are best
# Return true on successful rename, false otherwise
def rename_file(original_file: str, new_filename: str) -> bool:
    # Only rename if the original file exists and the new file doesn't exist
    if os.path.isfile(original_file) and not os.path.isfile(new_filename):
        # Make the parent directories if necessary
        new_file = CustomPath(new_filename)
        try:  # OS might error
            os.makedirs(new_file.parent_dir, exist_ok=True)
            print("Renaming {} to {}".format(original_file, new_filename))
            os.rename(original_file, new_filename)
        except Exception as e:
            print("Error renaming {} to {}: {}".format(original_file, new_filename, e))
            return False  # OS Error
        return True  # Successful rename
    else:
        return False  # Either the original file didn't exist or the new file already existed


# Runs when a new video file is detected, can also be used to update a previous video with the current selectables
def new_video_detected(file: CustomPath):
    print("New video file! {}".format(file))
    new_filename = get_new_filename(file)
    rename_success = rename_file(file.path, new_filename)
    if rename_success:
        # Create a recent recordings entry
        entry = {
            "original_path": file.path,
            "current_path": new_filename
        }
        # Add it to the front of the recent recordings list
        CONFIG["recent_recordings"].insert(0, entry)
        # If recent recordings is longer than number_of_recordings_to_show, truncate to the correct length
        max_recordings = CONFIG["recording_settings"]["number_of_recordings_to_show"]
        if len(CONFIG["recent_recordings"]) > max_recordings:
            del CONFIG["recent_recordings"][max_recordings:]
        write_config()
    else:  # Rename failed
        print("RENAME FAILED, no entry made {}".format(file.path))


# Check if a given file is a video file we want to rename based on the "file_extensions" in the config
def is_video(file: CustomPath) -> bool:
    return file.ext in CONFIG["recording_settings"]["file_extensions"]


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return  # We don't care about a directory update

        global MODIFY_CONFIG_LOCK
        with MODIFY_CONFIG_LOCK:  # Make sure this is thread-safe
            file = CustomPath(event.src_path)  # C:/OBS/test.mp4
            if is_video(file):
                new_video_detected(file)


if __name__ == '__main__':
    # Load the config from disk
    read_config(CONFIG_FILENAME)
    # TODO upon starting, anything not in "selectable_order" should have its value emptied

    # Start the file observer to detect new remuxed recordings ready to rename
    watch_dir = CONFIG["recording_settings"]["directory_to_watch"]
    observer = Observer()
    observer.schedule(FileChangeHandler(), watch_dir)
    observer.start()

    # Finally, run dev server
    # Enabling debug mode breaks the file observer because it launches two processes
    socket.run(app, debug=False, host="0.0.0.0", port=8080)
