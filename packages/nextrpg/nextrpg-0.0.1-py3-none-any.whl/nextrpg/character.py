from enum import Enum

from nextrpg.sprite import Coordinate, Sprite
from pygame import Surface


class Direction(Enum):
    DOWN = 0
    LEFT = 1
    RIGHT = 2
    UP = 3


class Character:
    def __init__(
        self,
        sprite_sheet: Surface,
        initial_coordinate: Coordinate,
        initial_direction: Direction = Direction.DOWN,
        speed: int = 5,
        animate_on_idle: bool = False,
    ) -> None:
        self.animate_on_idle = animate_on_idle
        self._sprites = {direction: _cut_sprite_sheet(sprite_sheet, direction) for direction in Direction}
        self._coordinate = initial_coordinate
        self._direction = initial_direction
        self._speed = speed
        self._current_frame = _FrameType.IDLE
        self._last_frame = _FrameType.RIGHT_FOOT

    @property
    def current_sprite(self) -> Sprite:
        return Sprite(self._sprites[self._direction][self._current_frame], self._coordinate)

    def step(self, direction: Direction) -> None:
        pass

    def step_frame(self) -> None:
        last_frame = self._current_frame
        match self._current_frame:
            case _FrameType.RIGHT_FOOT:
                self._current_frame = _FrameType.IDLE
            case _FrameType.LEFT_FOOT:
                self._current_frame = _FrameType.IDLE
            case _FrameType.IDLE:
                if self._last_frame is _FrameType.RIGHT_FOOT:
                    self._current_frame = _FrameType.LEFT_FOOT
                else:
                    self._current_frame = _FrameType.RIGHT_FOOT
        self._last_frame = last_frame


class _FrameType(Enum):
    RIGHT_FOOT = 0
    IDLE = 1
    LEFT_FOOT = 2


def _cut_sprite_sheet(sprite_sheet: Surface, direction: Direction) -> dict[_FrameType, Surface]:
    width = sprite_sheet.get_width() // len(_FrameType)
    height = sprite_sheet.get_height() // len(Direction)
    return {
        frame_type: sprite_sheet.subsurface(frame_type.value * width, direction.value * height, width, height)
        for frame_type in _FrameType
    }
