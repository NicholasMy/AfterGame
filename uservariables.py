# This is the file where you can define custom functions for variables in your output name.
# Don't modify the vars dict or the var function.
from UservarInput import UservarInput
from datetime import datetime

vars: dict = {}


def var(var_name: str):
    def wrapper(func):
        vars[var_name] = func

    return wrapper

# To make a custom variable, create a function that accepts an instance of UservarInput and returns a string.
# Add the @var decorator with a string that the variable will replace.
# When a selectable has its value set to that exact string, it will call the function
# and use its return value to replace the variable in the output file name.
# The output will still have the selectable's prefix and suffix applied to it.
# AfterGame must be restarted for changes here to take effect.
# See the UservarInput class for information about what data is accessible.

@var("[Sample Variable]")
def sample_variable(uservar: UservarInput) -> str:
    return "var " + uservar.selectable + "/"


@var("[OBS File Name]")
def obs_filename(uservar: UservarInput) -> str:
    return uservar.original_path.filename


# Given a file name like "2021-06-06 14.49.39 Video NVENC 1440p.mp4", return "2021-06-06 14.49.39"
@var("[OBS Date & Time]")
def obs_date_time(uservar: UservarInput) -> str:
    return " ".join(uservar.original_path.filename.split(" ")[:2])


# Intelligently determine the best folder to put this video in
@var("[Smart Directory]")
def smart_directory(uservar: UservarInput) -> str:
    player1: str = uservar.config["selectables"]["player1"]["value"]
    player2: str = uservar.config["selectables"]["player2"]["value"]
    player3: str = uservar.config["selectables"]["player3"]["value"]
    player4: str = uservar.config["selectables"]["player4"]["value"]

    if not player1:
        return "No Players Specified"

    # For single player, put the files in the player's personal folder
    if not player2 and not player3 and not player4:
        return player1

    else:
        return "Multiplayer"

@var("[time]")
def time(uservar: UservarInput) -> str:
    return "{} {}".format(datetime.now().date(), datetime.now().time()).replace(":", "-")
