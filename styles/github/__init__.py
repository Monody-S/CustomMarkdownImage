# TODO 封包后，改下这里引用路径
from CustomMarkdownRenderer import MdStyle, mdColor
from PIL import Image
from typing import override, Literal

class Style(MdStyle):
	"""仿GitHub样式
	
	Keyword arguments:
	mod -- 模式，暗色模式或者亮色模式
	withoutBg -- 没有背景
	"""
	def __init__(self, mod: Literal['dark', 'light']='dark', withoutBg: bool=False):
		super().__init__()

		self.name = 'GitHub Like'
		"""名称"""
		self.intr = '仿GitHub样式'
		"""简介"""
		self.author = 'Mr.Lee'
		"""作者"""
		self.version = '1.0'
		"""版本号"""

		self.title1FontSize = 2 * 16
		self.title2FontSize = 1.5 * 16
		self.title3FontSize = 1.25 * 16

		if mod == 'dark':self.darkColor()
		else: self.lightColor()

		if withoutBg:
			void = (0, 0, 0, 0)
			self.bgColor = void
			self.citeUnderpainting = void
			self.orderedListDotColor = void
			self.formUnderpainting = void

	@override
	def backGroundDrawFunc(self, xs: int, ys: int) -> Image.Image:
		img = Image.new("RGBA", (xs, ys), self.bgColor)
		return img
	
	def lightColor(self):
		self.bgColor = hexToRgb('#FFFFFF')

		# 文字
		self.textColor = hexToRgb('#1f2328')
		self.textGradientEndColor = self.textColor
		self.idlineColor = hexToRgb('#DFE4E9')

		# 引用
		self.citeUnderpainting = self.bgColor
		self.citeSplitLineColor = hexToRgb('#D1D9E0')

		# 连接
		self.linkColor = hexToRgb('#0969da')

		# 列表
		self.unorderedListDotColor = self.textColor
		self.orderedListDotColor = self.bgColor
		self.orderedListNumberColor = self.textColor

		# 行中式子
		self.expressionTextColor = self.textColor
		self.insertCodeTextColor = self.textColor
		self.codeBlockTextColor = self.textColor
		self.expressionUnderpainting = hexToRgb('#F0F1F2')
		self.insertCodeUnderpating = hexToRgb('#F0F1F2')
		self.codeBlockUnderpainting = hexToRgb('#F6F8FA')

		# 表格
		self.formLineColor = hexToRgb('#D1D9E0')
		self.formTextColor = self.textColor
		self.formUnderpainting = hexToRgb('#FFFFFF')
		self.formTitleUnderpainting = hexToRgb('#F6F8FA')
	
	def darkColor(self):
		"""深色模式"""

		# 背景
		self.bgColor = hexToRgb('#0D1117')

		# 文字
		self.textColor = hexToRgb('#f0f6fc')
		self.textGradientEndColor = self.textColor
		self.idlineColor = hexToRgb('#2F353D')

		# 引用
		self.citeUnderpainting = self.bgColor
		self.citeSplitLineColor = hexToRgb("#3D444D")

		# 连接
		self.linkColor = hexToRgb('#4493f8')

		# 列表
		self.unorderedListDotColor = self.textColor
		self.orderedListDotColor = self.bgColor
		self.orderedListNumberColor = self.textColor

		# 行中式子
		self.expressionTextColor = self.textColor
		self.insertCodeTextColor = self.textColor
		self.codeBlockTextColor = self.textColor
		self.expressionUnderpainting = hexToRgb('#1E242A')
		self.insertCodeUnderpating = hexToRgb('#1E242A')
		self.codeBlockUnderpainting = hexToRgb('#151B23')

		# 表格
		self.formLineColor = hexToRgb('#3D444D')
		self.formTextColor = self.textColor
		self.formUnderpainting = self.bgColor
		self.formTitleUnderpainting = hexToRgb('#151B23')
	

def hexToRgb(hexColor: str) -> mdColor:
	if hexColor.startswith("#"):
		hexColor = hexColor[1:]
	if len(hexColor) == 6:
		return tuple(int(hexColor[i:i + 2], 16) for i in (0, 2, 4))
	elif len(hexColor) == 3:
		return tuple(int(hexColor[i] * 2, 16) for i in range(3))
	else:
		raise ValueError("Invalid hex color format")