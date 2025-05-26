from pathlib import Path
from typing import Optional

FONT_PATH: Path = Path(__file__).parent / "data" / "fonts"
"""字体路径"""
IMAGE_DOWNLOAD_PATH: Path = Path(__file__).parent / "image_downloads"
"""图片下载路径"""



PAINT_PATH: Optional[Path] = None
"""立绘路径（传入paint时使用）"""
QUICK_IMAGE_PATH: Optional[Path] = None
"""快速图像路径（使用“!sgm[]”时使用）"""
LOGO_PATH: Optional[Path] = None
"""LOGO路径（传入logo时使用）"""
DEFAULT_IMAGE_PATH: Optional[Path] = None
"""默认图片路径（没有配置图片存储路径时使用）"""



DEFAULT_FONT: str = "smSans.ttf"
"""默认字体"""
DEFAULT_SECOND_FONTS: list[str] = [
    "yahei.ttf",
    "unifont.ttf"
]
"""默认备用字体"""