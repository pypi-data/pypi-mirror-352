from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from pygame import Surface
from pygame.image import load


class SpriteSheetSelection(NamedTuple):
    """
    A selection from a large sprite sheet.
    Both row and column are 0-indexed. e.g.

           col0 col1 col2 col3
    row0
    row1
    """

    row: int
    column: int


def load_sprite_sheet(
    path: Path, selection: SpriteSheetSelection | None = None
) -> Surface:
    ROW_LENGTH = 4
    COLUMN_LENGTH = 2
    image = load(path)
    if selection:
        width = image.get_width() // ROW_LENGTH
        height = image.get_height() // COLUMN_LENGTH
        return image.subsurface(
            selection.row * width, selection.column * height, width, height
        )
    return image


class Coordinate(NamedTuple):
    horizontal: int
    vertical: int


@dataclass
class Sprite:
    image: Surface
    coordinate: Coordinate
