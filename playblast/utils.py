from pathlib import Path


def get_bfont_path() -> Path:
    """
    Since Blender's built-in font cannot be directly used in ffmpeg,
    I extracted it from the source code to a separate TTF file.
    For consistency, this plugin uses this font as the default.
    """

    return Path(__file__).parent / "bfont.ttf"
