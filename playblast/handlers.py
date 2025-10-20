import logging
import os
from typing import List, Tuple
from pathlib import Path

import blf
import bpy
import gpu
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader

from .metadata import get_metadata
from .paths import bfont_path

logger = logging.getLogger(__name__)


def draw_text_in_viewport_handler():
    """Handler to draw burn-in text on the viewport"""

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

    def get_camera_frame_rect(
        context: bpy.types.Context,
    ) -> List[Tuple[float, float]]:
        """Get the rectangle of the camera frame in 3d viewport

        Returns:
            List of 4 tuples, each tuple is (x, y) coordinate of the rectangle corners
            in the order of top_right, bottom_right, bottom_left, top_left.

            Notice that the origin (0,0) is at the bottom-left corner of the viewport.
        """

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

        return frame_corners_2d

    def draw_rect(corners: List[Tuple[float, float]]):
        """Draw a rectangle in the viewport for debugging"""
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        shader.uniform_float("color", (0, 0.5, 0.5, 1.0))
        batch = batch_for_shader(
            shader,
            "LINES",
            {
                "pos": corners,
            },
            indices=((0, 1), (1, 2), (2, 3), (3, 0)),
        )
        batch.draw(shader)

    context = bpy.context

    if not poll(context):
        return

    props = context.scene.playblast.burn_in
    if not props.enable:
        return

    if not props.preview:
        return

    res_x = context.scene.render.resolution_x
    top_right, bottom_right, bottom_left, top_left = get_camera_frame_rect(context)
    metadata = get_metadata(context)

    # Calculate the scale factor to fit the text in the camera frame
    factor = (bottom_right[0] - bottom_left[0]) / res_x

    # Get font properties
    font_path = props.font_family
    if not font_path or not os.path.exists(font_path):
        font_path = bfont_path
    else:
        font_path = Path(font_path)
    font_id = blf.load(font_path.as_posix())
    font_size = int(props.font_size * factor)
    font_color = props.color
    font_margin = int(props.margin * factor)

    blf.size(font_id, font_size)
    blf.color(font_id, *font_color)
    blf.enable(font_id, blf.SHADOW)
    blf.shadow(font_id, 6, 0, 0, 0, 1)

    # Calculate baseline height
    # Reference: https://blender.stackexchange.com/questions/312413/blf-module-how-to-draw-text-in-the-center
    full_height = blf.dimensions(font_id, "GJKLPgjklp!?")[1]
    word_height = blf.dimensions(font_id, "x")[1]
    base_height = (full_height - word_height) // 2

    positions = [
        (
            "top_left",
            lambda w: (
                top_left[0] + font_margin,
                top_left[1] - full_height - font_margin + base_height,
            ),
        ),
        (
            "top_center",
            lambda w: (
                (top_left[0] + top_right[0]) / 2 - w / 2,
                top_right[1] - full_height - font_margin + base_height,
            ),
        ),
        (
            "top_right",
            lambda w: (
                top_right[0] - w - font_margin,
                top_right[1] - full_height - font_margin + base_height,
            ),
        ),
        (
            "bottom_left",
            lambda w: (
                bottom_left[0] + font_margin,
                bottom_left[1] + font_margin + base_height,
            ),
        ),
        (
            "bottom_center",
            lambda w: (
                (bottom_left[0] + bottom_right[0]) / 2 - w / 2,
                bottom_right[1] + font_margin + base_height,
            ),
        ),
        (
            "bottom_right",
            lambda w: (
                bottom_right[0] - w - font_margin,
                bottom_right[1] + font_margin + base_height,
            ),
        ),
    ]

    for pos, get_position in positions:
        text = getattr(props, pos)
        try:
            text = text.format_map(metadata)
        except Exception:
            logger.error(f'Error burn in text in {pos}: "{text}"')
            continue

        width, _ = blf.dimensions(font_id, text)
        pos_x, pos_y = get_position(width)
        blf.position(font_id, pos_x, pos_y, 0)
        blf.draw(font_id, text)
