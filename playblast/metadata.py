import os
from collections import defaultdict
from datetime import datetime
from typing import TypedDict

import bpy


class MetaData(TypedDict):
    """The metadata used to replace the placeholders for burn-in text."""

    datetime: str
    width: int
    height: int
    file_name: str
    file_version: str
    file_ext: str
    file_full_name: str
    frame_current: int
    frame_start: int
    frame_end: int
    frame_rate: int
    camera_name: str
    camera_focal: float


def get_metadata(context: bpy.types.Context, datetime_: datetime = None) -> MetaData:
    """Get the metadata for current frame in the given context."""

    scene = context.scene
    render = scene.render
    props = scene.playblast

    # Get Resolution Info
    scale = props.video.scale
    res_x = int(render.resolution_x * scale / 100)
    res_y = int(render.resolution_y * scale / 100)

    # Make sure resolution is even
    if res_x % 2 != 0:
        res_x += 1
    if res_y % 2 != 0:
        res_y += 1

    # Get camera info
    camera = scene.camera
    if camera and camera.type == "CAMERA":
        camera_focal = f"{camera.data.lens:.2f}"
        camera_name = camera.name
    else:
        camera_focal = ""
        camera_name = ""

    datetime_ = datetime_ or datetime.now()

    metadata: MetaData = {
        "datetime": datetime_.strftime("%Y-%m-%d %H:%M:%S"),
        "width": int(render.resolution_x * render.resolution_percentage / 100),
        "height": int(render.resolution_y * render.resolution_percentage / 100),
        "file_name": props.file.name,
        "file_version": props.file.version_str,
        "file_ext": props.file.extension,
        "file_full_name": os.path.basename(props.file.full_path),
        "frame_current": scene.frame_current,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "frame_rate": int(render.fps),
        "camera_name": camera_name,
        "camera_focal": camera_focal,
    }

    return defaultdict(str, metadata)
