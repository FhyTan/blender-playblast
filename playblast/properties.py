import bpy

from .paths import TEMPORARY_OUTPUT_DIR


class VideoProperties(bpy.types.PropertyGroup):
    include_audio: bpy.props.BoolProperty(
        name="Include Audio",
        description="Include audio in the playblast video",
        default=True,
    )

    codec: bpy.props.EnumProperty(
        name="Codec",
        description="Video codec for playblast",
        items=[
            ("libx264", "H.264", "H.264 codec"),
            ("libx265", "H.265", "HEVC codec"),
            ("mpeg4", "MPEG-4", "MPEG-4 codec"),
            ("libsvtav1", "AV1", "AV1 codec"),
        ],
        default="libx264",
    )

    scale: bpy.props.IntProperty(
        name="Scale",
        description="Scale factor for the playblast resolution",
        subtype="PERCENTAGE",
        default=100,
        min=1,
        max=100,
    )

    use_frame_range: bpy.props.BoolProperty(
        name="Use Frame Range",
        description="Use specific frame range for the playblast instead of the entire scene frame range",
        default=False,
    )

    frame_start: bpy.props.IntProperty(
        name="Start Frame",
        description="Start frame for the playblast",
        default=1,
        min=0,
    )

    frame_end: bpy.props.IntProperty(
        name="End Frame",
        description="End frame for the playblast",
        default=250,
        min=0,
    )


def get_version_str(self):
    if not self.use_version:
        return ""
    return f"v{self.version:03d}"


def get_full_path(self):
    dir = self.directory
    name = self.name
    use_ver = self.use_version
    ver = self.version_str
    ext = self.extension

    if not dir or dir.strip() == "//":
        dir = bpy.path.abspath("//")

    if not dir:
        dir = TEMPORARY_OUTPUT_DIR.as_posix()

    dir = dir.replace("\\", "/")
    if not dir.endswith("/"):
        dir += "/"

    if use_ver:
        ver = "." + ver

    path = f"{dir}{name}{ver}{ext}"

    return path


class FileProperties(bpy.types.PropertyGroup):
    directory: bpy.props.StringProperty(
        name="Directory",
        description="Directory to save playblast file.\n"
        "If not specified, use current blend file directory.\n"
        "Or use system temp directory if blend file is not saved.",
        subtype="DIR_PATH",
        default="",
    )

    name: bpy.props.StringProperty(
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

    version_str: bpy.props.StringProperty(
        name="Version String",
        description="Read-only properties.\n"
        "Get version string from the version number."
        "If version is 1, return v001."
        "Else return empty string.",
        get=get_version_str,
    )

    full_path: bpy.props.StringProperty(
        name="Full Path",
        description="Read-only properties.\n"
        "Join all parts to get the full path of the playblast file.",
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
        default=r"File: {file_name}.{file_version}",
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
        default=r"Camera: {camera_name} {camera_focal}mm",
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

    first_load: bpy.props.BoolProperty(
        name="First Load",
        description="Internal property.\n"
        "Indicate if this is the first time loading the playblast settings.\n"
        "If true, load default settings from the saved json file.\n"
        "It will be set and persisted to false after the first load.",
        default=True,
        options={"HIDDEN"},
    )
