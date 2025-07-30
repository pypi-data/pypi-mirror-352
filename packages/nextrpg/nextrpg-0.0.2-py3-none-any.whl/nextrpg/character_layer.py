from typing import override

from nextrpg.character import Character
from nextrpg.layer import Layer, TimeDelta
from pygame import Surface


class CharacterLayer(Layer):
    def __init__(self, character: Character, idle_animation_speed: TimeDelta = TimeDelta(500)) -> None:
        super().__init__([character.current_sprite])
        self._character = character
        self._idle_animation_speed = idle_animation_speed
        self._time_elapsed_on_current_frame = TimeDelta(0)

    @override
    def update(self, screen: Surface, time_delta: TimeDelta) -> None:
        self._time_elapsed_on_current_frame = TimeDelta(self._time_elapsed_on_current_frame + time_delta)
        if self._time_elapsed_on_current_frame > self._idle_animation_speed:
            self._character.step_frame()
            self._time_elapsed_on_current_frame = TimeDelta(0)
        sprite = self._character.current_sprite
        screen.blit(sprite.image, sprite.coordinate)
