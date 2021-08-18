import CustomPath


# Contains all the data passed into uservar functions for easy expandability
# original_path is the CustomPath of the original OBS output file (this might not exist on the filesystem anymore)
# current_path is the CustomPath of where the file is currently saved on the filesystem
# config is the global AfterGame configuration dictionary
# selectable is the name of the selectable that this variable is being used for (i.e. this selectable's value equals this variable name)
class UservarInput:
    def __init__(self, original_path: CustomPath, current_path: CustomPath, config: dict, selectable: str):
        self.original_path = original_path
        self.current_path = current_path
        self.config = config
        self.selectable = selectable
