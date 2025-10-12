import blf
import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d

from .metadata import get_metadata
from .text import Rect, iter_corner_text


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

    context = bpy.context

    if not poll(context):
        return

    props = context.scene.playblast.burn_in
    if not props.enable:
        return

    if not props.preview:
        return

    res_x = context.scene.render.resolution_x
    draw_rect = get_camera_frame_rect(context)
    metadata = get_metadata(context)

    # Draw each text to each corner
    for text in iter_corner_text(metadata):
        # Scale and move the text to fit in the camera frame
        factor = draw_rect.width / res_x
        text.scale(factor)
        text.move(draw_rect.x, draw_rect.y)

        # Draw the text
        font_id = text.font_id
        blf.size(font_id, text.font_size)
        blf.color(font_id, *text.font_color)
        blf.enable(font_id, blf.SHADOW)
        blf.position(font_id, text.rect.x, text.rect.y, 0)
        blf.draw(font_id, text.text)
