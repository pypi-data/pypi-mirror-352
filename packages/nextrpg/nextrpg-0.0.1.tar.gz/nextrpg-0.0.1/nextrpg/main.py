import pygame
from nextrpg.gui import GUI
from nextrpg.scene import Scene, TimeDelta
from pygame import display
from pygame.locals import QUIT, RESIZABLE
from pygame.time import Clock


def start_game(gui: GUI, entry_scene: Scene) -> None:
    """
    Entry function for the game.
    """
    pygame.init()
    display.set_caption(gui.title)
    surface = display.set_mode((gui.width, gui.height), RESIZABLE if gui.resizable else 0)
    clock = Clock()
    scene = entry_scene
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return quit()
            scene.on_event(event)
        scene.update(surface, TimeDelta(clock.get_time()))
        display.update()
        clock.tick(gui.frames_per_second)
