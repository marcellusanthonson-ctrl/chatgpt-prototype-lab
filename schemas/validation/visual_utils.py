from .context import *

def relative_luminance(hex_color: str) -> float | None:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_color):
        return None
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

def contrast_ratio(foreground: str, background: str) -> float | None:
    first = relative_luminance(foreground)
    second = relative_luminance(background)
    if first is None or second is None:
        return None
    lighter, darker = sorted((first, second), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)

