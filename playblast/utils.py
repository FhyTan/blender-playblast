import shutil

from fontTools import ttLib


def get_full_font_name(ttf_path) -> str:
    with ttLib.TTFont(ttf_path) as font:
        full_name = font["name"].getDebugName(4)
    return full_name


def detect_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None
