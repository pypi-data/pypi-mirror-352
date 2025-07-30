from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import NewType

from nextrpg.sprite import Sprite
from pygame import Surface

TimeDelta = NewType("TimeDelta", int)


@dataclass(frozen=True)
class Layer(ABC):
    sprites: list[Sprite]

    @abstractmethod
    def update(self, screen: Surface, time_delta: TimeDelta) -> None: ...
