<div align="center">

  <a href="https://github.com/Monody-S/CustomMarkdownImage/blob/main/icon/repository-open-graph-template.png?raw=true">
    <img src="https://github.com/Monody-S/CustomMarkdownImage/blob/main/icon/repository-open-graph-template.png?raw=true" max-width=100% height=auto alt="pillowmd">
  </a>

# CustomMarkdownImage

✨ 基于pillow的可自定义markdown渲染器 ✨

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/Monody-S/CustomMarkdownImage/master/LICENSE">
    <img src="https://img.shields.io/github/license/Monody-S/CustomMarkdownImage" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/pillowmd">
    <img src="https://img.shields.io/pypi/v/pillowmd?logo=python&logoColor=edb641" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=edb641" alt="python">
  <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/Monody-S/CustomMarkdownImage">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/Monody-S/CustomMarkdownImage">
  <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/pillowmd">
  <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/Monody-S/CustomMarkdownImage">
  <br />
  <a href="https://www.latex-project.org">
    <img src="https://img.shields.io/badge/LaTeX-red" alt="LaTeX">
  </a>
  <a href="https://daringfireball.net/projects/markdown">
    <img src="https://img.shields.io/badge/Markdown-red" alt="Markdown">
  </a>
  <a href="https://github.com/python-pillow/Pillow">
    <img src="https://img.shields.io/badge/Pillow-red" alt="Pillow">
  </a>
  <a href="https://github.com/Monody-S/pillowlatex">
    <img src="https://img.shields.io/badge/PillowLaTeX-red" alt="PillowLaTeX">
  </a>
  <img src="https://img.shields.io/badge/NoBrowser-green" alt="NoBrowser">
  <img src="https://img.shields.io/badge/NoMatplotlib-green" alt="NoMatplotlib">
  <br />
  <a href="https://qm.qq.com/q/h8hYy8j6YU">
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-498427849-orange?style=flat-square" alt="QQ Chat Group">
  </a>
  <a href="https://pd.qq.com/s/51umxrsg0">
    <img src="https://img.shields.io/badge/QQ%E9%A2%91%E9%81%93-SugarPublic-5492ff?style=flat-square" alt="QQ Channel">
  </a>
</p>

## 开始使用

使用`pip install pillowmd`

## 如何使用

先使用`style = pillowmd.LoadMarkdownStyles(style路径)`，然后使用`style.Render(markdown内容)`即可快速渲染。若没有style，则可以`pillowmd.MdToImage(内容)`使用默认风格渲染

注：MdToImage是异步函数，若想使用默认风格进行同步渲染，请使用：

```python
import pillowmd
style = pillowmd.MdStyle()
style.Render("# Is Markdown")
```

## 自定义style

见`docs`目录下的`how_to……`，里面有进一步指南，也可以进入Q群`498427849`

## 使用例

见tests目录

## 元素支持

### markdown元素

|元素|样例|是否支持|备注|
|-|-|-|-|
|标题|# 标题|✅️|仅支持1~3级标题|
|引用|> 123|✅️||
|无序列表|* 123<br>* 123|✅️||
|有序列表|1. 123<br>2. 123|✅️||
|行中代码|这是\`行中代码\`|✅️|不支持高亮|
|行中表达式|这是\$行中表达式\$|✅️|支持latex，且支持latex拆分换行，详见[pillowlatex](https://github.com/Monody-S/pillowlatex)|
|表格|\|这是\|表格\|<br>\|-\|-\|<br>\|1\|2\||✅️|表格中仅支持普通文本，且不支持自定义对其方式。会自动换行|
|代码块|\`\`\`python<br>print("hello world")<br>\`\`\`|✅️|不支持高亮|
|行间表达式|&&<br>\frac{1}{2}<br>&&|✅️|支持latex，且支持latex拆分换行，详见[pillowlatex](https://github.com/Monody-S/pillowlatex)|
|HTML|\<br\>|❎️|暂不支持|

### 额外元素
|元素|样例|备注|
|-|-|-|
|自定义颜色|<color=#FF0000>|强制更改颜色，填入#xxxxxx格式的颜色，填入None则为取消强制更改|
|快捷图片|!sgm[图片名]<br>!sgm[图片名\|比例]<br>!sgm[图片名\|x比例,y比例]|需要设置快捷图片路径，可在渲染时取消使用该元素|
|自定义元素|!sgexter[元素名,参数……]<br>!sgexter[card,"title","content",800,400,"图片.jpg"]|可在渲染时取消使用该元素|

### 渲染差异
当仅有一个\n时，也会换行

## 图片预览

> 元素预览
![元素预览](https://raw.githubusercontent.com/Monody-S/CustomMarkdownImage/refs/heads/main/preview/预览1.gif)
> 分页+侧边图渲染
![额外效果](https://raw.githubusercontent.com/Monody-S/CustomMarkdownImage/refs/heads/main/preview/预览2.gif)
> 新版本LaTeX支持
![额外效果](https://raw.githubusercontent.com/Monody-S/CustomMarkdownImage/refs/heads/main/preview/预览3.png)

## Style下载

见[github](https://github.com/Monody-S/CustomMarkdownImage/tree/main/styles)

## 其他

欢迎各位分享你自己的style风格，联系QQ`614675349`，或者直接在GitHub上提交PR

## 更新日志

### 0.7.0

新增行间latex支持，优化readme，现在引用一级的线会被渲染出来了

### 0.6.0

新增latex支持，详见[pillowlatex](https://github.com/Monody-S/pillowlatex)

### 0.5.3

修复了表格渲染会错误的在前后加上行间距的问题
增加了表格的debug显示
