import tempfile
from pathlib import Path

# Since Blender's built-in font cannot be directly used in ffmpeg,
# I extracted the bfont from the source code to a separate TTF file.
# For consistency, this plugin uses this font as the default.
BFONT_PATH = Path(__file__).parent / "font" / "bfont.ttf"

# Path to the ASS template file that is used to build subtitles
TEMPLATE_ASS_PATH = Path(__file__).parent / "template" / "template.ass"

# By default, the output playblast video will save to the folder of the blend file.
# But if the user does not save the blend file yet, we will use a temporary directory instead.
TEMPORARY_OUTPUT_DIR = Path(tempfile.gettempdir(), "blender_anim_reviewer")
