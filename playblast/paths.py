from pathlib import Path

# Since Blender's built-in font cannot be directly used in ffmpeg,
# I extracted the bfont from the source code to a separate TTF file.
# For consistency, this plugin uses this font as the default.
bfont_path = Path(__file__).parent / "font" / "bfont.ttf"

# Path to the ASS template file that is used to build subtitles
template_ass_path = Path(__file__).parent / "template" / "template.ass"
