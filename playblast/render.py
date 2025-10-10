import time
from typing import Tuple

import blf
import bpy
import gpu
from bpy_extras.view3d_utils import location_3d_to_region_2d


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


def poll(context: bpy.types.Context) -> bool:
    """Check if the current context is valid for drawing burn-in text"""
    return (
        context.area is not None
        and context.area.type == "VIEW_3D"
        and context.space_data is not None
        and context.space_data.region_3d is not None
        and context.space_data.region_3d.view_perspective == "CAMERA"
        and context.scene is not None
        and context.scene.camera is not None
    )


def get_camera_frame_rect(context: bpy.types.Context) -> Rect:
    """Get the rectangle of the camera frame in 3d viewport"""

    region = context.region
    rv3d = context.space_data.region_3d
    cam = context.scene.camera
    if cam is None:
        raise Exception("No camera found in the scene")

    # Get the camera frame corners in world space
    frame_corners = cam.data.view_frame(scene=context.scene)
    frame_corners_world = [cam.matrix_world @ corner for corner in frame_corners]

    # Convert the world space corners to 2D screen space
    frame_corners_2d = []
    for corner in frame_corners_world:
        corner_2d = location_3d_to_region_2d(region, rv3d, corner)
        frame_corners_2d.append(corner_2d)

    x = min(corner[0] for corner in frame_corners_2d)
    y = min(corner[1] for corner in frame_corners_2d)
    width = max(corner[0] for corner in frame_corners_2d) - x
    height = max(corner[1] for corner in frame_corners_2d) - y

    return Rect(x, y, width, height)


def get_text_location(
    draw_rect: Rect, text_rect: Rect, margin: int, position: str
) -> Tuple[int, int]:
    """Get the location to draw text based on the specified position and margin

    Arguments:
        draw_rect: The rectangle to draw, usually the camera frame rect
        text_rect: The rectangle of the text to draw
        margin: The margin from the edges of the draw_rect
        position: The position to draw the text,
            one of "top_left", "top_center", "top_right", "bottom_left", "bottom_center", "bottom_right"

    Returns:
        (x, y): The bottom left corner of the text to draw
    """

    if position == "top_left":
        x, y = draw_rect.top_left
        return x + margin, y - text_rect.height - margin
    elif position == "top_center":
        x, y = draw_rect.top_center
        return x - text_rect.width // 2, y - text_rect.height - margin
    elif position == "top_right":
        x, y = draw_rect.top_right
        return x - text_rect.width - margin, y - text_rect.height - margin
    elif position == "bottom_left":
        x, y = draw_rect.bottom_left
        return x + margin, y + margin
    elif position == "bottom_center":
        x, y = draw_rect.bottom_center
        return x - text_rect.width // 2, y + margin
    elif position == "bottom_right":
        x, y = draw_rect.bottom_right
        return x - text_rect.width - margin, y + margin
    else:
        raise ValueError(f"Invalid position: {position}")


def load_font(path) -> int:
    """Load a font from a given path and return its font ID."""

    if not path:
        return 0  # Default font

    font_id = blf.load(path)
    if font_id == -1:
        raise Exception(f"Failed to load font from {path}")
    return font_id


def _draw_burn_in_text(
    context: bpy.types.Context,
    draw_rect: Rect,
    font_size: float,
    margin: float,
):
    """"""
    burn_in_props = context.scene.playblast.burn_in
    font_id = load_font(burn_in_props.font_family)

    # Setup blf font
    blf.size(font_id, font_size)
    blf.color(font_id, *burn_in_props.color)
    blf.enable(font_id, blf.SHADOW)

    # Draw each text to each corner
    for position, text_template in [
        ("top_left", burn_in_props.top_left),
        ("top_center", burn_in_props.top_center),
        ("top_right", burn_in_props.top_right),
        ("bottom_left", burn_in_props.bottom_left),
        ("bottom_center", burn_in_props.bottom_center),
        ("bottom_right", burn_in_props.bottom_right),
    ]:
        # if not text_template.strip():
        #     continue

        # # Format the text with context info
        # text = text_template.format(
        #     filename=bpy.path.basename(bpy.data.filepath) or "Untitled",
        #     version=bpy.path.basename(bpy.data.filepath).split(".")[-1]
        #     if bpy.data.filepath
        #     else "",
        #     datetime=bpy.utils.smpte_from_frame(context.scene.frame_current),
        #     width=draw_rect.width,
        #     height=draw_rect.height,
        #     frame=context.scene.frame_current,
        #     fps=context.scene.render.fps,
        # )
        text = text_template

        # Get text dimensions
        text_width, text_height = blf.dimensions(font_id, text)
        text_rect = Rect(0, 0, text_width, text_height)

        # Get the location to draw the text
        x, y = get_text_location(draw_rect, text_rect, margin, position)

        # Draw the text
        blf.position(font_id, x, y, 0)
        blf.draw(font_id, text)


def draw_burn_in_text_in_viewport():
    """Draw burn-in text on the viewport."""

    context = bpy.context

    if not poll(context):
        return

    burn_in_props = context.scene.playblast.burn_in
    if not burn_in_props.enable:
        return

    if not burn_in_props.preview:
        return

    original_font_size = burn_in_props.font_size
    original_margin = burn_in_props.margin

    draw_rect = get_camera_frame_rect(context)

    # Get real font size to draw
    res_x = context.scene.render.resolution_x
    font_size = original_font_size * draw_rect.width / res_x
    margin = original_margin * draw_rect.width / res_x

    _draw_burn_in_text(context, draw_rect, font_size, margin)


def draw_burn_in_text_in_render(context: bpy.types.Context):
    """Draw burn-in text in the offscreen rendered image."""
    burn_in_props = context.scene.playblast.burn_in
    if not burn_in_props.enable:
        return

    original_font_size = burn_in_props.font_size
    original_margin = burn_in_props.margin

    render = context.scene.render
    res_x = render.resolution_x
    res_y = render.resolution_y
    draw_rect = Rect(0, 0, res_x, res_y)

    # Get real font size to draw
    font_size = original_font_size * draw_rect.width / res_x
    margin = original_margin * draw_rect.width / res_x

    _draw_burn_in_text(context, draw_rect, font_size, margin)


def offscreen_render(
    context: bpy.types.Context, offscreen: gpu.types.GPUOffScreen
) -> bpy.types.Image:
    """Render a single frame offscreen."""

    render = context.scene.render
    playblast = context.scene.playblast

    resolution = (render.resolution_x, render.resolution_y)

    with offscreen.bind():
        offscreen.draw_view3d(
            scene=context.scene,
            view_layer=context.view_layer,
            view3d=context.space_data,
            region=context.region,
            view_matrix=context.scene.camera.matrix_world.inverted(),
            projection_matrix=context.scene.camera.calc_matrix_camera(
                context.evaluated_depsgraph_get(),
                x=resolution[0],
                y=resolution[1],
            ),
            do_color_management=True,
            draw_background=True,
        )

        if playblast.burn_in.enable:
            draw_burn_in_text_in_render(context)

        # Retrieve the image from the offscreen buffer
        buffer = offscreen.texture_color.read()

    # Create a new Blender image if not exists
    if "Playblast Result" not in bpy.data.images:
        bpy.data.images.new(
            "Playblast Result", width=resolution[0], height=resolution[1]
        )

    image = bpy.data.images["Playblast Result"]
    image.scale(resolution[0], resolution[1])

    # Copy buffer data to image
    t = time.time()
    print("Start copying buffer to image")

    buffer.dimensions = resolution[0] * resolution[1] * 4
    image.pixels = [v / 255 for v in buffer]

    print("Finish copying buffer to image", time.time() - t)

    return image
