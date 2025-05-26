import pillowmd
from PIL import Image
from pathlib import Path

"""
分页+立绘例子（自动分页）
"""

def run():
    md = "[芳糖助手](https://bot.q.qq.com/s/3ewpir2j0?id=102070088)\n"*300

    paint = pillowmd.SampleStyles.SAMPLE_PAINT

    style = pillowmd.MdStyle()
    style.Render(
        md,
        autoPage = True,
        paint = paint
    ).image.show()