from typing import override

from nextrpg.layer import Layer, TimeDelta
from nextrpg.sprite import Coordinate, Sprite
from pygame import Surface


class StaticImageLayer(Layer):
    def __init__(self, image: Surface, coordinate: Coordinate = Coordinate(0, 0)) -> None:
        self.sprite = Sprite(image, coordinate)
        super().__init__([Sprite(image, coordinate)])

    @override
    def update(self, screen: Surface, time_delta: TimeDelta) -> None:
        screen.blit(self.sprite.image, self.sprite.coordinate)
