"""The DengueWatch logo as an inline image (works offline)."""
from base64 import b64encode
from pathlib import Path

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"


def logo_img(size="1.3em"):
    """HTML image of the logo, sized to sit beside a title."""
    data = b64encode(LOGO_PATH.read_bytes()).decode()
    return (f"<img src='data:image/png;base64,{data}' alt='DengueWatch logo' "
            f"style='height:{size};width:{size};vertical-align:middle;margin-right:.25em'>")
