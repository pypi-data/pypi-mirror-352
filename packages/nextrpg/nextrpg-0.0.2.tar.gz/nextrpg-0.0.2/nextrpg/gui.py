from dataclasses import dataclass


@dataclass(frozen=True)
class GUI:
    """
    Graphical User Interface / window for the game.

    Attributes:
        title (str): The title of the GUI window.
        default_width (int): The default width of the GUI window on startup.
        default_height (int): The default height of the GUI window on startup.
        resizable (bool): Whether the GUI window is resizable.
        max_frames_per_second (int): The maximum number of frames per second the GUI will update.
    """
    title: str
    width: int = 1280
    height: int = 800
    resizable: bool = True
    frames_per_second: int = 60
