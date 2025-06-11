import pillowmd
from PIL import Image
from pathlib import Path

"""
latex渲染例子
"""

def run():

    style = pillowmd.SampleStyles.STYLE1

    t = "".join([
        r"\frac{1}{\frac{a}{{a}{b}c \frac{c}{d}} (\sqrt{\sqrt[\frac{1}{2} + \binom{\frac{1}{2} }{2}]1})^2} \times \frac{1}{\frac{a}{{a}{b}c \frac{c}{d}} (\sqrt{\sqrt[5]1})^2}\times\sin(1+\frac{a}{b}) \times \ddot{\frac{1}{2} }^{(n)} \times \pmod{123} _{123}^{\frac{1}{2}} \times 123 \times \sideset{_1^2}{_3^4}{\frac{1}{2}}_a^b \times \frac{1}{2}^1_2 \hat{123} \check{444} \grave{a} \acute{a} \tilde{a} \breve{a} \bar{a} \vec{a} ",
        r"\not{a} \widetilde{123456} \widehat{12345} \overleftarrow{123456} \overline{99999} \underline{99999} \overbrace{999999999999999999} \underbrace{9999999} \overset{a}{b}",
        r"\stackrel\frown{12345} \overleftrightarrow{999999999} \xleftarrow[1111]{123456} \xrightarrow[111]{999} \lim_{x \to 0} \textstyle \lim_{x \to 0}",
        r"\log_{1}{5} \int_{1}^{2} \int\limits_{5}^{5} \sum_{1}^{5} \textstyle \sum_{2}^{3} \left ( \frac{5}{\frac{9}{9}} testbig \right ) 123456 \int_{\sum_{a}^{b} }^{c} \left \lfloor 123 \right \rfloor ",
        r"\|\| \binom{\frac{1}{2} }{2} \begin{pmatrix}1 & 2 & 3\\ 1 & 2\\4 & 6 & 89898 & \frac{1}{2}\end{pmatrix}\begin{vmatrix}1 & 2 & 3\\ 1 & 2\\4 & 6 & 89898 & \frac{1}{2}\end{vmatrix}",
        r"\begin{Vmatrix}1 & 2 & 3\\ 1 & 2\\4 & 6 & 89898 & \frac{1}{2}\end{Vmatrix}\begin{Bmatrix}1 & 2 & 3\\ 1 & 2\\4 & 6 & 89898 & \frac{1}{2}\end{Bmatrix}",
        r"""\begin{cases}& \text{ if } x=  & \text{ if } x=  & \text{ if } x=  & \text{ if } x= \\& \text{ if } x=  & \text{ if } x=  & \frac{1}{\frac{a}{{a}{b}c \frac{c}{d}} (\sqrt{\sqrt[\frac{1}{2} + \binom{\frac{1}{2} }{2}]1})^2}   & \text{ if } x= \\& \text{ if } x=  & \text{ if } x=  & \text{ if } x=  & \text{ if } x= \\& \text{ if } x=  & \text{ if } x=  & \text{ if } x=  & \text{ if } x= \\& \text{ if } x=  & \text{ if } x=  & \text{ if } x=  & \frac{1}{\frac{a}{{a}{b}c \frac{c}{d}} (\sqrt{\sqrt[\frac{1}{2} + \binom{\frac{1}{2} }{2}]1})^2} \end{cases}"""
    ])

    style.Render(f"""|这|是|表|格|
|---|---|---|---|
|这是|表格里面的|元素|些|
|当然|可以|不止有一行|的元素|
            
12132
             
新版本的表达式足够强大，可以渲染这一坨巨无霸：
${t}$

# 一级标题
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
```

$$
这是行间latex表达式：\\sin^2(\\pi)\\times\\cos^2(\\pi)$
$$

""",title="标题").image.show()