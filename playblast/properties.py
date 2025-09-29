import bpy


class VideoProperties(bpy.types.PropertyGroup):
    codec: bpy.props.EnumProperty(
        name="Codec",
        description="Video codec for playblast",
        items=[
            ("H264", "H.264", "H.264 codec"),
            ("MPEG4", "MPEG-4", "MPEG-4 codec"),
            ("QuickTime", "QuickTime", "QuickTime codec"),
        ],
        default="H264",
    )

    quality: bpy.props.IntProperty(
        name="Quality",
        description="Quality of the video (1-100)",
        default=90,
        min=1,
        max=100,
    )

    scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale factor for the playblast resolution",
        default=1.0,
        min=0.1,
        max=1.0,
    )


def get_full_path(self):
    dir = self.directory
    name = self.filename
    use_ver = self.use_version
    ver = f".v{self.version:03d}"
    ext = self.extension

    dir = dir.replace("\\", "/")
    if not dir.endswith("/"):
        dir += "/"

    if use_ver:
        path = f"{dir}{name}{ver}{ext}"
    else:
        path = f"{dir}{name}{ext}"

    return path


class FileProperties(bpy.types.PropertyGroup):
    enable: bpy.props.BoolProperty(
        name="Enable Save To File",
        description="Enable saving the playblast to a file",
        default=True,
    )

    directory: bpy.props.StringProperty(
        name="Directory",
        description="Directory to save playblast file",
        subtype="DIR_PATH",
    )

    filename: bpy.props.StringProperty(
        name="File Name",
        description="Base name for playblast file",
        default="playblast",
    )

    use_version: bpy.props.BoolProperty(
        name="Use Version",
        description="",
        default=True,
    )

    version: bpy.props.IntProperty(
        name="Version",
        description="Version number for the playblast file",
        default=1,
        min=0,
    )

    extension: bpy.props.EnumProperty(
        name="Extension",
        description="File extension for playblast",
        items=[
            (".mp4", ".mp4", "MP4 format"),
            (".avi", ".avi", "AVI format"),
            (".mov", ".mov", "MOV format"),
        ],
        default=".mp4",
    )

    full_path: bpy.props.StringProperty(
        name="Full Path",
        description="Full path to the playblast file",
        get=get_full_path,
    )


class BurnInProperties(bpy.types.PropertyGroup):
    enable: bpy.props.BoolProperty(
        name="Enable Burn-In Data",
        description="Enable burn-in text overlay on the playblast, if not specified, use blender default font",
        default=True,
    )

    preview: bpy.props.BoolProperty(
        name="Preview in Viewport",
        description="Preview the burn-in text in the 3D viewport\n"
        "You need to be in Camera view to see it",
        default=True,
    )

    font_family: bpy.props.StringProperty(
        name="Font Family",
        description="Font family for the burn-in text",
        subtype="FILE_PATH",
        default="",
    )

    font_size: bpy.props.IntProperty(
        name="Font Size",
        description="Size of the burn-in text font",
        default=20,
    )

    margin: bpy.props.IntProperty(
        name="Margin",
        description="Text margin from the edges of the viewport",
        default=10,
    )

    color: bpy.props.FloatVectorProperty(
        name="Color",
        description="Color of the burn-in text",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )

    top_left: bpy.props.StringProperty(
        name="Top Left",
        description="Text to display in the top left corner",
        default=r"File: {filename}.{version}",
    )

    top_center: bpy.props.StringProperty(
        name="Top Center",
        description="Text to display in the top center",
        default=r"",
    )

    top_right: bpy.props.StringProperty(
        name="Top Right",
        description="Text to display in the top right corner",
        default=r"Date: {datetime}",
    )

    bottom_left: bpy.props.StringProperty(
        name="Bottom Left",
        description="Text to display in the bottom left corner",
        default=r"Resolution: {width}x{height}",
    )

    bottom_center: bpy.props.StringProperty(
        name="Bottom Center",
        description="Text to display in the bottom center",
        default=r"Camera: {camera_name} {focal_length}mm",
    )

    bottom_right: bpy.props.StringProperty(
        name="Bottom Right",
        description="Text to display in the bottom right corner",
        default=r"Frame: {frame_current} | {frame_start}-{frame_end}",
    )


class PlayblastProperties(bpy.types.PropertyGroup):
    video: bpy.props.PointerProperty(type=VideoProperties)
    file: bpy.props.PointerProperty(type=FileProperties)
    burn_in: bpy.props.PointerProperty(type=BurnInProperties)
