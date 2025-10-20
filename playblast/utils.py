from fontTools import ttLib


def get_full_font_name(ttf_path: str) -> str:
    with ttLib.TTFont(ttf_path) as font:
        full_name = font["name"].getDebugName(4)
    return full_name


if __name__ == "__main__":
    print(get_full_font_name("C:/Windows/Fonts/segoeprb.ttf"))
