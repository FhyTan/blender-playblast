import os
import shutil
import tempfile
from typing import Dict

import bpy
import mathutils

from .metadata import MetaData, get_metadata
from .text import get_bfont_path, iter_corner_text


class PlayblastOperator(bpy.types.Operator):
    bl_idname = "render.playblast"
    bl_label = "Playblast"
    bl_description = "Create a playblast of the current scene"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def modal(self, context, event):
        wm = context.window_manager

        if event.type == "TIMER":
            if self.frame_render <= context.scene.frame_end:
                # Render single frame
                context.scene.frame_set(self.frame_render)
                context.scene.render.filepath = self.temp_png.format(self.frame_render)
                self.metadata[self.frame_render] = get_metadata(context)
                bpy.ops.render.opengl(write_still=True)
                wm.progress_update(self.frame_render)
                self.frame_render += 1
            else:
                # Finish the operation
                self.build_subtitles(context)
                self.build_video(context)
                self._teardown(context)
                print("Playblast completed")
                return {"FINISHED"}

        if event.type in {"ESC"}:
            # Cancel the operation
            self._teardown(context)
            print("Playblast canceled")
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        self.frame_render = context.scene.frame_start

        # Start the modal timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        wm.progress_begin(0, 9999)

        # Record and set up settings
        self._record_settings(context)
        self._setup_settings(context)

        # Create temporary directory for storing render frames and subtitles
        self.temp_dir = tempfile.mkdtemp(prefix="blender_playblast_").replace("\\", "/")
        self.temp_png = self.temp_dir + "/" + "{:04d}.png"
        self.temp_ass = self.temp_dir + "/" + "subtitles.ass"

        # Record metadata for each frame
        self.metadata: Dict[int, MetaData] = {}

        return {"RUNNING_MODAL"}

    def _teardown(self, context: bpy.types.Context):
        """Clear and recover everything after playblast is done."""

        # Stop the modal timer
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        wm.progress_end()

        # Recover settings
        self._recover_settings(context)

        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _record_settings(self, context: bpy.types.Context):
        """Record all settings that will be changed during the playblast."""

        render = context.scene.render

        self._filepath = render.filepath
        self._resolution_percentage = render.resolution_percentage
        self._use_file_extension = render.use_file_extension
        self._use_render_cache = render.use_render_cache
        self._file_format = render.image_settings.file_format
        self._color_mode = render.image_settings.color_mode
        self._color_depth = render.image_settings.color_depth
        self._compression = render.image_settings.compression

        self._frame_origin = context.scene.frame_current

    def _setup_settings(self, context: bpy.types.Context):
        """Set up all settings needed for the playblast."""

        render = context.scene.render
        props = context.scene.playblast
        video_props = props.video

        render.resolution_percentage = video_props.scale

        render.use_file_extension = False
        render.use_render_cache = False

        render.image_settings.file_format = "PNG"
        render.image_settings.color_mode = "RGB"
        render.image_settings.color_depth = "8"
        render.image_settings.compression = 15

    def _recover_settings(self, context: bpy.types.Context):
        """Recover all settings that were changed during the playblast."""

        render = context.scene.render

        render.filepath = self._filepath
        render.resolution_percentage = self._resolution_percentage
        render.use_file_extension = self._use_file_extension
        render.use_render_cache = self._use_render_cache
        render.image_settings.file_format = self._file_format
        render.image_settings.color_mode = self._color_mode
        render.image_settings.color_depth = self._color_depth
        render.image_settings.compression = self._compression

        bpy.context.scene.frame_set(self._frame_origin)

    def build_subtitles(self, context: bpy.types.Context):
        """Build subtitles of metadata for the video."""

        def _frame_to_timecode(frame, fps):
            """Convert frame number to ASS timecode format (H:MM:SS.cs)."""
            total_seconds = frame / fps
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = total_seconds % 60

            if frame != 0:
                seconds -= 0.01

            # ASS uses centiseconds (0.01s) for the fractional part
            return f"{hours}:{minutes:02d}:{seconds:06.2f}"

        def _get_hex_color(color):
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

        template_path = os.path.join(os.path.dirname(__file__), "template.ass")
        with open(template_path, "r", encoding="utf-8") as f:
            template_ass = f.read()

        metadata = self.metadata[scene.frame_start]
        subtitles = template_ass.format_map(
            {
                "res_x": metadata["width"],
                "res_y": metadata["height"],
                "font_name": "bfont",
                "font_size": props.burn_in.font_size,
                "font_color": _get_hex_color(props.burn_in.color),
            }
        )
        fps = metadata["frame_rate"]

        dialogues = []
        template_dialogue = (
            "Dialogue: 0,{start},{end},default,,0,0,0,,{{\\an1\\pos({x},{y})}}{text}"
        )
        for frame in range(scene.frame_start, scene.frame_end + 1):
            metadata = self.metadata[frame]
            for text in iter_corner_text(metadata):
                dialogues.append(
                    template_dialogue.format(
                        start=_frame_to_timecode(frame - scene.frame_start, fps),
                        end=_frame_to_timecode(frame - scene.frame_start + 1, fps),
                        text=text.text,
                        x=text.rect.x,
                        y=text.rect.y,
                    )
                )

        subtitles += "\n".join(dialogues)

        # Save subtitles to temporary folder
        with open(self.temp_ass, "w", encoding="utf-8") as f:
            f.write(subtitles)

    def build_video(self, context: bpy.types.Context):
        """Build video from the rendered frames using ffmpeg."""

        props = context.scene.playblast
        file_props = props.file
        video_props = props.video

        output_path = file_props.full_path
        input_pattern = os.path.join(self.temp_dir, "%04d.png")
        input_pattern = input_pattern.replace("\\", "/")

        codec = video_props.codec

        bfont_path = os.path.basename(get_bfont_path())
        escape_bfont_path = bfont_path.replace(":", "\\:")
        escape_ass_path = self.temp_ass.replace(":", "\\:")

        ffmpeg_cmd = (
            f"ffmpeg "
            f"-y "
            f"-framerate {context.scene.render.fps} "
            f"-start_number {context.scene.frame_start} "
            f'-i "{input_pattern}" '
            f"-c:v {codec} "
            f"-crf 23 "
            f"-pix_fmt yuv420p "
            f"-frames:v {context.scene.frame_end - context.scene.frame_start + 1} "
            f"-vf \"subtitles='{escape_ass_path}':fontsdir='{escape_bfont_path}'\" "
            f'"{output_path}"'
        )

        print("Executing command:", ffmpeg_cmd)
        result = os.system(ffmpeg_cmd)

        if result != 0:
            self.report({"ERROR"}, "Failed to build video with ffmpeg.")
        else:
            self.report({"INFO"}, f"Playblast saved to {output_path}, opening file.")
            print(f"Playblast saved to {output_path}, opening file.")
            os.startfile(output_path)
