import pillowmd
from PIL import Image
from pathlib import Path

"""
快速渲染例子（使用默认样式）
"""

def run():
    md = """# 一级标题
## 二级标题
### 三级标题

> 引用一级
>> 引用二级
>>> 引用三级
……

**加粗**~~删除线~~
[链接](http://baidu.com)

* 无序
* 列表

1. 有序
2. 列表

这是`行中代码`与$行中表达式：\\sin^2(\\pi)\\times\\cos^2(\\pi)$

|这|是|表|格|
|---|---|---|---|
|这是|表格里面的|元素|些|
|当然|可以|不止有一行|的元素|

```这是行中代码块
这是代码块里的内容
```"""

    logo = pillowmd.SampleStyles.SAMPLE_LOGO

    style = pillowmd.MdStyle()

    style.Render(
        md,
        "标题",
        logo = logo,
    ).image.show()