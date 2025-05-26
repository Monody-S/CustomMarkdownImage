# CustomMarkdownImage

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

## 图片预览

> 元素预览
![元素预览](https://raw.githubusercontent.com/Monody-S/CustomMarkdownImage/refs/heads/main/preview/预览1.gif)

> 分页+侧边图渲染
![额外效果](https://raw.githubusercontent.com/Monody-S/CustomMarkdownImage/refs/heads/main/preview/预览2.gif)

## Style下载

见[github](https://github.com/Monody-S/CustomMarkdownImage/tree/main/styles)

## 其他

欢迎各位分享你自己的style风格，联系QQ`614675349`，或者直接在GitHub上提交PR

## TODO

LaTex解析

## 更新日志

### 0.5.3

修复了表格渲染会错误的在前后加上行间距的问题
增加了表格的debug显示