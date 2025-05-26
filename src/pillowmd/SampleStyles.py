import os
from PIL import Image
from pathlib import Path
from . import CustomMarkdownRenderer as Cmr

dataPath = Path(__file__).parent / "data"
sampleStylePath = dataPath / "sample_styles"

STYLE1 = Cmr.LoadMarkdownStyles(sampleStylePath / "Sample1")
"""独角兽Sugar风格，可爱系"""

STYLE2 = Cmr.LoadMarkdownStyles(sampleStylePath / "Sample2")
"""独角兽Suagar-GIF风格，GIF示例"""

STYLE3 = Cmr.LoadMarkdownStyles(sampleStylePath / "Sample3")
"""函数绘制背景示例"""

STYLE4 = Cmr.LoadMarkdownStyles(sampleStylePath / "Sample4")
"""朴素米黄风格"""

STYLE5 = Cmr.LoadMarkdownStyles(sampleStylePath / "Sample5")
"""最朴素的复古风格"""

SAMPLE_LOGO = Image.open(dataPath / "logo" / "sample.png")
SAMPLE_PAINT = Image.open(dataPath / "paint" / "sample.png")