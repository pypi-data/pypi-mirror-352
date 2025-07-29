import base64
from pathlib import Path

def format_currency(value, currency="R$"):
    if value >= 1_000_000:
        val = f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        val = f"{value / 1_000:.1f}K"
    else:
        val = f"{value:.0f}"

    val = val.replace(".", ",")
    return f"{currency} {val}" if currency else val


def image_to_base64(path):
    img_path = Path(path)
    if img_path.exists():
        return base64.b64encode(img_path.read_bytes()).decode("utf-8")
    return ""