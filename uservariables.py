# This is the file where you can define custom functions for variables in your output name.
# Don't modify the vars dict or the var function.
from CustomPath import CustomPath

vars: dict = {}


def var(var_name: str):
    def wrapper(func):
        vars[var_name] = func

    return wrapper


# To create a custom variable, create a function that accepts the original file name as a CustomPath,
# the AfterGame config, and the selectable name, and returns a string to replace the variable with.
# Add the @var decorator with a string that the variable will replace.
# When a selectable has its value set to that exact string, it will call the function
# and use its output to replace the variable in the output file name.
# The output will still have the selectable's prefix and suffix applied to it.
# AfterGame must be restarted for changes here to take effect

@var("[Sample Variable]")
def sample_variable(original_filename: CustomPath, config: dict, selectable: str) -> str:
    return "var " + selectable + "/"


@var("[OBS File Name]")
def obs_filename(original_filename: CustomPath, config: dict, selectable: str) -> str:
    return original_filename.filename


# Given a file name like "2021-06-06 14.49.39 Video NVENC 1440p.mp4", return "2021-06-06 14.49.39"
@var("[OBS Date & Time]")
def obs_date_time(original_filename: CustomPath, config: dict, selectable: str) -> str:
    return " ".join(original_filename.filename.split(" ")[:2])


# Intelligently determine the best folder to put this video in
@var("[Smart Directory]")
def smart_directory(original_filename: CustomPath, config: dict, selectable: str) -> str:

    game = config["selectables"]["game"]["value"]

    if config["selectables"]["player1"]["value"] == "Nicholas":
        if game != "":
            game = "/" + game
        if config["selectables"]["player2"]["value"] == "":
            return "Nicholas" + game
        else:
            return "Multiplayer" + game

    return "" + game
