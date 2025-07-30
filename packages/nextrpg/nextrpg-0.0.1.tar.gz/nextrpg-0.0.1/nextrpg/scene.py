from abc import ABC, abstractmethod
from dataclasses import dataclass

from nextrpg.layer import Layer, TimeDelta
from pygame.event import Event
from pygame.surface import Surface


@dataclass(frozen=True)
class Scene(ABC):
    layers: list[Layer]

    @abstractmethod
    def on_event(self, event: Event) -> None: ...

    def update(self, screen: Surface, time_delta: TimeDelta) -> None:
        for layer in self.layers:
            layer.update(screen, time_delta)
