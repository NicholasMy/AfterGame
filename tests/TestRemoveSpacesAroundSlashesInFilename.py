import unittest
from app import remove_spaces_around_slashes_in_filename


class Test(unittest.TestCase):

    # Ensure no changes are made when they don't need to be
    def test_no_spaces(self):
        filename = "C:/apple/banana/carrot"
        new_filename = remove_spaces_around_slashes_in_filename(filename)
        self.assertEqual(filename, new_filename, "no changes")

    def test_small_strings(self):
        strings = ["hello / world", "hello \\ world", "hello/ world", "hello\\ world", "hello /world", "hello \\world"]
        for s in strings:
            output = remove_spaces_around_slashes_in_filename(s)
            print(output)
            self.assertFalse(" " in output)  # Make sure there's no space in the output

    def test_multiple_spaces(self):
        strings = ["hello  / world", "hello  \\ world", "hello / world", "hello \\ world", "hello  /world",
                   "hello  \\world",
                   "hello /  world", "hello \\  world", "hello/  world", "hello\\  world", "hello / world",
                   "hello \\ world"]
        for s in strings:
            output = remove_spaces_around_slashes_in_filename(s)
            print(output)
            self.assertFalse(" " in output)  # Make sure there's no space in the output

    def test_no_change(self):
        strings = ["hello world", "hello  world", "hello   world", "this has a couple words in it",
                   "there are no slashes here", "this has a slash in the correct location/", "/this does too",
                   "\\and backslash", "and backslash at the end\\", "and/slashes/throughout but no/spaces touching a/",
                   "other\\slashes are\\cool too", "\\starting and ending with slashes\\",
                   "/having/multiple/slashes/throughout/", "only/slashes/in/middle"]
        for actual in strings:
            expected = remove_spaces_around_slashes_in_filename(actual)
            self.assertEqual(actual, expected)

    def test_realistic_filenames(self):
        # Input -> Expected
        pairs = {
            "C:\\my video / some/game": "C:\\my video/some/game",
            "C:/games /xbox 360/Forza Motorsport 99 \\this game.mp4": "C:/games/xbox 360/Forza Motorsport 99\\this game.mp4",
            "C:/games / xbox 360/ Forza Motorsport 99 \\ this game.mp4": "C:/games/xbox 360/Forza Motorsport 99\\this game.mp4",
            "C: / games / xbox 360 / Forza Motorsport 99 \\ this game.mp4": "C:/games/xbox 360/Forza Motorsport 99\\this game.mp4",
            "C:    /    games  /      xbox 360  /  Forza Motorsport 99 \\    this game.mp4": "C:/games/xbox 360/Forza Motorsport 99\\this game.mp4",
            "/mnt/drive/games/Forza Motorsport 99/this game.mp4": "/mnt/drive/games/Forza Motorsport 99/this game.mp4",
            "/mnt/ drive/ games/ Forza Motorsport 99/ this game.mp4": "/mnt/drive/games/Forza Motorsport 99/this game.mp4",
            " / mnt / drive/ games /  Forza Motorsport 99/     this game.mp4": "/mnt/drive/games/Forza Motorsport 99/this game.mp4",
            " / mnt/ drive  / games / Forza Motorsport 99/  this game.mp4": "/mnt/drive/games/Forza Motorsport 99/this game.mp4",
            " /mnt / drive/ games/ Forza Motorsport 99 / this game.mp4": "/mnt/drive/games/Forza Motorsport 99/this game.mp4"
        }

        for input, expected in pairs.items():
            output = remove_spaces_around_slashes_in_filename(input)
            self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()
