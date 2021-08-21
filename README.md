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
(TODO)

## Understanding the config
(TODO)

## Using custom variables
(TODO)

