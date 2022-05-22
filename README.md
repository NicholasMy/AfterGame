# Welcome to AfterGame!
###### A highly customizable file renaming assistant to organize video game recordings

## Features
* Automatically rename outputs from OBS and similar software to organize your recordings
* Supports multiple directory layers and automatically creates directories when necessary
* Has a modern, responsive, minimalistic, and easy to use web front end
* Create custom categories of "selectables" with prefixes, suffixes, and user-friendly text hints
* Add and remove "selectable options" related to each "selectable" via the front end or manual configuration editing
* Scroll through all selectable options in alphabetical order, and use the partial search box to narrow down results
* Multiple "selectables" can be linked to the same list of options (useful when player1 and player2 will come from the same list of possible players)
* Retroactively update previous recordings according to the current selectables
* All settings and data can be manually modified in `data.json`
* Use infinitely customizable variables in your output names via Python functions in `uservariables.py`
* Create and load presets with a barcode scanner
* Quickly add your whole game library and associated presets with the "Bulk Game Adder"
* Presets are partial - they only update fields that are explicitly defined within them. If you only want a preset to adjust the game and the platform,
it won't update or clear your other fields.

Although AfterGame was designed with video games in mind, it can be configured for any type of use. The only caveat is the "Bulk Game Adder" won't work. 
It can otherwise be expanded to work with any file extension by updating `file_extensions` in the config.

## Getting started
It's really easy to get started! Clone the repo, specify the source location of your recordings on your host in `docker-compose.yml`; the line has a comment about this. Finally, run `docker-compose up -d` to start the server. It'll run on port 8080 by default, but you can change this in `docker-compose.yml`.

## Understanding the config
The configuration file (`data.json`) is admittedly a little complicated. I'll break down the most important parts here.

### Recording settings, presets, and recent recordings
The `recording_settings` is straightforward; you can set the directory to watch (there's no need to change this if you're using Docker), which file extensions to pay attention to, and how many previous recordings to keep track of for retroactive renames.

The `presets` and `recent_recordings` sections are automatically generated, so there's rarely any need to manually modify these.

### Selectables
The `selectables` section is the most complicated. This is where you define all possible categories to choose from for generating the file name.

```json
"selectables": {
    "game": {
      "empty_text": "No Game",
      "friendly_name": "Game",
      "prefix": "",
      "suffix": "",
      "add_text": "New Game",
      "options": "games",
      "value": "My Game"
    }, ...
```

Each selectable is a dictionary where the key is the selectable's name and the value is a dictionary containing information about it.

* `empty_text`, `friendly_name`, and `add_text` are only shown on the front-end for user-friendliness and don't affect the output at all.
* `prefix` and `suffix` are automatically prepended and appended to the value if a value is selected. It will behave as if these were part of the value.
* `options` specifies which set of options this selectable chooses from (explained below). Multiple selectables may use the same list of options.
* `value` stores the current value of this selectable.


### Selectable options
The `selectable_options` section is used to specify all possible values for a selectable. It may look like this:
```json
"selectable_options": {
  "platforms": [
      "Gamecube",
      "PC",
      "PlayStation 2",
      "Wii",
      "Switch"
    ], ...
```

These **MUST** be sorted alphabetically, otherwise options added through the front-end may not remain alphabetical.

### Selectable Order
Finally, the order of selectables must be specified in `selectable_order`. This may look like:
```json
  "selectable_order": [
    "directory",
    "game",
    "platform",
    "player1",
    "player2"
  ]
```

Each entry must be the key of one of the selectables. This determines the order on the front-end, and therefore, the order in the output file name.

## Using custom variables
For unlimited customization, you can define your own variables in `uservariables.py`.

 To make a custom variable, create a function that accepts an instance of `UservarInput` and returns a string. Add the `@var` decorator with a string that the variable will replace. When a selectable has its value set to that exact string, it will call the function and use its return value to replace the variable in the output file name. The output will still have the selectable's prefix and suffix applied to it. AfterGame must be restarted for changes here to take effect. See the UservarInput class for information about what data is accessible.

For example, to get part of the original file name, you could write this:
```python
# Given a file name like "2021-06-06 14.49.39 Video NVENC 1440p.mp4", return "2021-06-06 14.49.39"
@var("[OBS Date & Time]")
def obs_date_time(uservar: UservarInput) -> str:
    return " ".join(uservar.original_path.filename.split(" ")[:2])
```

When any selectable's value is "[OBS Date & Time]", it will be replaced with the output of this function.

If an exception is raised when evaluating a custom variable, it will be evaluated to "(Uservar Error)" and the error will be printed to the console, but it will continue as usual.