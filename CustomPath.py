import os


# An easy way to get required parts of a file path
# Takes an absolute path, allows accessing some useful fields
class CustomPath:
    def __init__(self, path: str):
        self.path = path  # C:/OBS\test.mp4
        self.parent_dir, self.filename_with_ext = os.path.split(self.path)  # C:/OBS, test.mp4
        self.filename, self.ext = os.path.splitext(self.filename_with_ext)  # test, .mp4
