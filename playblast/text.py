import os
from typing import Iterator, Tuple

import blf
import bpy

from .metadata import get_metadata


class Rect:
    """Represents a rectangle

    In blender, the x,y is the bottom left corner
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def top_left(self) -> Tuple[int, int]:
        return self.x, self.y + self.height

    @property
    def top_center(self) -> Tuple[int, int]:
        return self.x + self.width // 2, self.y + self.height

    @property
    def top_right(self) -> Tuple[int, int]:
        return self.x + self.width, self.y + self.height

    @property
    def bottom_left(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def bottom_center(self) -> Tuple[int, int]:
        return self.x + self.width // 2, self.y

    @property
    def bottom_right(self) -> Tuple[int, int]:
        return self.x + self.width, self.y

    def scale(self, factor: float):
        self.x = int(self.x * factor)
        self.y = int(self.y * factor)
        self.width = int(self.width * factor)
        self.height = int(self.height * factor)

    def move(self, x: float, y: float):
        self.x += int(x)
        self.y += int(y)


class Text:
    """Represents a text to be drawn.

    Attributes:
        text: The text content
        position: The position of the text, one of these value:
            top_left, top_center, top_right,
            bottom_left, bottom_center, bottom_right.
        font_id: Loaded font id base on playblast setting.
        font_size: The font size base on full resolution on render setting.
        rect: The rect of the text base on full resolution on render setting.
    """

    def __init__(self, text: str, position: str):
        self.text = text
        self.position = position

        # Use playblast settings to calculate the text location to full resolution
        render = bpy.context.scene.render
        res_x = render.resolution_x
        res_y = render.resolution_y

        props = bpy.context.scene.playblast
        self.font_id = load_font(props.burn_in.font_family)
        self.font_size = props.burn_in.font_size
        self.font_color = props.burn_in.color
        margin = props.burn_in.margin

        # Calculate the font rect size
        blf.size(self.font_id, self.font_size)
        width, height = blf.dimensions(self.font_id, text)
        self.rect = Rect(0, 0, width, height)

        # Calculate the font rect position
        if position == "top_left":
            self.rect.x = margin
            self.rect.y = res_y - height - margin
        elif position == "top_center":
            self.rect.x = res_x // 2 - self.rect.width // 2
            self.rect.y = res_y - height - margin
        elif position == "top_right":
            self.rect.x = res_x - self.rect.width - margin
            self.rect.y = res_y - height - margin
        elif position == "bottom_left":
            self.rect.x = margin
            self.rect.y = margin
        elif position == "bottom_center":
            self.rect.x = res_x // 2 - self.rect.width // 2
            self.rect.y = margin
        elif position == "bottom_right":
            self.rect.x = res_x - self.rect.width - margin
            self.rect.y = margin
        else:
            raise ValueError(f"Invalid position: {position}")

    def scale(self, factor: float):
        self.rect.scale(factor)
        self.font_size = int(self.font_size * factor)

    def move(self, x: float, y: float):
        self.rect.move(x, y)


def get_bfont_path() -> str:
    """
    Since Blender's built-in font cannot be directly used in ffmpeg,
    I extracted it from the source code to a separate TTF file.
    For consistency, this plugin uses this font as the default.
    """

    path = os.path.join(os.path.dirname(__file__), "bfont.ttf")
    path = path.replace("\\", "/")
    return path


def load_font(path: str = None) -> int:
    """Load a font from a given path and return its font ID.

    If not specify, return default bfont.
    """

    if not path:
        # Use default BFont if no path is given
        path = get_bfont_path()

    font_id = blf.load(path)
    if font_id == -1:
        raise Exception(f"Failed to load font from {path}")
    return font_id


def iter_corner_text(metadata: dict = None) -> Iterator[Text]:
    context = bpy.context
    props = context.scene.playblast.burn_in

    if not metadata:
        metadata = get_metadata(context)

    for position, text_template in [
        ("top_left", props.top_left),
        ("top_center", props.top_center),
        ("top_right", props.top_right),
        ("bottom_left", props.bottom_left),
        ("bottom_center", props.bottom_center),
        ("bottom_right", props.bottom_right),
    ]:
        if not text_template.strip():
            # Skip if the text is empty
            continue

        text = text_template.format_map(metadata)
        text = Text(text, position)

        yield text
