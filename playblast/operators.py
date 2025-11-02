import json
import os
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict

import bpy
from bpy.app.translations import pgettext_rpt as rpt_
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .metadata import MetaData, get_metadata
from .paths import BFONT_PATH, DEFAULT_SETTINGS_FILE, TEMPLATE_ASS_PATH
from .utils import detect_ffmpeg, get_full_font_name, play_video


class PlayblastOperator(bpy.types.Operator):
    bl_idname = "playblast.run"
    bl_label = "Run Playblast"
    bl_description = (
        "Create a playblast video of the current scene.\n"
        "Please ensure you have an active camera and ffmpeg is installed in your system."
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.area.type == "VIEW_3D" and context.scene.camera is not None

    def execute(self, context: bpy.types.Context):
        # First detect whether ffmpeg is installed
        if not detect_ffmpeg():
            self.report(
                {"ERROR"},
                "FFmpeg is not installed or not found in PATH.",
            )
            return {"CANCELLED"}

        # Create temporary directory for storing render frames and subtitles
        self.temp_dir = tempfile.mkdtemp(prefix="blender_playblast_").replace("\\", "/")
        self.temp_png = self.temp_dir + "/" + "{:04d}.png"
        self.temp_ass = self.temp_dir + "/" + "subtitles.ass"
        self.temp_aud = self.temp_dir + "/" + "audio.mp3"

        # Get user Specified font path and copy to temporary directory
        # This method can avoid error log for ffmpeg
        spec_font_path: Path = context.scene.playblast.burn_in.font_family
        if not spec_font_path or not os.path.exists(spec_font_path):
            spec_font_path = BFONT_PATH
        else:
            spec_font_path = Path(spec_font_path)

        self.temp_font = Path(self.temp_dir, "font", spec_font_path.name)
        self.temp_font.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(spec_font_path, self.temp_font)

        # Record metadata for each frame
        self.metadata: Dict[int, MetaData] = {}
        self.datetime = datetime.now()

        with (
            render_properties_override(context),
            register_collect_metadata_handler(context),
        ):
            context.scene.render.filepath = self.temp_dir + "/"
            bpy.ops.render.opengl(animation=True, view_context=True)

            self.metadata = context.scene.playblast["metadata"]
            for data in self.metadata.values():
                data["datetime"] = self.datetime.isoformat(sep=" ", timespec="seconds")

            self.build_subtitles(context)
            self.build_audio(context)
            self.build_video(context)

        return {"FINISHED"}

    # def modal(self, context, event):
    #     wm = context.window_manager

    #     if event.type == "TIMER":
    #         frame_current = context.scene.frame_current
    #         if frame_current <= context.scene.frame_end:
    #             # Render single frame
    #             context.scene.render.filepath = self.temp_png.format(frame_current)
    #             self.metadata[frame_current] = get_metadata(context, self.datetime)
    #             bpy.ops.render.opengl(write_still=True)
    #             wm.progress_update(frame_current)

    #             # Move to next frame
    #             context.scene.frame_set(frame_current + 1)
    #         else:
    #             # Finish the operation
    #             self.build_subtitles(context)
    #             self.build_audio(context)
    #             self.build_video(context)
    #             self._teardown(context)
    #             return {"FINISHED"}

    #     if event.type in {"ESC"}:
    #         # Cancel the operation
    #         self._teardown(context)
    #         self.report({"INFO"}, "Playblast canceled")
    #         return {"CANCELLED"}

    #     return {"PASS_THROUGH"}

    def build_subtitles(self, context: bpy.types.Context):
        """Build subtitles of metadata for the video."""

        def frame_to_timecode(frame, fps):
            """Convert frame number to ASS timecode format (H:MM:SS.cs)."""
            total_seconds = frame / fps
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = total_seconds % 60

            if frame != 0:
                seconds -= 0.01

            # ASS uses centiseconds (0.01s) for the fractional part
            return f"{hours}:{minutes:02d}:{seconds:06.2f}"

        def get_hex_color(color):
            # Copy color list
            color = list(color)

            # # Convert scene linear to srgb
            # color[0:3] = list(mathutils.Color(color[:3]).from_scene_linear_to_srgb())

            # ASS Subtitle use reversed alpha channel
            color[3] = 1 - color[3]

            # ASS Subtitle use reversed order, it is AABBGGRR
            color.reverse()

            for i, c in enumerate(color):
                # Convert color from 0~1 to 0~255
                cc = int(round(c * 255))

                # Convert color from dec to hex
                color[i] = f"{cc:02X}"

            return "".join(["&H", *color])

        scene = context.scene
        props = scene.playblast

        with open(TEMPLATE_ASS_PATH, "r", encoding="utf-8") as f:
            template_ass = f.read()

        metadata = self.metadata[str(scene.frame_start)]
        res_x = metadata["width"]
        res_y = metadata["height"]
        fps = metadata["frame_rate"]

        # Get real name of font
        font_name = get_full_font_name(self.temp_font)

        # Keep text ratio regardless of resolution scale
        font_size = props.burn_in.font_size * props.video.scale // 100

        # Get correct color format
        font_color = get_hex_color(props.burn_in.color)

        subtitles = template_ass.format_map(
            {
                "res_x": res_x,
                "res_y": res_y,
                "font_name": font_name,
                "font_size": font_size,
                "font_color": font_color,
            }
        )

        # Also scale margin to keep aspect ratio
        margin = props.burn_in.margin * props.video.scale // 100

        dialogues = []
        template_dialogue = "Dialogue: 0,{start},{end},default,,0,0,0,,{{\\an{align}\\pos({x},{y})}}{text}"
        for frame in range(scene.frame_start, scene.frame_end + 1):
            metadata = self.metadata[str(frame)]
            start = frame_to_timecode(frame - scene.frame_start, fps)
            end = frame_to_timecode(frame - scene.frame_start + 1, fps)

            # Notice that the origin (0,0) is at the top-left corner for ass subtitles
            for pos in (
                "top_left",
                "top_center",
                "top_right",
                "bottom_left",
                "bottom_center",
                "bottom_right",
            ):
                text = getattr(props.burn_in, f"{pos}")
                try:
                    text = text.format_map(metadata)
                except Exception:
                    self.report(f'Error burn in text in {pos}: "{text}"')
                    continue

                if pos == "top_left":
                    align = "7"
                    x = margin
                    y = margin
                elif pos == "top_center":
                    align = "8"
                    x = res_x // 2
                    y = margin
                elif pos == "top_right":
                    align = "9"
                    x = res_x - margin
                    y = margin
                elif pos == "bottom_left":
                    align = "1"
                    x = margin
                    y = res_y - margin
                elif pos == "bottom_center":
                    align = "2"
                    x = res_x // 2
                    y = res_y - margin
                elif pos == "bottom_right":
                    align = "3"
                    x = res_x - margin
                    y = res_y - margin

                dialogue = template_dialogue.format(
                    start=start,
                    end=end,
                    align=align,
                    x=x,
                    y=y,
                    text=text,
                )
                dialogues.append(dialogue)

        subtitles += "\n".join(dialogues)

        # Save subtitles to temporary folder
        with open(self.temp_ass, "w", encoding="utf-8") as f:
            f.write(subtitles)

    def build_audio(self, context: bpy.types.Context):
        """Build audio file use blender's built-in tools."""

        props = context.scene.playblast.video
        if not props.include_audio:
            return

        # Render audio
        bpy.ops.sound.mixdown(
            filepath=self.temp_aud,
            container="MP3",
            codec="MP3",
        )

    def build_video(self, context: bpy.types.Context):
        """Build video from the rendered frames using ffmpeg."""

        props = context.scene.playblast
        file_props = props.file
        video_props = props.video
        include_audio = video_props.include_audio

        output_path = file_props.full_path
        png_pattern = self.temp_dir + "/%04d.png"

        codec = video_props.codec

        escape_font_path = self.temp_font.parent.as_posix().replace(":", "\\:")
        escape_ass_path = self.temp_ass.replace(":", "\\:")

        # Ensure output path exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        ffmpeg_cmd = (
            "ffmpeg " +
            "-y " +
            f"-framerate {context.scene.render.fps} " +
            f"-start_number {context.scene.frame_start} " +
            f'-i "{png_pattern}" ' +
            (f'-i "{self.temp_aud}" ' if include_audio else "") +
            f"-c:v {codec} " +
            ("-c:a copy " if include_audio else "") +
            "-map 0:v:0 " +
            ("-map 1:a:0 " if include_audio else "") +
            "-crf 23 " +
            "-pix_fmt yuv420p " +
            f"-frames:v {context.scene.frame_end - context.scene.frame_start + 1} " +
            f"-vf \"scale='iw+mod(iw,2)':'ih+mod(ih,2)',subtitles='{escape_ass_path}':fontsdir='{escape_font_path}'\" " +
            f'"{output_path}"'
        )  # fmt: skip

        print("Executing command:", ffmpeg_cmd)
        result = os.system(ffmpeg_cmd)

        if result != 0:
            self.report({"ERROR"}, "Failed to build video with ffmpeg.")
        else:
            self.report(
                {"INFO"},
                rpt_(
                    msgid='Playblast completed, saved to "{}", opening video...'
                ).format(output_path),
            )
            play_video(output_path)


class SaveAsDefaultOperator(bpy.types.Operator):
    bl_idname = "playblast.save_as_default"
    bl_label = "Save As Default"
    bl_description = "Save the current playblast settings as default, then your new blender file will use these playblast settings as default."

    def execute(self, context):
        bpy.ops.playblast.export_settings(filepath=DEFAULT_SETTINGS_FILE.as_posix())
        self.report(
            {"INFO"},
            "Default playblast settings saved. New blender files will use these settings.",
        )
        return {"FINISHED"}


class ImportSettingsOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "playblast.import_settings"
    bl_label = "Import Settings"
    bl_description = "Import playblast settings from a file"

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def execute(self, context):
        props = context.scene.playblast
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        props.video.codec = data.get("video.codec", props.video.codec)
        props.video.include_audio = data.get(
            "video.include_audio", props.video.include_audio
        )
        props.file.extension = data.get("file.extension", props.file.extension)
        props.burn_in.enable = data.get("burn_in.enable", props.burn_in.enable)
        props.burn_in.preview = data.get("burn_in.preview", props.burn_in.preview)
        props.burn_in.font_family = data.get(
            "burn_in.font_family", props.burn_in.font_family
        )
        props.burn_in.font_size = data.get("burn_in.font_size", props.burn_in.font_size)
        props.burn_in.margin = data.get("burn_in.margin", props.burn_in.margin)
        props.burn_in.color = data.get("burn_in.color", list(props.burn_in.color))
        props.burn_in.top_left = data.get("burn_in.top_left", props.burn_in.top_left)
        props.burn_in.top_center = data.get(
            "burn_in.top_center", props.burn_in.top_center
        )
        props.burn_in.top_right = data.get("burn_in.top_right", props.burn_in.top_right)
        props.burn_in.bottom_left = data.get(
            "burn_in.bottom_left", props.burn_in.bottom_left
        )
        props.burn_in.bottom_center = data.get(
            "burn_in.bottom_center", props.burn_in.bottom_center
        )
        props.burn_in.bottom_right = data.get(
            "burn_in.bottom_right", props.burn_in.bottom_right
        )

        return {"FINISHED"}


class ExportSettingsOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "playblast.export_settings"
    bl_label = "Export Settings"
    bl_description = "Export current playblast settings to a file"

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def execute(self, context: bpy.types.Context):
        props = context.scene.playblast
        data = {
            "video.codec": props.video.codec,
            "video.include_audio": props.video.include_audio,
            "file.extension": props.file.extension,
            "burn_in.enable": props.burn_in.enable,
            "burn_in.preview": props.burn_in.preview,
            "burn_in.font_family": props.burn_in.font_family,
            "burn_in.font_size": props.burn_in.font_size,
            "burn_in.margin": props.burn_in.margin,
            "burn_in.color": list(props.burn_in.color),
            "burn_in.top_left": props.burn_in.top_left,
            "burn_in.top_center": props.burn_in.top_center,
            "burn_in.top_right": props.burn_in.top_right,
            "burn_in.bottom_left": props.burn_in.bottom_left,
            "burn_in.bottom_center": props.burn_in.bottom_center,
            "burn_in.bottom_right": props.burn_in.bottom_right,
        }

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return {"FINISHED"}


# @contextmanager
# def temporary_directory():
#     """Context manager for creating and cleaning up a temporary directory."""

#     temp_dir = tempfile.mkdtemp(prefix="blender_playblast_").replace("\\", "/")
#     try:
#         yield temp_dir
#     finally:
#         shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def render_properties_override(context: bpy.types.Context):
    """Context manager for overriding render properties during playblast"""

    scene = context.scene
    render = scene.render
    props = context.scene.playblast

    # Store original render properties
    frame_current = scene.frame_current
    frame_start = scene.frame_start
    frame_end = scene.frame_end

    resolution_x = render.resolution_x
    resolution_y = render.resolution_y
    resolution_percentage = render.resolution_percentage

    filepath = render.filepath
    use_file_extension = render.use_file_extension
    use_render_cache = render.use_render_cache
    file_format = render.image_settings.file_format
    color_mode = render.image_settings.color_mode
    color_depth = render.image_settings.color_depth
    compression = render.image_settings.compression

    # Setup render properties for playblast
    metadata = get_metadata(context)

    scene.frame_start = metadata["frame_start"]
    scene.frame_end = metadata["frame_end"]
    render.resolution_percentage = props.video.scale
    render.use_file_extension = True
    render.use_render_cache = False
    render.image_settings.file_format = "PNG"
    render.image_settings.color_mode = "RGB"
    render.image_settings.color_depth = "8"
    render.image_settings.compression = 15

    # Ensure the VIEW_3D area is in camera view
    region_3d = context.region_data
    region_3d.view_perspective = "CAMERA"

    try:
        yield
    finally:
        scene.frame_set(frame_current)
        scene.frame_start = frame_start
        scene.frame_end = frame_end

        render.resolution_x = resolution_x
        render.resolution_y = resolution_y
        render.resolution_percentage = resolution_percentage

        render.filepath = filepath
        render.use_file_extension = use_file_extension
        render.use_render_cache = use_render_cache
        render.image_settings.file_format = file_format
        render.image_settings.color_mode = color_mode
        render.image_settings.color_depth = color_depth
        render.image_settings.compression = compression


@contextmanager
def register_collect_metadata_handler(context: bpy.types.Context):
    """Register a handler to collect metadata after each frame is rendered."""

    def handler(scene: bpy.types.Scene, dependency):
        metadata = get_metadata(bpy.context)
        scene.playblast["metadata"][str(scene.frame_current)] = metadata

    context.scene.playblast["metadata"] = {}
    bpy.app.handlers.frame_change_post.append(handler)

    try:
        yield
    finally:
        bpy.app.handlers.frame_change_post.remove(handler)
        del context.scene.playblast["metadata"]
