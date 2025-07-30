from pathlib import Path
from typing import override

from nextrpg.character import Character
from nextrpg.character_layer import CharacterLayer
from nextrpg.layer import TimeDelta
from nextrpg.scene import Scene
from pygame.event import Event
from pygame.surface import Surface
from pytmx import TiledImageLayer, TiledTileLayer, load_pygame


class MapScene(Scene):
    def __init__(self, player_character: Character, tmx_map: Path) -> None:
        super().__init__([CharacterLayer(player_character)])
        self.player_character = player_character
        self.tmx_map = tmx_map

    @override
    def on_event(self, event: Event) -> None:
        pass

    @override
    def update(self, screen: Surface, time_delta: TimeDelta) -> None:
        tmx_map = load_pygame(self.tmx_map)
        for layer in tmx_map.visible_layers:
            if isinstance(layer, TiledImageLayer):
                screen.blit(layer.image, (0, 0))
                continue

            if isinstance(layer, TiledTileLayer):
                for x, y, tile in layer.tiles():
                    screen.blit(tile, (x * tmx_map.tilewidth, y * tmx_map.tileheight))

        CharacterLayer(self.player_character).update(screen, time_delta)
