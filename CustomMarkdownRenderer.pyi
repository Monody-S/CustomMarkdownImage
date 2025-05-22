"""
自定义markdown渲染器
"""
from PIL import Image
from typing import Union,TypeAlias,Literal,ParamSpec
from typing import Any,Optional,Callable,Sequence
from pathlib import Path

from .Setting import (
    DEFAULT_FONT,
    DEFAULT_SECOND_FONTS,
    DEFAULT_IMAGE_PATH
)

fileUri:TypeAlias = Union[Path,str]

from dataclasses import dataclass

class MDDecorates:
    def __init__(
        self,
        backGroundMode:int,
        backGroundData:dict,
        topDecorates:dict,
        bottomDecorates:dict,
        path:Path,
        page:Optional[int],
        duratio:float,
        playbackSequence:Optional[str]
    ) -> None:
        self.backGroundMode = backGroundMode
        self.backGroundData = backGroundData
        self.topDecorates = topDecorates
        self.bottomDecorates = bottomDecorates
        self.path = path
        self.imagePath = self.path / "imgs"
        self.imageCache = {}
        self.gifPage:Optional[int] = page
        self.duratio = duratio

        self.playbackSequence:list[int]
    
    def GetImage(self, name: str, lock: bool = False) -> Image.Image:...
    
    def Draw(self,x:int,y:int,page:Optional[int] = None) -> Image.Image:...
    
    def DrawTop(self,x:int,y:int,page:Optional[int] = None) -> Image.Image:...

@dataclass
class MdRenderResult:
    image: Image.Image
    """渲染结果"""

    imageType: str
    """图片文件类型"""

    images: list[Image.Image]
    """多图渲染结果"""

    gifDuratio: float
    """GIF动画间隔时长"""

    def Save(self, path: Union[Path, str]) -> Path:
        """
        保存并获取文件路径
        """

        ...

mdColor:TypeAlias = Union[tuple[int,int,int],tuple[int,int,int,int]]
mdBackGroundDrawFunc:TypeAlias = Callable[[int,int],Image.Image]

def DefaultMdBackGroundDraw(xs:int,ys:int) -> Image.Image:...

mdPageLineStyle:TypeAlias = Literal["full_line","dotted_line"]

@dataclass
class MdStyle:
    """Markdown生成风格"""
    name:str = ""
    """名称"""
    intr:str = ""
    """简介"""
    author:str = ""
    """作者"""
    version:str = "1.0"
    """版本号"""

    cost:int = 0
    """价格"""
    selling:bool = False
    """正在出售"""

    path:Path = Path(".")
    """数据所在目录"""

    fontSize:int = 25
    """普通文本大小"""

    title1FontSize:int = 70
    """一级标题文本大小"""
    title2FontSize:int = 55
    """二级标题文本大小"""
    title3FontSize:int = 40
    """三级标题文本大小"""

    expressionFontSizeRate:float = 0.8
    """表达式类（包括行中代码）字体缩放倍率"""

    codeBlockFontSize:int = 15
    """行中代码块文本大小"""

    rd:int = 30
    """右边距"""
    ld:int = 30
    """左边距"""
    ud:int = 30
    """上边距"""
    dd:int = 30
    """下边距"""

    xSizeMax:int = 1000
    """X轴单行元素最大长度"""

    font:str = DEFAULT_FONT
    """正文字体"""
    titleFont:str = DEFAULT_FONT
    """标题字体"""
    expressionFont:str = DEFAULT_FONT
    """表达式字体"""
    codeFont:str = DEFAULT_FONT
    """代码字体"""

    codeBlockLRDistance:int = 20
    """代码块左右边距"""
    codeBlockUDDistance:int = 20
    """代码块上下边距"""

    formLineDistance:int = 20
    """表格行间距"""
    lineDistance:int = 10
    """行间距"""
    citeDistance:int = 30
    """引用间距"""

    pageLineColor:mdColor = (50,255,255,150)
    """分页竖线颜色"""
    pageLineStyle:mdPageLineStyle = "full_line"
    """
    分页竖线样式
     - full_line 实线
     - dotted_line 虚线
    """

    backGroundDrawFunc:mdBackGroundDrawFunc = DefaultMdBackGroundDraw
    """背景绘制函数"""

    unorderedListDotColor:mdColor = (204,229,255)
    """无序列表前置点颜色"""
    orderedListDotColor:mdColor = (204,229,255)
    """有序列表前置点颜色"""
    orderedListNumberColor:mdColor = (76,0,153)
    """有序列表序号颜色"""

    citeUnderpainting:mdColor = (0,60,120,180)
    """引用底色"""
    citeSplitLineColor:mdColor = (0,102,204,238)
    """引用分割线颜色"""

    codeBlockUnderpainting:mdColor = (0,0,102,180)
    """代码块底色"""
    codeBlockTitleColor:mdColor = (204,229,255)
    """代码块标题颜色"""

    formLineColor:mdColor = (85,255,255)
    """表格分割线颜色"""
    formTextColor:mdColor = (255,255,255)
    """表格文本颜色"""
    formUnderpainting:mdColor = (0,0,0,0)
    """表格底色"""
    formTitleUnderpainting:mdColor = (0,0,0,0)
    """表格标题底色"""

    textColor:mdColor = (255,255,255)
    """文本基础颜色"""
    textGradientEndColor:mdColor = (30,255,255)
    """由普通字体到一级标题时颜色变化的最终色"""
    linkColor:mdColor = (255,187,255)
    """链接颜色"""

    expressionUnderpainting:mdColor = (0,0,102,180)
    """表达式底色"""

    insertCodeUnderpating:mdColor = (0,0,102,180)
    """行中代码底色"""

    idlineColor:mdColor = (120,255,255)
    """行间分割线颜色"""

    expressionTextColor:mdColor = (153,204,255)
    """表达式文本颜色"""
    insertCodeTextColor:mdColor = (153,255,153)
    """行中代码文本颜色"""
    codeBlockTextColor:mdColor = (153,255,153)
    """代码块文本颜色"""

    remarkColor:mdColor = (51,255,246)
    """标题备注颜色"""
    remarkFontSize:int = 15
    """标题备注字体大小"""
    remarkCoordinate:tuple[int,int] = (30,2)
    """标题备注坐标（x为正表示距离左边距离，为负为右边。y为正表示距离上方距离，负数为下方）"""

    decorates:Optional[MDDecorates] = None
    """装饰数据（当启用时，backGroundDrawFunc会被覆盖）"""

    secondFonts:list[str] = DEFAULT_SECOND_FONTS.copy()
    """备用字体列表"""
    
    def Render(
        self,
        text: str,
        title: str = "",
        useImageUrl: bool = False,
        imageUrlGetTimeout: int = 10,
        imagePath: Union[str, Path] = DEFAULT_IMAGE_PATH,
        paint: Optional[str] = None,
        page: int = 1,
        autoPage: bool = False,
        debug: bool = False,
        logoFile: Optional[str] = None,
        showLink:bool = True
    ) -> MdRenderResult:
        """
        将Markdown转化为图片
        text - 要转化的文本
        title - 标题
        fontName - 字体文件名（和后缀）
        useImageUrl - 解析图片url
        imageUrlGetTimeout - 图片url解析超时时间
        imagePath - 图片相对路径所使用的基路径
        paint - 右侧立绘文件名（相对立绘文件夹）
        page - 页码
        autoPage - 是否自动分页（尽可能接近黄金分割比）
        debug - 是否开启调试模式
        logoFile - logo文件名（相对logo文件夹）
        showLink - 是否显示链接（否则只显示连接文字）

        ---

        Markdown额外语法说明
        
        <color=#FFFFFF> 以强制设定文本颜色
        <color=None> 以取消强制设定文本颜色

        !sgexter[对象名,参数1,参数2]绘制自定义对象（以下4个为预设对象）:
        - probar 进度条 [str,float,int,str] [标签,百分比,长度,显示]
        - balbar 平衡条 [str,float,int] [标签,平衡度,长度]
        - chabar 条形统计图[list[[str,int],...],int,int] [对象组[[对象名,对象所占比],...],x宽度,y宽度]
        - card 卡片 [str,str,int,int,str] [标题,内容,x宽度,y宽度,图片绝对文件路径]

        快速渲染图片（使用quick_image）:
        !sgm[图片名]
        !sgm[图片名|比例]
        !sgm[图片名|x比例,y比例]

        ---
        
        返回: MdRenderResult
        """

DEFAULT_STYLE = MdStyle()

P = ParamSpec("P")
def NewMdExterImageDrawer(name:str) -> Callable[[Callable[P,Image.Image]],Callable[P,Image.Image]]:
    ...

def LoadMarkdownStyles(path: Union[str, Path]) -> MdStyle:
    ...

def MdToImage(
        text: str,
        title: str = "",
        useImageUrl: bool = False,
        imageUrlGetTimeout: int = 10,
        imagePath: Union[str, Path] = DEFAULT_IMAGE_PATH,
        paint: Optional[str] = None,
        page: int = 1,
        autoPage: bool = False,
        style: MdStyle = DEFAULT_STYLE,
        debug: bool = False,
        logoFile: Optional[str] = None,
        showLink:bool = True
    ) -> MdRenderResult:
    """
    将Markdown转化为图片
    text - 要转化的文本
    title - 标题
    fontName - 字体文件名（和后缀）
    useImageUrl - 解析图片url
    imageUrlGetTimeout - 图片url解析超时时间
    imagePath - 图片相对路径所使用的基路径
    paint - 右侧立绘文件名（相对立绘文件夹）
    page - 页码
    autoPage - 是否自动分页（尽可能接近黄金分割比）
    style - 风格
    debug - 是否开启调试模式
    logoFile - logo文件名（相对logo文件夹）
    showLink - 是否显示链接（否则只显示连接文字）

    ---

    Markdown额外语法说明
    
    <color=#FFFFFF> 以强制设定文本颜色
    <color=None> 以取消强制设定文本颜色

    !sgexter[对象名,参数1,参数2]绘制自定义对象（以下4个为预设对象）:
     - probar 进度条 [str,float,int,str] [标签,百分比,长度,显示]
     - balbar 平衡条 [str,float,int] [标签,平衡度,长度]
     - chabar 条形统计图[list[[str,int],...],int,int] [对象组[[对象名,对象所占比],...],x宽度,y宽度]
     - card 卡片 [str,str,int,int,str] [标题,内容,x宽度,y宽度,图片绝对文件路径]

    快速渲染图片（使用quick_image）:
    !sgm[图片名]
    !sgm[图片名|比例]
    !sgm[图片名|x比例,y比例]

    ---
    
    返回: MdRenderResult
    """

    ...