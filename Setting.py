from pathlib import Path
from typing import Optional

FONT_PATH: Path = Path(__file__).parent / "fonts"
"""字体路径"""

DEFAULT_OUTPUT_PATH: Path = Path(__file__).parent / "output"
"""默认输出路径"""

PAINT_PATH: Path = Path(__file__).parent / "paints"
"""立绘路径"""

QUICK_IMAGE_PATH: Optional[Path] = Path(__file__).parent / "quick_images"
"""快速图像路径"""

IMAGE_DOWNLOAD_PATH: Path = Path(__file__).parent / "image_downloads"
"""图片下载路径"""

LOGO_PATH: Path = Path(__file__).parent / "logos"
"""LOGO路径"""

DEFAULT_IMAGE_PATH: Path = Path(__file__).parent / "default_images"
"""默认图片路径"""

DEFAULT_FONT: str = "smSans.ttf"
"""默认字体"""
DEFAULT_SECOND_FONTS: list[str] = [
    "yahei.ttf",
    "unifont.ttf"
]
"""默认备用字体"""