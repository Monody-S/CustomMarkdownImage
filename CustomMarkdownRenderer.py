"""
自定义markdown渲染器
"""
from PIL import Image, ImageDraw
from typing import Union,TypeAlias,Literal,ParamSpec
from PIL.ImageFont import FreeTypeFont
from PIL.ImageDraw import ImageDraw as IDW
from fontTools.ttLib import TTFont
from typing import Any,Optional,Callable,Sequence
from pathlib import Path

import requests
import os
import json
import yaml
import math
import copy
import random
import inspect
import importlib

from .Setting import (
    FONT_PATH,
    PAINT_PATH,
    DEFAULT_IMAGE_PATH,
    DEFAULT_FONT,
    DEFAULT_SECOND_FONTS,
    QUICK_IMAGE_PATH,
    IMAGE_DOWNLOAD_PATH,
    LOGO_PATH
)

fileUri:TypeAlias = Union[Path,str]

from dataclasses import dataclass

def FillImage(img1:Image.Image,img2:Image.Image,mode:Literal[0,1,2,3,4,5,6]):
    x,y = img1.size
    match mode:
        case 0:
            img1.paste(img2.resize((x,y)))
        case 1:
            img = img2
            ix,iy = img.size
            for nx in range(0,x+1,ix):
                for ny in range(0,y+1,iy):
                    img1.paste(img,(nx,ny))
        case 2:
            img = img2
            ix,iy = img.size
            xn = 0
            yn = 0
            while xn*(ix+1) < x:
                xn += 1
            while yn*(iy+1) < y:
                yn += 1
            
            k1,k2 = max(1,xn*ix),max(1,(xn+1)*ix)
            if max(k2,x)/min(k2,x) < max(k1,x)/min(k1,x):
                xn += 1
            k1,k2 = max(1,yn*iy),max(1,(yn+1)*iy)
            if max(k2,y)/min(k2,y) < max(k1,y)/min(k1,y):
                yn += 1
            
            ix = math.ceil(x/xn)
            iy = math.ceil(y/yn)
            img = img.resize((ix,iy))
            for nx in range(0,x+1,ix):
                for ny in range(0,y+1,iy):
                    img1.paste(img,(nx,ny))
        case 3:
            ix,iy = img2.size
            img = img2.resize((int(y/iy*ix),y))
            ix,iy = img.size
            for nx in range(0,x+1,ix):
                img1.paste(img,(nx,0))
        case 4:
            ix,iy = img2.size
            img = img2.resize((x,int(x/ix*iy)))
            ix,iy = img.size
            for ny in range(0,y+1,iy):
                img1.paste(img,(0,ny))
        case 5:
            ix,iy = img2.size
            img = img2.resize((int(y/iy*ix),y))
            ix,iy = img.size
            xn = 0
            while xn*(ix+1) < x:
                xn += 1
            
            k1,k2 = max(1,xn*ix),max(1,(xn+1)*ix)
            if max(k2,x)/min(k2,x) < max(k1,x)/min(k1,x):
                xn += 1
            
            ix = math.ceil(x/xn)
            img = img.resize((ix,y))
            for nx in range(0,x+1,ix):
                img1.paste(img,(nx,0))
        case 6:
            ix,iy = img2.size
            img = img2.resize((x,int(x/ix*iy)))
            ix,iy = img.size
            yn = 0
            while yn*(iy+1) < y:
                yn += 1
            
            k1,k2 = max(1,yn*iy),max(1,(yn+1)*iy)
            if max(k2,y)/min(k2,y) < max(k1,y)/min(k1,y):
                yn += 1
            
            iy = math.ceil(y/yn)
            img = img.resize((x,iy))
            for ny in range(0,y+1,iy):
                img1.paste(img,(0,ny))

def ImgResize(x:int,y:int,img:Image.Image,data:dict) -> Image.Image:
    match data["mode"]:
        case 0:
            ...
        case 1:
            rawSize = img.size
            xs1 = int(x*data["xlimit"])
            xs2 = int((y*data["ylimit"])/rawSize[0]*rawSize[1])
            if xs1 > xs2:
                size = (xs2,int(y*data["ylimit"]))
            else:
                size = (xs1,int(xs1/rawSize[0]*rawSize[1]))
            if "min" in data and size[0] < img.size[0]*data["min"]:
                size = (int(size[0]*data["min"]),int(size[1]*data["min"]))
            if "max" in data and size[0] > img.size[0]*data["max"]:
                size = (int(size[0]*data["max"]),int(size[1]*data["max"]))
            img = img.resize(size)
    return img

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

        path = Path(path) if isinstance(path, str) else path

        fid = random.randint(1000000, 9999999)
        fullname = f"{fid}.{self.imageType}"

        if self.imageType == "gif":
            self.image.save(path / fullname, save_all = True, optimize = True , append_images = self.images[1:], duratio = self.gifDuratio * 1000, loop=0)
        
        else:
            self.image.save(path / fullname)
        
        return path / fullname

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

        if not self.gifPage:
            self.playbackSequence = [1]
        else:    
            self.playbackSequence:list[int] = list(range(1,self.gifPage+1)) if not playbackSequence else [int(i) for i in playbackSequence.split()]

            if not self.playbackSequence:
                self.playbackSequence = [1 for i in range(self.gifPage)]

            if len(self.playbackSequence) < self.gifPage:
                for i in range(self.gifPage - len(self.playbackSequence)):
                    self.playbackSequence.append(self.playbackSequence[-1])

        self.__nowPage = None
    
    def GetImage(self, name: str, lock: bool = False) -> Image.Image:

        exter = "" if not self.__nowPage or lock else f"_{self.__nowPage}"
        fname = '.'.join(name.split(".")[0:-1])
        ftype = name.split(".")[-1]

        name = fname + exter + "." + ftype

        if name not in self.imageCache:
            self.imageCache[name] = Image.open(self.imagePath / name)
            
        return self.imageCache[name]
    
    def Draw(self,x:int,y:int,page:Optional[int] = None) -> Image.Image:

        rx,ry = x,y

        self.__nowPage = page
        if not page and self.gifPage:
            self.__nowPage = 1

        oimg = Image.new("RGBA",(x,y))
        bmode = self.backGroundMode
        bdata = self.backGroundData
        cxs1, cys1, cxs2, cys2 = 0, 0, 0, 0

        def Check(key:str,aim:dict) -> bool:
            return key in aim and aim[key]

        match bmode:
            case 0:
                FillImage(oimg,self.GetImage(bdata["img"],lock = Check("lock",bdata)),bdata["mode"])
            case 1:
                corner1 = self.GetImage(bdata["left-up"],lock = Check("lu-lock",bdata))
                corner2 = self.GetImage(bdata["right-up"],lock = Check("ru-lock",bdata))
                corner3 = self.GetImage(bdata["right-down"],lock = Check("rd-lock",bdata))
                corner4 = self.GetImage(bdata["left-down"],lock = Check("ld-lock",bdata))

                cxs1 = max(corner1.width,corner4.width)
                cxs2 = max(corner2.width,corner3.width)
                cys1 = max(corner1.height,corner2.height)
                cys2 = max(corner3.height,corner4.height)

                corner1 = corner1.resize((cxs1,cys1))
                corner2 = corner2.resize((cxs2,cys1))
                corner3 = corner3.resize((cxs2,cys2))
                corner4 = corner4.resize((cxs1,cys2))

                x = max(cxs1+cxs2+1,x)
                y = max(cys1+cys2+1,y)
                oimg = Image.new("RGBA",(x,y))

                oimg.paste(corner1,(0,0))
                oimg.paste(corner2,(x-cxs2,0))
                oimg.paste(corner3,(x-cxs2,y-cys2))
                oimg.paste(corner4,(0,y-cys2))

                img = self.GetImage(bdata["up"],lock = Check("u-lock",bdata))
                tempImg = Image.new("RGBA",(x-cxs1-cxs2,cys1))
                FillImage(tempImg,img,{0:0,1:3,2:5}[bdata["ud-mode"]]) # type: ignore
                oimg.paste(tempImg,(cxs1,0))

                img = self.GetImage(bdata["down"],lock = Check("d-lock",bdata))
                tempImg = Image.new("RGBA",(x-cxs1-cxs2,cys2))
                FillImage(tempImg,img,{0:0,1:3,2:5}[bdata["ud-mode"]]) # type: ignore
                oimg.paste(tempImg,(cxs1,y-cys2))

                img = self.GetImage(bdata["left"],lock = Check("l-lock",bdata))
                tempImg = Image.new("RGBA",(cxs1,y-cys1-cys2))
                FillImage(tempImg,img,{0:0,1:4,2:6}[bdata["lr-mode"]]) # type: ignore
                oimg.paste(tempImg,(0,cys1))

                img = self.GetImage(bdata["right"],lock = Check("r-lock",bdata))
                tempImg = Image.new("RGBA",(cxs2,y-cys1-cys2))
                FillImage(tempImg,img,{0:0,1:4,2:6}[bdata["lr-mode"]]) # type: ignore
                oimg.paste(tempImg,(x-cxs2,cys1))

                img = self.GetImage(bdata["middle"],lock = Check("m-lock",bdata))
                tempImg = Image.new("RGBA",(x-cxs1-cxs2,y-cys1-cys2))
                FillImage(tempImg,img,bdata["middle-mode"])
                oimg.paste(tempImg,(cxs1,cys1))

        for decorates in self.bottomDecorates["left-up"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(0,0))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.bottomDecorates["left"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(0,int(ky/2-img.size[1]/2)))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.bottomDecorates["left-down"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(0,ky-img.size[1]))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.bottomDecorates["up"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(int(kx/2-img.size[0]/2),0))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.bottomDecorates["down"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(int(kx/2-img.size[0]/2),ky-img.size[1]))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.bottomDecorates["right-up"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(kx-img.size[0],0))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.bottomDecorates["right"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(kx-img.size[0],int(ky/2-img.size[1]/2)))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.bottomDecorates["right-down"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(kx-img.size[0],ky-img.size[1]))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.bottomDecorates["middle"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(int(kx/2-img.size[0]/2),int(ky/2-img.size[1]/2)))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))
        
        if rx != x:
            oimg = oimg.resize((rx,ry))
        
        self.__nowPage = None
        return oimg
    
    def DrawTop(self,x:int,y:int,page:Optional[int] = None) -> Image.Image:

        rx,ry = x,y

        self.__nowPage = page
        if not page and self.gifPage:
            self.__nowPage = 1

        def Check(key:str,aim:dict) -> bool:
            return key in aim and aim[key]

        oimg = Image.new("RGBA",(x,y))
        bmode = self.backGroundMode
        bdata = self.backGroundData
        cxs1, cys1, cxs2, cys2 = 0, 0, 0, 0

        match bmode:
            case 0:
                ...
            case 1:
                corner1 = self.GetImage(bdata["left-up"],lock = Check("lu-lock",bdata))
                corner2 = self.GetImage(bdata["right-up"],lock = Check("ru-lock",bdata))
                corner3 = self.GetImage(bdata["right-down"],lock = Check("rd-lock",bdata))
                corner4 = self.GetImage(bdata["left-down"],lock = Check("ld-lock",bdata))

                cxs1 = max(corner1.width,corner4.width)
                cxs2 = max(corner2.width,corner3.width)
                cys1 = max(corner1.height,corner2.height)
                cys2 = max(corner3.height,corner4.height)

                x = max(cxs1+cxs2+1,x)
                y = max(cys1+cys2+1,y)
                oimg = Image.new("RGBA",(x,y))

        for decorates in self.topDecorates["left-up"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(0,0))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.topDecorates["left"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(0,int(ky/2-img.size[1]/2)))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.topDecorates["left-down"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(0,ky-img.size[1]))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.topDecorates["up"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(int(kx/2-img.size[0]/2),0))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.topDecorates["down"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(int(kx/2-img.size[0]/2),ky-img.size[1]))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.topDecorates["right-up"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(kx-img.size[0],0))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.topDecorates["right"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(kx-img.size[0],int(ky/2-img.size[1]/2)))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.topDecorates["right-down"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(kx-img.size[0],ky-img.size[1]))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))

        for decorates in self.topDecorates["middle"]:
            kx,ky = x,y
            icMode = False
            if bmode == 1 and "include" in decorates and decorates["include"]:
                kx, ky = max(x - cxs1 - cxs2, 1), max(y - cys1 - cys2, 1)
                icMode = True
            img = ImgResize(kx,ky,self.GetImage(decorates["img"],lock = Check("lock",decorates)),decorates)
            k = Image.new("RGBA",(kx,ky))
            k.paste(img,(int(kx/2-img.size[0]/2),int(ky/2-img.size[1]/2)))
            oimg.alpha_composite(k,(cxs1, cys1) if icMode else (0,0))
        
        if rx != x:
            oimg = oimg.resize((rx,ry))
        
        return oimg

class MixFont(FreeTypeFont):
    def __init__(
            self, 
            font=None, 
            size=10, 
            index=0, 
            encoding="", 
            layout_engine=None,
            second_fonts: list[str] = []
        ) -> None:
        super().__init__(font, size, index, encoding, layout_engine)
        self.seconde_fonts = {second_font:FreeTypeFont(second_font,size) for second_font in second_fonts}
        self.font_dict = TTFont(font)
        self.font_dict = self.font_dict['cmap'].tables[0].ttFont.getBestCmap().keys() #type: ignore

        def _GetD(font:str) -> TTFont:
            k = TTFont(font)
            return k['cmap'].tables[0].ttFont.getBestCmap().keys() #type: ignore

        self.seconde_font_dict = {
            second_font:_GetD(second_font)
            for second_font in second_fonts
        }
    
    def ChoiceFont(self,char:str) -> FreeTypeFont:

        k = ord(char)

        if k in self.font_dict:
            return self
        
        for second_font in self.seconde_font_dict:
            if k in self.seconde_font_dict[second_font]:
                return self.seconde_fonts[second_font]
        
        return self

    def CheckChar(self,char:str) -> bool:
        return ord(char) in self.font_dict

    def GetSize(self,text) -> tuple[int,int]:

        outObj = self
        rawObj = self

        if rawObj not in size_cache:
            size_cache[rawObj] = {}
        
        if text in size_cache[rawObj]:
            return size_cache[rawObj][text]

        if not text:
            size_cache[rawObj][text] = (0,0)
            return (0,0)
        for char in text:
            try:
                if not outObj.CheckChar(char):
                    outObj = outObj.ChoiceFont(char)
                    break
            except:
                pass
        temp = outObj.getbbox(text)
        rt = (int(temp[2]-temp[0]), int(temp[3]-temp[1]))

        #print(size_cache)
        size_cache[rawObj][text] = rt
        return rt

class ImageDrawPro(ImageDraw.ImageDraw):
    def __init__(
            self, im, 
            lock_color = None, 
            blod_mode = None, 
            delete_line_mode = None,
            under_line_mode = None,
            mode=None
        ):
        super().__init__(im, mode)
        self.text_lock_color = lock_color
        self.text_blod_mode = blod_mode
        self.delete_line_mode = delete_line_mode
        self.under_line_mode = under_line_mode
    
    def text(
            self,
            xy,
            text,
            fill=None,
            font:Optional[MixFont]=None,
            use_lock_color = True,
            use_blod_mode = True,
            use_delete_line_mode = True,
            use_under_line_mode = True,
            *args,
            **kwargs,
        ):

        if font is None:
            raise SyntaxError("font为必选项")

        useFont: Union[MixFont,FreeTypeFont] = font

        for char in text:
            if not useFont.CheckChar(char):
                useFont = useFont.ChoiceFont(char)
                break

        if self.text_lock_color != None and use_lock_color:
            fill = self.text_lock_color
        
        super().text(xy,text,fill,font,*args,**kwargs)
        if self.text_blod_mode and use_blod_mode:
            for a,b in [(-1,0),(1,0)]:
                super().text((xy[0]+a,xy[1]+b),text,fill,font,*args,**kwargs)
        
        if self.delete_line_mode or self.under_line_mode:
            xs,ys = font.GetSize(text)

        if self.delete_line_mode and use_delete_line_mode:
            super().line((xy[0],xy[1]+int(font.size/2),xy[0]+xs,xy[1]+int(font.size/2)),fill,int(font.size/10)+1)

        if self.under_line_mode and use_under_line_mode:
            super().line((xy[0],xy[1]+font.size+2,xy[0]+xs,xy[1]+font.size+2),fill,int(font.size/10)+1)

def GetArgs(args:str)->tuple[list[Any],dict[str,Any]]:
    args+=","
    args1 = []
    args2 = {}
    pmt = ""

    def GetOneArg(arg:str):
        if arg[0]=="[" and arg[-1]=="]":
            args = []
            pmt = ""
            deep = 0
            string = False
            pre = ""
            for i in arg[1:-1]+",":
                if i == "]" and not string:
                    deep -= 1
                if i == "\"" and pre != "\\":
                    string = not string

                if i == "," and deep==0 and not string:
                    args.append(pmt.strip())
                    pmt = ""
                    pre = ""
                    continue
                elif i == "[" and not string:
                    deep += 1
                
                pmt += i
                pre = i
            return [GetOneArg(i) for i in args]
        if arg[0] == '"' and arg[-1] == '"':
            return arg[1:-1]
        if arg in ['True','true']:
            return True
        if "." in arg:
            return float(arg)
        return int(arg)
                

    deep = 0
    pre = ""
    string = False
    for i in args:

        if i == "]" and not string:
            deep -= 1
        
        if i == "\"" and pre != "\\":
            string = not string

        if i == "," and deep==0 and not string:
            pmt = pmt.strip()
            if pmt[0] not in ['"',"[",] and pmt not in ['True','true','False','false'] and not pmt[0].isdigit():
                args2[pmt.split('=')[0].strip()] = "=".join(pmt.split('=')[1:]).strip()
            else:
                args1.append(pmt)
            pmt = ""
            pre = ""
            continue
        elif i == "[" and not string:
            deep += 1
        
        pmt += i
        pre = i
    
    args1 = [GetOneArg(i) for i in args1]
    for key in args2:
        args2[key] = GetOneArg(args2[key])
    
    return (args1,args2)

size_cache:dict[MixFont,dict[str,tuple[int,int]]] = {}
mdColor:TypeAlias = Union[tuple[int,int,int],tuple[int,int,int,int]]
mdBackGroundDrawFunc:TypeAlias = Callable[[int,int],Image.Image]

def DefaultMdBackGroundDraw(xs:int,ys:int) -> Image.Image:
    image = Image.new("RGBA",(xs,ys),color=(0,0,0))

    drawUnder = ImageDrawPro(image)
    for i in range(11):
        drawUnder.rectangle((0,i*int(ys/10),xs,(i+1)*int(ys/10)),(52-3*i,73-4*i,94-2*i))

    imgUnder2 = Image.new("RGBA",(xs,ys),color=(0,0,0,0))
    drawUnder2 = ImageDrawPro(imgUnder2)
    for i in range(int(xs*ys/20000)+1):
        temp = random.randint(1,5)
        temp1 = random.randint(20,40)
        temp2 = random.randint(10,80)
        temp3 = random.randint(0,xs-temp*4)
        temp4 = random.randint(-50,ys)
        for x in range(3):
            for y in range(temp1):
                if random.randint(1,2)==2:
                    continue
                drawUnder2.rectangle((temp3+(temp+2)*x,temp4+(temp+2)*y,temp3+(temp+2)*x+temp,temp4+(temp+2)*y+temp),(0,255,180,temp2))

    image.alpha_composite(imgUnder2)

    return image

mdPageLineStyle:TypeAlias = Literal["full_line","dotted_line"]

from dataclasses import dataclass, field

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

    # mdBackGroundDrawFunc 可以删了
    # backGroundDrawFunc:mdBackGroundDrawFunc = DefaultMdBackGroundDraw
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

    secondFonts:list[str] = field(default_factory=lambda: DEFAULT_SECOND_FONTS.copy())
    """备用字体列表"""

    def GetMixFont(self, mainFont:str,size:int,secondFonts:Optional[list[str]] = None) -> MixFont:

        if secondFonts is None:
            secondFonts = self.secondFonts

        if (path := self.path / "fonts").exists():
            key = str(hash(str([self.name, mainFont, secondFonts, size])))
        else:
            key = str(hash(str([mainFont, secondFonts, size])))
        
        global fontCache

        if key in fontCache:
            return fontCache[key]
        
        path1 = path if path.exists() else FONT_PATH
        path2 = FONT_PATH

        files1 = os.listdir(path1)

        fontCache[key] = MixFont(
            (path1 / mainFont).as_posix() if mainFont in files1 else (path2 / mainFont).as_posix(),
            size,
            second_fonts=[
                (path1 / secondFont).as_posix() if secondFont in files1 else (path2 / secondFont).as_posix()
                for secondFont in secondFonts
            ]
        )
        return fontCache[key]
    
    def backGroundDrawFunc(xs: int, ys: int) -> Image.Image:
        """背景绘制函数"""
        return DefaultMdBackGroundDraw(xs, ys)

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
        return MdToImage(
            text = text,
            title = title,
            useImageUrl = useImageUrl,
            imageUrlGetTimeout = imageUrlGetTimeout,
            imagePath = imagePath,
            paint = paint,
            page = page,
            autoPage = autoPage,
            debug = debug,
            logoFile = logoFile,
            showLink = showLink,
            style = self
        )

DEFAULT_STYLE = MdStyle()

class MdExterImageDrawer:
    def __init__(self,drawer:Callable[...,Image.Image]):
        self.drawer = drawer
    def __call__(
        self,
        *args: Any,
        nowf: MixFont,
        style: MdStyle,
        lockColor,
        **kwds: Any
    ) -> Image.Image:
        kwds["nowf"] = nowf
        kwds["style"] = style
        kwds["lockColor"] = lockColor
        useVars = inspect.getfullargspec(self.drawer).args
        return self.drawer(
            *args,**{key:kwds[key] for key in kwds if key in useVars}
        )
    
extendFuncs: dict[str, MdExterImageDrawer] = {}

P = ParamSpec("P")

def NewMdExterImageDrawer(name:str) -> Callable[[Callable[P,Image.Image]],Callable[P,Image.Image]]:
    def catch(func:Callable[P,Image.Image]) -> Callable[P,Image.Image]:
        extendFuncs[name] = MdExterImageDrawer(func)
        return func
    return catch

def ColorChange(color:Sequence[int],num:float)->tuple:
    """颜色按比例改变"""
    return (int(color[0]*num),int(color[1]*num),int(color[2]*num))

@NewMdExterImageDrawer("probar")
def MakeProbar(
        label:str,
        pro: float,
        size: int,
        show: str,
        nowf: MixFont,
        style: MdStyle = DEFAULT_STYLE
    )->Image.Image:
    
    tempFs = nowf.GetSize(label)
    temp = int(nowf.size/6)+1
    halfTemp = int(temp/2)
    exterImage = Image.new("RGBA",(tempFs[0]+temp*3+size, int(nowf.size+temp*2)),color=(0,0,0,0))
    drawEm = ImageDraw.Draw(exterImage)
    for i in range(11):
        drawEm.rectangle((0,i*int((exterImage.size[1])/10),exterImage.size[0],(i+1)*int((exterImage.size[1])/10)),(40+80-8*i,40+80-8*i,40+80-8*i))
    drawEm.text((temp-1,halfTemp),label,"#00CCCC",nowf)
    drawEm.text((temp+1,halfTemp),label,"#CCFFFF",nowf)
    drawEm.text((temp,halfTemp),label,"#33FFFF",nowf)
    drawEm.rectangle((temp*2+tempFs[0],temp,temp*2+tempFs[0]+size,temp+nowf.size),(0,0,0))
    for i in range(20):
        drawEm.rectangle((temp*2+tempFs[0]+int(size*pro/20*i),temp,temp*2+tempFs[0]+int(size*pro/20*(i+1)),temp+nowf.size),(int(78+78*((i/20)**3)),int(177+177*((i/20)**3)),int(177+177*((i/20)**3))))
    drawEm.text((temp*3+tempFs[0],halfTemp),show,(0,102,102),nowf)
    return exterImage

@NewMdExterImageDrawer("balbar")
def MakeBalbar(
        label: str,
        bal: float,
        size: int,
        nowf: MixFont,
        style: MdStyle = DEFAULT_STYLE
    )->Image.Image:
    
    tempFs = nowf.GetSize(label)
    temp = int(nowf.size/6)+1
    halfTemp = int(temp/2)
    exterImage = Image.new("RGBA",(tempFs[0]+temp*3+size, int(nowf.size+temp*2)),color=(0,0,0,0))
    drawEm = ImageDraw.Draw(exterImage)
    for i in range(11):
        drawEm.rectangle((0,i*int((exterImage.size[1])/10),exterImage.size[0],(i+1)*int((exterImage.size[1])/10)),(40+80-8*i,40+80-8*i,40+80-8*i))
    drawEm.text((temp-1,halfTemp),label,"#00CCCC",nowf)
    drawEm.text((temp+1,halfTemp),label,"#CCFFFF",nowf)
    drawEm.text((temp,halfTemp),label,"#33FFFF",nowf)
    drawEm.rectangle((temp*2+tempFs[0],temp,temp*2+tempFs[0]+size,temp+nowf.size),(0,0,0))
    for i in range(20):
        drawEm.rectangle((temp*2+tempFs[0]+int(size*bal/20*i),temp,temp*2+tempFs[0]+int(size*bal/20*(i+1)),temp+nowf.size),(int(78+78*((i/20)**3)),int(177+177*((i/20)**3)),int(177+177*((i/20)**3))))
        drawEm.rectangle((temp*2+tempFs[0]+size-int(size*(1-bal)/20*(i+1)),temp,temp*2+tempFs[0]+size-int(size*(1-bal)/20*i),temp+nowf.size),(int(177+177*((i/20)**3)),int(21+21*((i/20)**3)),int(21+21*((i/20)**3))))
    drawEm.line((temp*2+tempFs[0]+int(size*bal),temp-halfTemp,temp*2+tempFs[0]+int(size*bal),temp+nowf.size+halfTemp),(255,255,255),5)
    if bal == 0.5:
        drawEm.text((temp*2+tempFs[0]+int(size*bal)+3,halfTemp),"+0%",(102,0,0),nowf)
    elif bal > 0.5:
        if bal == 1:
            text = "+∞%"
        else:
            text = f"+{round(bal/(1-bal)*100-100,2)}%"
        drawEm.text((temp*2+tempFs[0]+int(size*bal)-nowf.GetSize(text)[0]-3,halfTemp),text,(0,102,102),nowf)
    elif bal < 0.5:
        if bal == 0:
            text = "-∞%"
        else:
            text = f"-{round((1-bal)/bal*100-100,2)}%"
        drawEm.text((temp*2+tempFs[0]+int(size*bal)+3,halfTemp),text,(102,0,0),nowf)

    return exterImage

@NewMdExterImageDrawer("chabar")
def MakeChabar(
        objs: list[tuple[str,int]],
        xSize: int,
        ySize: int,
        nowf: MixFont,
        style: MdStyle = DEFAULT_STYLE
    )->Image.Image:
    
    nums = [nowf.GetSize(str(i[1])) for i in objs]
    strs = [nowf.GetSize(i[0]) for i in objs]
    space = int(xSize/(len(objs)*2+1))
    halfSpace = int(space/2)

    exterImage = Image.new(
        "RGBA",
        (
            int(max([i[0] for i in nums])+xSize+max(strs[-1][0]/2-space*1.5,0))+5,
            int(ySize+nums[0][1]/2+max([i[1] for i in strs]))+5
        ),
        color=(0,0,0,0)
    )
    drawEm = ImageDraw.Draw(exterImage)

    lineY = int(ySize+nums[0][1]/2)-5
    lineX = int(max([i[0] for i in nums])+5)

    maxM = max([i[1] for i in objs])

    for i in range(len(objs)):
        X = space*(1+i*2)
        Y = int(ySize*0.8*objs[i][1]/maxM)

        drawEm.line((lineX,lineY-Y,lineX+X+space,lineY-Y),ColorChange(style.textGradientEndColor,0.6),1)
        drawEm.text((lineX-nums[i][0]-5,lineY-Y-int(nums[i][1]/2)),str(objs[i][1]),style.textColor,nowf)
        drawEm.text((int(lineX+X+space/2-strs[i][0]/2),lineY+5),objs[i][0],style.textColor,nowf)
        drawEm.rectangle((lineX+X,lineY-Y,lineX+X+space,lineY),style.textGradientEndColor)
        drawEm.text((lineX+X+halfSpace-int(nums[i][0]/2),lineY-Y-nowf.size-2),str(objs[i][1]),style.textColor,nowf)

    drawEm.line((lineX,lineY,lineX+xSize,lineY),style.textColor,1)
    drawEm.polygon([(lineX+xSize,lineY),(lineX+xSize-3,lineY-3),(lineX+xSize-3,lineY+3)],style.textColor)
    drawEm.line((lineX,lineY-ySize,lineX,lineY),style.textColor,1)
    drawEm.polygon([(lineX,lineY-ySize),(lineX-3,lineY-ySize+3),(lineX+3,lineY-ySize+3)],style.textColor)

    return exterImage

@NewMdExterImageDrawer("card")
def MakeCard(
        title: str,
        text: str,
        xSize: int,
        ySize: int,
        file: str,
        nowf: MixFont,
        style: MdStyle = DEFAULT_STYLE
    ) -> Image.Image:
        """创建卡片"""
        if xSize < ySize:
            raise ValueError("xSize必须比ySize大")
        im = Image.open(file)
        back = Image.new("RGBA",(xSize,ySize),(0,0,0))
        d = ImageDrawPro(back)

        im = im.resize((ySize-8,ySize-8))
        d.rectangle((0,0,xSize,ySize),(27, 26, 85))
        d.rectangle((0,0,ySize,ySize),(83, 92, 145))
        d.rectangle((2,2,ySize-2,ySize-2),(83, 92, 145))

        back.paste(im,(4,4))
        
        d.text((ySize + 8,8),title,(30,255,255),nowf)
        x,y = ySize + 8, 8 + nowf.size + 8
        for i in text:
            s = nowf.GetSize(i)
            if x + s[0] > xSize or i == "\n":
                x = ySize + 8
                y += nowf.size + 8
            d.text((x,y),i,(255,255,255),nowf)
            x += s[0]

        return back


def DrawHText(obj:IDW,font:MixFont,text:str,color,xy:tuple[int,int])->None:
    for a,b in [(-1,0),(1,0),(0,0)]:
        obj.text((xy[0]+a,xy[1]+b),text,color,font)

fontCache = {}
def GetMixFont(mainFont:str,secondFonts:list[str],size:int) -> MixFont:
    key = str(hash(str([mainFont,secondFonts,size])))
    global fontCache

    if key in fontCache:
        return fontCache[key]

    fontCache[key] = MixFont(f"data/fonts/{mainFont}",size,second_fonts=[f"data/fonts/{secondFont}" for secondFont in secondFonts])
    return fontCache[key]

COLOR_KEYS = [
    "pageLineColor",
    "unorderedListDotColor",
    "orderedListDotColor",
    "orderedListNumberColor",
    "citeUnderpainting",
    "citeSplitLineColor",
    "codeBlockUnderpainting",
    "codeBlockTitleColor",
    "formLineColor",
    "textColor",
    "textGradientEndColor",
    "linkColor",
    "expressionUnderpainting",
    "insertCodeUnderpating",
    "idlineColor",
    "expressionTextColor",
    "insertCodeTextColor",
    "codeBlockTextColor",
    "remarkColor",
    "formTextColor",
    "formUnderpainting",
    "formTitleUnderpainting",
]

defaultHeaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:104.0) Gecko/20100101 Firefox/104.0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'
}

DEFAULT_STYLE = MdStyle()
MARKDOWN_STYLE_PATH = Path("./data/MarkdownStyles")

def LoadMarkdownStyles(style: Union[str, Path], *args: Any, **kwargs: Any) -> MdStyle:
    styleRoot: Path
    if isinstance(style, str):
        # 默认去 styles 文件夹下寻找
        findPath = (Path(__file__).parent / 'styles' / style)
        if findPath.exists() and findPath.is_dir():
            styleRoot = findPath
        else:
            styleRoot = Path(style)
    else:
        styleRoot = style

    # python样式
    if (styleRoot / "__init__.py").exists():return loadMarkdownStylesPython(styleRoot, args, kwargs)
    
    # json样式
    if args or kwargs:
        raise ValueError("json style dont support args and kwargs")
    return loadMarkdownStylesJson(styleRoot)

def loadMarkdownStylesPython(path: Path, args: list[Any], kwargs: dict[str,Any]) -> MdStyle:
    style = importlib.import_module(pathToModuleName(path.resolve()))
    mdstyle = getattr(style, "Style", None)
    if not mdstyle:
        raise ValueError(f"Style not found in {path.as_posix()}")
    if not issubclass(mdstyle, MdStyle):
        raise ValueError(f"Style is not MdStyle in {path.as_posix()}")
    return mdstyle(*args, **kwargs)

def loadMarkdownStylesJson(path: Path) -> MdStyle:
    elements = loadJson(path, "elements")
    setting = loadJson(path, "setting")

    items: dict[str, Any] = {key:tuple(setting[key]) if key in COLOR_KEYS else setting[key] for key in setting}

    if elements["enable"]:
        decorates = MDDecorates(
            elements["background"]["mode"],
            elements["background"]["data"],
            elements["decorates"]["top"],
            elements["decorates"]["bottom"],
            path,
            elements["page"] if "page" in elements else None,
            elements["duratio"] if "duratio" in elements else 0.5,
            elements["playbackSequence"] if "playbackSequence" in elements else None,
        )
        items["decorates"] = decorates

    return MdStyle(**items,path = path)

def loadJson(rootPath: Path, name: str)-> Any:
    loadMap = {
        'yml': lambda file: yaml.load(file, yaml.FullLoader),
        'yaml': lambda file: yaml.load(file, yaml.FullLoader),
        'json': lambda file: json.load(file),
    }
    for extension, loader in loadMap.items():
        if (rootPath / f"{name}.{extension}").exists():
            with open(rootPath / f"{name}.{extension}", 'r', encoding='utf-8') as file:
                return loader(file)
            
    raise FileNotFoundError(f"File {name} not found in {rootPath.as_posix()} with extensions {list(loadMap.keys())}")

def pathToModuleName(path: Path) -> str:
    """转换路径为模块名(借鉴于nb)"""
    rel_path = path.resolve().relative_to(Path.cwd().resolve())
    return ".".join(rel_path.parts[:-1] + (rel_path.stem,))

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

    imagePath = imagePath if isinstance(imagePath, Path) else Path(imagePath)

    font: MixFont = style.GetMixFont(style.font, style.fontSize)
    """正文字体"""
    fontG: MixFont = style.GetMixFont(style.expressionFont, int(style.fontSize*style.expressionFontSizeRate))
    """表达式字体"""
    fontC: MixFont = style.GetMixFont(style.codeFont, style.codeBlockFontSize)
    """代码字体"""
    font1: MixFont = style.GetMixFont(style.titleFont, style.title3FontSize)
    """一级标题字体"""
    font1G: MixFont = style.GetMixFont(style.expressionFont, int(style.title3FontSize*style.expressionFontSizeRate))
    """一级标题表达式字体"""
    font2: MixFont = style.GetMixFont(style.titleFont, style.title2FontSize)
    """二级标题字体"""
    font2G: MixFont = style.GetMixFont(style.expressionFont, int(style.title2FontSize*style.expressionFontSizeRate))
    """二级标题表达式字体"""
    font3: MixFont = style.GetMixFont(style.titleFont, style.title1FontSize)
    """三级标题字体"""
    font3G: MixFont = style.GetMixFont(style.expressionFont, int(style.title1FontSize*style.expressionFontSizeRate))
    """三级标题表达式字体"""
    fontR: MixFont = style.GetMixFont(style.font, style.remarkFontSize)
    """备注字体"""

    rb: int = style.rd
    """右边距"""
    lb: int = style.ld
    """左边距"""
    ub: int = style.ud
    """上边距"""
    db: int = style.dd
    """下边距"""

    maxX: int = style.xSizeMax
    """X轴单行元素最大长度"""

    nmaxX: int = 0
    """当前行最大长度"""
    xidx: int = 0
    """当前行索引"""
    yidx: int = 1
    """行索引"""
    nx: int = 0
    """当前x坐标"""
    ny: int = 0
    """当前y坐标"""
    ys: int = 0
    """当前y大小"""
    nmaxh: int = 0
    """当前行最大高度"""
    nowf: MixFont = font
    """当前字体"""
    fontK: MixFont = nowf
    """前字体"""
    hs: list[int] = []
    """当前行高度列表"""

    textS: int = len(text)
    """文本长度"""

    bMode: bool = False
    """表达式模式"""
    bMode2: bool = False
    """行中代码模式"""
    lMode: bool = False
    """删除线模式"""
    codeMode: bool = False
    """代码块模式"""
    linkMode: bool = False
    """链接模式"""
    yMode: bool = False
    """引用模式"""
    textMode: bool = False
    """纯文本模式（？）"""


    codeLb: int = style.codeBlockLRDistance
    """代码块左右边距"""
    codeUb: int = style.codeBlockUDDistance
    """代码块上下边距"""
    citeNum: int = 0
    """引用数量"""

    formLineSpace: int = style.formLineDistance
    """表格行间距"""
    lineSpace: int = style.lineDistance
    """行间距"""

    halfLineSpace: int = lineSpace//2
    """半行间距"""
    halfFormLineSpace: int = formLineSpace//2
    """半表格行间距"""

    forms: list[dict] = []
    """表格列表"""
    formIdx: int = -1
    """表格索引"""

    images: list[dict[str, Any]] = []
    """图片列表"""
    dldImageNum: int = 0
    """下载图片数量"""

    isImage: bool = False
    """是否为图片"""
    nowImage: Optional[Image.Image] = None
    """当前图片"""
    sgImages: list[str] = os.listdir(QUICK_IMAGE_PATH) if QUICK_IMAGE_PATH else []
    """快速图片列表"""
    drawId = random.randint(10000000,99999999)
    """绘制ID（随机数）"""

    skips = []
    """跳过列表"""
    linkbegins = []
    """链接开始列表"""
    linkends = []
    """链接结束列表"""

    lockColor = None
    """锁定颜色"""
    colors = []
    """颜色列表"""

    debugs = []
    """调试列表"""

    idx = -1
    """当前索引"""

    dr = 0
    """这是什么"""

    Gfonts = [
        fontG,
        font1G,
        font2G,
        font3G
    ]

    def GetGFont(font:MixFont) -> MixFont:
        return font1G if font == font1 \
        else font2G if font == font2 \
        else font3G if font == font3 \
        else fontG

    while idx<textS-1:
        isImage = False
        nowObjH = nowf.size
        idx += 1
        i = text[idx]
        xidx += 1
        size = nowf.GetSize(i)
        xs,ys = size[0],size[1]

        if idx in skips:
            continue
        if idx in linkends:
            continue

        if xidx == 1 and not codeMode and i == " ":
            while idx<textS and text[idx] == " ":
                idx += 1
            idx -= 1
            xidx = 0
            continue

        if not textMode and i == "#" and not codeMode:
            if idx+1<textS and text[idx+1]=="#":
                if idx+2<=textS and text[idx+2]=="#":
                    idx += 2
                    nowf = font1
                else:
                    idx += 1
                    nowf = font2
            else:
                nowf = font3
            while idx+1<textS and text[idx+1]==" ":
                idx += 1
            continue
        elif not textMode and i in ["*","-","+"] and idx+1<textS and text[idx+1] == " " and not codeMode:
            idx += 1
            dr = nmaxh
            nx += nmaxh
            while idx+1<textS and text[idx+1]==" ":
                idx += 1
            continue
        elif not textMode and i.isdigit() and not codeMode:
            tempIdx = idx-1
            flag = False
            number = ""
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx+=1
                if text[tempIdx].isdigit():
                    number+=text[tempIdx]
                elif text[tempIdx] == ".":
                    flag = True
                    break
                else:
                    break
            if flag:
                idx = tempIdx
                nx += 30
                while idx+1<textS and text[idx+1]==" ":
                    idx += 1
                continue
            textMode = True
        elif not textMode and i==">" and not codeMode:
            citeNum = 1
            while idx+1<textS and text[idx+1]==">":
                citeNum += 1
                idx += 1
            while idx+1<textS and text[idx+1]==" ":
                idx += 1
            nx += 30*(citeNum-1)+5
            continue
        elif not textMode and idx+2 <= textS and text[idx:idx+3] in ["```","~~~"]:
            ny+=codeUb
            nx+=codeLb
            while idx<textS-1 and text[idx+1]!="\n":
                idx+=1
            if not codeMode:
                fontK = nowf
                nowf = fontC
            else:
                nowf = fontK
            codeMode = not codeMode
            #idx+=1
            continue
        elif not textMode and i == "|" and not codeMode:
            tempIdx = idx-1
            lText = ""
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx += 1
                lText += text[tempIdx]
            
            tempIdx += 1
            lText2 = ""
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx += 1
                lText2 += text[tempIdx]
            
            lText = lText.strip()
            lText2 = lText.strip()

            temp1 = lText.count("|")
            temp2 = lText2.count("|")
            exterX = temp1*formLineSpace
            if len(lText) and len(lText2) and lText[0] == lText[-1] == lText2[0] == lText2[-1] == "|" and temp1 == temp2 and temp1 >= 2 and exterX < maxX:
                form = [lText.split("|")[1:-1]]

                while True:

                    preIdx = tempIdx
                    tempIdx += 1
                    tempText = ""

                    if tempIdx+1 >= textS or text[tempIdx+1] != "|":
                        break

                    while tempIdx<textS-1 and text[tempIdx+1]!="\n":
                        tempIdx += 1
                        tempText += text[tempIdx]

                    temp = tempText.count("|")
                    if not( tempText[0]==tempText[-1]=="|" and temp>=2):
                        tempIdx = preIdx
                        break

                    form.append(tempText.split("|")[1:-1])
                
                formHeadNum = len(form[0])
                formSize = []
                for ii in range(len(form)):

                    formNowLNum = len(form[ii])

                    if formNowLNum<formHeadNum:
                        form[ii] = form[ii]+[""]*(formHeadNum-formNowLNum)
                    if formNowLNum>formHeadNum:
                        form = form[0:formHeadNum]

                    formSize.append([sum([font.GetSize(j)[0] for j in i]) for i in form[ii]])

                formRow = len(form)
                colunmSizes = [[0,99999]]+sorted([[max([formSize[deep][i] for deep in range(formRow)]),i] for i in range(formHeadNum)],key=lambda x:x[0])
                maxIdx = len(colunmSizes)-1

                if not(font.size*len(colunmSizes)+exterX > maxX):

                    while sum([i[0] for i in colunmSizes])+exterX > maxX:
                        exceed = sum([i[0] for i in colunmSizes])+exterX-maxX
                        sizeIdx = len(colunmSizes)-1

                        while colunmSizes[sizeIdx-1][0] == colunmSizes[sizeIdx][0]:
                            sizeIdx -= 1
                        
                        temp = math.ceil(min(exceed/(maxIdx-sizeIdx+1),colunmSizes[sizeIdx][0]-colunmSizes[sizeIdx-1][0]))
                        for ii in range(sizeIdx,maxIdx+1):
                            colunmSizes[ii][0] = colunmSizes[ii][0] - temp
                    
                    colunmSizes=([i[0] for i in sorted(colunmSizes[1:],key=lambda x:x[1])])
                    rowSizes = []

                    for ii in range(formRow):

                        nMaxRowSize = 0
                        
                        for j in range(formHeadNum):

                            tempRowSize = font.size
                            formNx = 0
                            formTextIdx = -1
                            formText = form[ii][j]
                            formTextSize = len(formText)
                            
                            while formTextIdx+1<formTextSize:

                                formTextIdx += 1
                                char = formText[formTextIdx]
                                formCharX = font.GetSize(char)[0]

                                if formNx+formCharX > colunmSizes[j]:
                                    tempRowSize += font.size+lineSpace
                                    formNx = 0

                                formNx += formCharX

                            nMaxRowSize = max(nMaxRowSize,tempRowSize)
                        
                        rowSizes.append(nMaxRowSize)
                    
                    forms.append({"height":(formRow+2)*formLineSpace+sum(rowSizes),"width":sum(colunmSizes)+exterX,"rowSizes":copy.deepcopy(rowSizes),"colunmSizes":copy.deepcopy(colunmSizes),"form":copy.deepcopy(form),"endIdx":tempIdx,"beginIdx":idx})
                    ny += lineSpace*2+(formRow+2)*formLineSpace+sum(rowSizes)
                    idx = tempIdx
                    nmaxX = max(nmaxX,sum(colunmSizes)+exterX)
                    continue
        else:
            textMode = True
        
        if i == "*" and idx+1<textS and text[idx+1] == "*" and not codeMode:
            idx+=1
            continue
        if i == "~" and idx+1<textS and text[idx+1] == "~" and not codeMode:
            idx+=1
            continue

        if i == "$" and (text[idx-1]!="\\" if idx>=1 else True) and not codeMode and not bMode2:
            tempIdx = idx
            flag = False
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx+=1
                if text[tempIdx]=="$":
                    flag = True
                    break
            if flag or bMode:
                nx+=2
                if not bMode:
                    fontK = nowf
                    nowf = GetGFont(nowf)
                else:
                    nowf = fontK
                bMode = not bMode
                continue
        if i == "`" and (text[idx-1]!="\\" if idx>=1 else True) and not codeMode and not bMode:
            if not (xidx == 1 and idx+2 <= textS and text[idx:idx+3] == "```"):
                tempIdx = idx
                flag = False
                while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                    tempIdx+=1
                    if text[tempIdx]=="`":
                        flag = True
                        break
                if flag or bMode2:
                    nx+=2
                    if not bMode2:
                        fontK = nowf
                        nowf = GetGFont(nowf)
                    else:
                        nowf = fontK
                    bMode2 = not bMode2
                    continue
        
        if i == "!" and idx+9<textS and text[idx:idx+9] == "!sgexter[" and not codeMode and not bMode:
            tempIdx = idx+8
            flag = False
            data = ""

            deep = 0
            string = False
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx+=1

                if text[tempIdx]=="\"" and text[tempIdx-1]=="\\":
                    string = not string

                if text[tempIdx]=="[" and not string:
                    deep += 1

                if text[tempIdx]=="]" and not string:
                    
                    if deep == 0:
                        flag = True
                        break

                    deep -= 1

                data += text[tempIdx]

            if flag:
                flag = False
                
                try:    
                    args = data.split(",")
                    funcName = args[0]
                    args = ",".join(args[1:])
                    flag = True
                except:
                    pass
                
                if flag and funcName in extendFuncs:
                    flag = False

                    try:
                        args1,args2 = GetArgs(args) # type: ignore
                        flag = True
                    except:
                        pass

                    if flag:
                        idata = {"image":extendFuncs[funcName](*args1,**args2,nowf=nowf,style=style,lockColor=lockColor),"begin":idx,"end":tempIdx}
                        images.append(idata)
                        isImage = True
                        xs,ys = idata['image'].size
                        nowObjH = ys
                        idx = tempIdx
                            
                            

        if i == "!" and idx+4<textS and text[idx:idx+5] == "!sgm[" and not codeMode and not bMode:
            tempIdx = idx+4
            flag = False
            imageName = ""
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx+=1
                if text[tempIdx]=="]":
                    flag = True
                    break
                imageName += text[tempIdx]

            if flag and (iFile := imageName.split("|")[0].strip()) in sgImages:
                idx = tempIdx
                nowImage = Image.open(f"data/MarkdownImages/{iFile}")
                if "|" in imageName:
                    reSize = tuple(map(float,imageName.split("|")[1].split(",")))
                    if len(reSize) == 1:
                        nowImage = nowImage.resize(tuple([int(i*reSize[0]) for i in nowImage.size])) # type: ignore
                    elif len(reSize) == 2:
                        nowImage = nowImage.resize(tuple(map(int,reSize))) # type: ignore
                if nowImage.size[0] > maxX:
                    nowImage = nowImage.resize((int(maxX),int(nowImage.size[1]*(maxX/nowImage.size[0]))))
                isImage = True
                xs,ys = nowImage.size
                nowObjH = ys
        
        if i == "!" and idx+1<textS and text[idx:idx+2] == "![" and not codeMode and not bMode:
            imageName = ""
            imageSrc = ""
            getInfo = False
            tempIdx = idx+1
            try:
                flag = False
                while tempIdx<textS-1 and text[tempIdx+1]!="\n":
                    tempIdx+=1
                    if text[tempIdx] == "]":
                        flag = True
                        break
                    imageName += text[tempIdx]
                if not flag:
                    raise ValueError("错误: 图片解析失败")
                tempIdx += 1
                flag = False
                while tempIdx<textS-1 and text[tempIdx+1]!="\n":
                    tempIdx+=1
                    if text[tempIdx] == ")":
                        flag = True
                        break
                    imageSrc += text[tempIdx]
                if not flag:
                    raise ValueError("错误: 图片解析失败")
                imageSrc = imageSrc.split(" ")[0]
                getInfo = True
                try:
                    image = Image.open(imagePath / imageSrc)
                except:
                    if useImageUrl:
                        html = requests.get(imageSrc,timeout=imageUrlGetTimeout,headers=defaultHeaders)
                        imageName = f"{drawId}_{dldImageNum}.png"
                        with open(IMAGE_DOWNLOAD_PATH / imageName,"wb") as f:
                            f.write(html.content)
                        try:
                            image = Image.open(IMAGE_DOWNLOAD_PATH / imageName)
                        except:
                            try:
                                os.remove(IMAGE_DOWNLOAD_PATH / imageName)
                            except:
                                pass
                        dldImageNum += 1
                idata = {"image":image,"begin":idx,"end":tempIdx}
                images.append(idata)
                if idata['image'].size[0] > maxX:
                    idata['image'] = idata['image'].resize((int(maxX),int(idata['image'].size[1]*(maxX/idata['image'].size[0]))))
                isImage = True
                xs,ys = idata['image'].size
                nowObjH = ys
                idx = tempIdx
            except Exception as e:
                skips+=list(range(idx+len(imageName)+2,tempIdx))
                linkbegins.append(idx)
                linkends.append(tempIdx)
                continue
        
        if i == "[" and not codeMode and not bMode:
            tempIdx = idx
            linkName = ""
            link = ""
            flag = False
            while tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx+=1
                if text[tempIdx] == "]":
                    flag = True
                    break
                linkName += text[tempIdx]
            flag = False
            tempIdx += 1
            if tempIdx+1<=textS and text[tempIdx] == "(":
                while tempIdx<textS-1 and text[tempIdx+1]!="\n":
                    tempIdx += 1
                    if text[tempIdx] == ")":
                        flag = True
                        break
                    link += text[tempIdx]
            if flag:
                skips.append(idx+len(linkName)+2)
                linkbegins.append(idx)
                linkends.append(tempIdx if showLink else idx+len(linkName)+2)
                if not showLink:
                    for k in range(idx+len(linkName)+3,tempIdx):
                        skips.append(k)
                skips.append(tempIdx)

        if i == "<" and idx+6<textS and text[idx+1:idx+7] == "color=":
            color = ""
            flag = False
            tempIdx = idx+6
            k = 0
            while tempIdx<textS-1 and text[tempIdx+1]!="\n":
                k+=1
                if k >= 10:
                    break
                tempIdx+=1
                if text[tempIdx] == ">":
                    flag = True
                    break
                color += text[tempIdx]

            if flag:
                if (len(color)==7 and color[0] == "#") or color == "None":
                    lockColor = None if color=="None" else color
                    colors.append({"beginIdx":idx,"endIdx":tempIdx,"color":lockColor})
                    idx = tempIdx
                    continue
        
        if debug:
            sz = nowf.GetSize(i)
            debugs.append((lb+nx,ub+ny+nmaxh-nowf.size,lb+nx+sz[0],ub+ny+nmaxh))

        ex = 0
        preNmaxh = max(nmaxh,nowObjH)
        if dr and min(preNmaxh,font3.size) > dr:
            ex += min(preNmaxh,font3.size)-dr
            dr = min(preNmaxh,font3.size)

        if i == "\n":
            nmaxX = max(nx,nmaxX)
            nx = codeMode*codeLb
            ny += nmaxh+lineSpace
            xidx = 0
            yidx += 1
            hs.append(nmaxh)
            nmaxh = int(fontC.size/3)
            textMode = False
            citeNum = 0
            if not codeMode:
                nowf = font
            dr = 0
            continue
        if nx+xs+ex > maxX:
            nmaxX = max(nx,nmaxX)
            yidx += 1
            nx = codeMode*codeLb
            ny += nmaxh+lineSpace
            if citeNum:
                nx += 30*(citeNum-1)+5
            hs.append(nmaxh)
            nmaxh = int(fontC.size)
            dr = 0
        
        nx += int(xs+ex)
        nmaxh = int(max(nmaxh,nowObjH))

        if debug:
            print(i,hs)

    nmaxX = max(nx,nmaxX)
    nmaxh = max(nmaxh,ys)
    ny += nmaxh
    hs.append(nmaxh)

    if debug:
        print(hs)
        print("\n".join([f"idx:{i+1} {hs[i]}" for i in range(len(hs))]))

    paintImage = None

    if not paint is None:
        paintImage = Image.open(PAINT_PATH / paint)

    if autoPage:
        page = 1
        while True:
            bX = (nmaxX+rb+lb)*page
            bY = int(ny/page)+ub+db
            if bY > 300 and paintImage:
                txs,tys = bX, bY

                if tys < txs*2.5:
                    bX += int(paintImage.size[0]/paintImage.size[1]*(bY-ub-db))
            eX = (nmaxX+rb+lb)*(page+1)
            eY = int(ny/(page+1))+ub+db
            if eY > 300 and paintImage:
                txs,tys = eX, eY

                if tys < txs*2.5:
                    eX += int(paintImage.size[0]/paintImage.size[1]*(eY-ub-db))
            if abs(min(bX,bY)/max(bX,bY)-0.618) < abs(min(eX,eY)/max(eX,eY)-0.618):
                break
            page += 1
    
    if page > len(hs):
        page = len(hs)
    
    txs,tys = (nmaxX+rb+lb)*page,int(ny/page)

    yTys = tys

    temp = 0
    temp2 = tys
    temp3 = tys
    for ys in hs:
        temp += ys

        if temp > yTys:
            temp2 = max(temp2,temp+1)
            temp = 0
            continue

        temp += lineSpace

    temp = 0
    for ys in hs[-1::-1]:
        temp += ys

        if temp > yTys:
            temp3 = max(temp3,temp+1)
            temp = 0
            continue

        temp += lineSpace
    
    tys = min(temp2,temp3)
    
    tys = int(tys)

    PYL = tys+1
    tys += ub+db
    tlb = lb

    bt = False

    if tys > 300 and tys < txs*2.5 and paintImage:
        bt = True
        temp = int(tys-ub-db)
        paintImage = paintImage.resize((int(paintImage.size[0]/paintImage.size[1]*temp),temp))
        txs += paintImage.size[0]

    lockColor = None
    gifPage = None
    gifDuratio = 0.5
    imgUnders:dict[int,Image.Image] = {}

    if style.decorates:
        gifPage = style.decorates.gifPage
        if gifPage:
            gifDuratio = style.decorates.duratio
            for num in set(style.decorates.playbackSequence):
                imgUnders[num] = style.decorates.Draw(int(txs), tys,num)
        else:
            imgUnders[1] = style.decorates.Draw(int(txs), tys)
    else:
        imgUnders[1] = style.backGroundDrawFunc(int(txs), tys)

    imgEffect = Image.new("RGBA",(int(txs), tys),color=(0,0,0,0))
    imgText = Image.new("RGBA",(int(txs), tys),color=(0,0,0,0))
    imgImages = Image.new("RGBA",(int(txs), tys),color=(0,0,0,0))
    
    drawEffect = ImageDrawPro(imgEffect)
    draw = ImageDrawPro(imgText)

    if debug:
        for debugr in debugs:
            draw.rectangle(debugr,(0,0,255,30),(0,0,255))

    effectMaxX = txs
    effectMaxY = ny+ub+db

    for i in range(1,page):
        lx = (nmaxX+rb+lb)*i
        lby = ub
        ley = tys-db
        lwidth = int(min(lb,rb)/6)*2
        match style.pageLineStyle:
            case "full_line":
                drawEffect.line((lx,lby,lx,ley),style.pageLineColor,lwidth)
            case "dotted_line":
                for nly in range(lby,ley,lwidth*8):
                    drawEffect.line((lx,nly,lx,nly+lwidth*5),style.pageLineColor,lwidth)
    
    xidx = 0
    yidx = 1
    nx = 0
    ny = 0
    nmaxh = 0
    nowf = font
    hMode = False
    bMode = False
    bMode2 = False
    lMode = False
    yMode = False
    codeMode = False
    citeNum = 0
    textMode = False

    def ChangeLockColor(color) -> None:
        nonlocal lockColor
        lockColor = color
        draw.text_lock_color = color
    def ChangeLinkMode(mode:bool) -> None:
        nonlocal linkMode
        linkMode = mode
        draw.under_line_mode = mode
    def ChangeDeleteLineMode(mode:bool) -> None:
        nonlocal lMode
        lMode = mode
        draw.delete_line_mode = mode
    def ChangeBlodMode(mode:bool) -> None:
        nonlocal hMode
        hMode = mode
        draw.text_blod_mode = mode

    imageIdx = -1

    idx: int = -1
    while idx<textS-1:
        isImage = False
        nowObjH = nowf.size
        idx += 1
        i = text[idx]
        xidx += 1
        size = nowf.GetSize(i)
        xs,ys = size[0],size[1]
        if idx in skips:
            if idx in linkends:
                ChangeLinkMode(False)
            continue
        if idx in linkbegins:
            ChangeLinkMode(True)
        if idx in linkends:
            ChangeLinkMode(False)
            continue

        if xidx == 1 and not codeMode and i == " ":
            while idx<textS and text[idx] == " ":
                idx += 1
            idx -= 1
            xidx = 0
            continue

        if not textMode and i == "#" and not codeMode:
            if idx+1<textS and text[idx+1]=="#":
                if idx+2<=textS and text[idx+2]=="#":
                    idx += 2
                    nowf = font1
                else:
                    idx += 1
                    nowf = font2
            else:
                nowf = font3
            while idx+1<textS and text[idx+1]==" ":
                idx += 1
            continue
        elif not textMode and i in ["*","-","+"] and idx+1<textS and text[idx+1] == " " and not codeMode:
            idx += 1
            h = min(hs[yidx-1],font3.size)
            s = int(h/6)
            zx,zy = lb+nx+int(h/2),ub+ny+int(h/2)+1
            draw.polygon([(zx-s,zy),(zx,zy-s),(zx+s,zy),(zx,zy+s)],style.unorderedListDotColor)
            nx += int(h)
            while idx+1<textS and text[idx+1]==" ":
                idx += 1
            continue
        elif not textMode and i.isdigit() and not codeMode:
            tempIdx = idx-1
            flag = False
            number = ""
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx+=1
                if text[tempIdx].isdigit():
                    number+=text[tempIdx]
                elif text[tempIdx] == ".":
                    flag = True
                    break
                else:
                    break
            if flag:
                idx = tempIdx
                h = hs[yidx-1]
                s = int(style.codeBlockFontSize*0.67)
                zx,zy = lb+nx+int(h/2),ub+ny+int(hs[yidx-1]/2)+1
                draw.polygon([(zx-s,zy),(zx,zy-s),(zx+s,zy),(zx,zy+s)],style.orderedListDotColor)
                sz = fontC.GetSize(number)
                draw.text((zx-int((sz[0]-1)/2),zy-int(fontC.size/2)-1),number,style.orderedListNumberColor,fontC)
                nx += h
                while idx+1<textS and text[idx+1]==" ":
                    idx += 1
                continue
            else:
                textMode = True
        elif not textMode and i==">" and not codeMode:
            citeNum = 1
            while idx+1<textS and text[idx+1]==">":
                citeNum += 1
                idx += 1
            if not yMode:
                drawEffect.rectangle((lb+nx,ub+ny-halfLineSpace,lb+nx+nmaxX,ub+ny+hs[yidx-1]+halfLineSpace),style.citeUnderpainting)
            for k in range(citeNum-1):
                drawEffect.line((lb+nx+style.citeDistance*(k+1),ub+ny-halfLineSpace,lb+nx+style.citeDistance*(k+1),ub+ny+hs[yidx-1]+halfLineSpace),style.citeSplitLineColor,5)
            nx += style.citeDistance*(citeNum-1)+5
            yMode = True
            xidx -= 1
            while idx+1<textS and text[idx+1]==" ":
                idx += 1
            continue
        elif not textMode and idx+2 <= textS and text[idx:idx+3] in ["```","~~~"]:
            name = ""
            while idx<textS-1 and text[idx+1]!="\n":
                idx+=1
                name += text[idx]
            drawEffect.rectangle((lb,ub+ny,lb+nmaxX,ub+ny+codeUb+fontC.size),style.codeBlockUnderpainting)
            draw.text((lb+codeLb+2,ub+ny),name[2:],style.codeBlockTitleColor,fontC)
            if not codeMode:
                fontK = nowf
                nowf = fontC
            else:
                nowf = fontK
                drawEffect.rectangle((lb,ub+ny-lineSpace,lb+nmaxX,ub+ny+codeUb),style.codeBlockUnderpainting)
            ny+=codeUb
            nx+=codeLb
            codeMode = not codeMode
            continue

        elif not textMode and i == "|" and formIdx+1<len(forms) and forms[formIdx+1]["beginIdx"]==idx and not codeMode:
            formIdx += 1
            formData = forms[formIdx]
            form = formData['form']
            rowSizes = formData['rowSizes']
            colunmSizes = formData['colunmSizes']
            formHeight = formData['height']
            formWidth =formData['width']
            idx = formData['endIdx']
            ny += lineSpace

            exterNum = 0
            bx,by = int(lb+halfFormLineSpace),ub+ny+int(halfFormLineSpace)+exterNum
            
            draw.rectangle((bx,by,int(lb-halfFormLineSpace+formWidth),ub+ny+int(halfFormLineSpace)+formLineSpace*len(rowSizes)+sum(rowSizes)),style.formUnderpainting)
            draw.rectangle((bx,by,int(bx-halfFormLineSpace*2+formWidth),by+rowSizes[0]+formLineSpace),style.formTitleUnderpainting)

            for num in rowSizes:
                draw.line((int(lb+halfFormLineSpace),ub+ny+int(halfFormLineSpace)+exterNum,int(lb-halfFormLineSpace+formWidth),ub+ny+int(halfFormLineSpace)+exterNum),style.formLineColor,2)
                exterNum += num+formLineSpace
            draw.line((int(lb+halfFormLineSpace),ub+ny+int(halfFormLineSpace)+exterNum,int(lb-halfFormLineSpace+formWidth),ub+ny+int(halfFormLineSpace)+exterNum),style.formLineColor,2)
            
            exterNum = 0
            for num in colunmSizes:
                draw.line((int(lb+halfFormLineSpace)+exterNum,ub+ny+int(halfFormLineSpace),int(lb+halfFormLineSpace)+exterNum,ub+ny+int(formHeight-formLineSpace*3/2)),style.formLineColor,2)
                exterNum += num+formLineSpace
            draw.line((int(lb+halfFormLineSpace)+exterNum,ub+ny+int(halfFormLineSpace),int(lb+halfFormLineSpace)+exterNum,ub+ny+int(formHeight-formLineSpace*3/2)),style.formLineColor,2)

            formRow = len(form)
            formHeadNum = len(form[0])

            formTextX = formLineSpace
            formTextY = formLineSpace

            for ii in range(formRow):

                formTextX = formLineSpace
                
                for j in range(formHeadNum):

                    formNx = 0
                    formNy = 0
                    formTextIdx = -1
                    formText = form[ii][j]
                    formTextSize = len(formText)
                    
                    while formTextIdx+1<formTextSize:
                        
                        formTextIdx += 1
                        char = formText[formTextIdx]
                        formCharX = font.GetSize(char)[0]

                        if formNx+formCharX > colunmSizes[j]:
                            formNx = 0
                            formNy += font.size

                        draw.text((lb+formTextX+formNx,ub+ny+formTextY+formNy),char,style.formTextColor,font)

                        formNx += formCharX
                    
                    formTextX += colunmSizes[j]+formLineSpace
                
                formTextY += rowSizes[ii]+formLineSpace
            
            ny += lineSpace+formHeight
            continue
        else:
            textMode = True

        if len(colors) and colors[0]['beginIdx'] == idx:
            ChangeLockColor(colors[0]['color'])
            idx = colors[0]['endIdx']
            del colors[0]
            continue

        if i == "*" and idx+1<textS and text[idx+1] == "*" and not codeMode:
            idx+=1
            ChangeBlodMode(not hMode)
            continue
        if i == "~" and idx+1<textS and text[idx+1] == "~" and not codeMode:
            idx+=1
            ChangeDeleteLineMode(not lMode)
            continue
        if i == "$" and (text[idx-1]!="\\" if idx>=1 else True) and not codeMode and not bMode2:
            tempIdx = idx
            flag = False
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx+=1
                if text[tempIdx]=="$":
                    flag = True
                    break
            if flag or bMode:
                if not bMode:
                    fontK = nowf
                    nowf = GetGFont(nowf)
                    fs = nowf.size
                else:
                    fs = nowf.size
                    nowf = fontK
                bMode = not bMode
                zx,zy = lb+nx,ub+ny+hs[yidx-1]
                drawEffect.rectangle((zx,zy-fs-2,zx+2,zy),style.expressionUnderpainting)
                nx += 2
                continue
        if i == "`" and (text[idx-1]!="\\" if idx>=1 else True) and not codeMode and not bMode:
            if not (xidx == 1 and idx+2 <= textS and text[idx:idx+3] == "```"):
                tempIdx = idx
                flag = False
                while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                    tempIdx+=1
                    if text[tempIdx]=="`":
                        flag = True
                        break
                if flag or bMode2:
                    if not bMode2:
                        fontK = nowf
                        nowf = GetGFont(nowf)
                        fs = nowf.size
                    else:
                        fs = nowf.size
                        nowf = fontK
                    bMode2 = not bMode2
                    zx,zy = lb+nx,ub+ny+hs[yidx-1]
                    draw.rectangle((zx,zy-fs-2,zx+2,zy),style.insertCodeUnderpating)
                    nx += 2
                    continue

        if i == "!" and idx+4<textS and text[idx:idx+5] == "!sgm[" and not codeMode and not bMode:
            tempIdx = idx+4
            flag = False
            imageName = ""
            while  tempIdx<textS-1 and text[tempIdx+1]!="\n":
                tempIdx+=1
                if text[tempIdx]=="]":
                    flag = True
                    break
                imageName += text[tempIdx]

            if flag and (iFile := imageName.split("|")[0].strip()) in sgImages:
                idx = tempIdx
                nowImage = Image.open(f"data/MarkdownImages/{iFile}")
                if "|" in imageName:
                    reSize = tuple(map(float,imageName.split("|")[1].split(",")))
                    if len(reSize) == 1:
                        nowImage = nowImage.resize(tuple([int(i*reSize[0]) for i in nowImage.size])) # type: ignore
                    elif len(reSize) == 2:
                        nowImage = nowImage.resize(tuple(map(int,reSize))) # type: ignore
                if nowImage.size[0] > maxX:
                    nowImage = nowImage.resize((int(maxX),int(nowImage.size[1]*(maxX/nowImage.size[0]))))
                isImage = True
                xs,ys = nowImage.size
                nowObjH = ys

        
        if imageIdx+1 < len(images) and idx == images[imageIdx+1]['begin']:
            imageIdx += 1
            idx = images[imageIdx]['end']
            nowImage = images[imageIdx]["image"]
            isImage = True
            xs,ys = nowImage.size # type: ignore
            nowObjH = ys
        if xidx == 1 and codeMode:
            drawEffect.rectangle((lb,ub+ny-lineSpace,lb+nmaxX,ub+ny+nowf.size),style.codeBlockUnderpainting)

        if i == "\n":
            nx = codeMode*codeLb
            ny += nmaxh+lineSpace
            xidx = 0
            yidx +=1
            if ny+hs[yidx-1] > PYL:
                ny = 0
                lb += tlb+rb+nmaxX
            nmaxh = int(fontC.size/3)
            textMode = False
            citeNum = 0
            if nowf != font and nowf not in Gfonts and not codeMode:
                draw.line((lb,ub+ny-2,lb+nmaxX,ub+ny-2),style.idlineColor)
            if not codeMode:
                nowf = font
            yMode = False
            continue
        if nx+xs > maxX:
            nx = codeMode*codeLb
            ny += nmaxh+lineSpace
            yidx += 1
            nmaxh = int(fontC.size)
            try:
                if ny+hs[yidx-1] > PYL:
                    ny = 0
                    lb += tlb+rb+nmaxX
            except:
                pass
            if citeNum:
                nx += style.citeDistance*(citeNum-1)+5
            if yMode:
                drawEffect.rectangle((lb,ub+ny-halfLineSpace,lb+nmaxX,ub+ny+hs[yidx-1]+halfLineSpace),style.citeUnderpainting)
                for k in range(citeNum-1):
                    drawEffect.line((lb+style.citeDistance*(k+1),ub+ny-halfLineSpace,lb+style.citeDistance*(k+1),ub+ny+hs[yidx-1]+halfLineSpace),style.citeSplitLineColor,5)
        
        b = style.title1FontSize - style.fontSize
        normalColor = tuple(int(style.textColor[i]+(style.textGradientEndColor[i]-style.textColor[i])/b*(nowf.size-style.fontSize)) for i in range(min(len(style.textColor),len(style.textGradientEndColor))))
        if linkMode:
            normalColor = style.linkColor

        if debug:
            print(f"{i}: {lb+nx},{ub+ny+hs[yidx-1]-nowf.size} idx:{yidx}")

        if isImage and isinstance(nowImage,Image.Image):
            #drawImage.rectangle((lb+nx-1,ub+ny+hs[yidx-1]-nowImage.size[1]-1,lb+nx+nowImage.size[0]+1,ub+ny+hs[yidx-1]+1),None,"#99FFCCAA",2)
            imgImages.alpha_composite(nowImage.convert("RGBA"),(int(lb+nx), ub+ny+hs[yidx-1]-nowImage.size[1]))
        elif bMode or bMode2:
            if bMode:
                drawEffect.rectangle((lb+nx,ub+ny+hs[yidx-1]-nowf.size-2,lb+nx+xs,ub+ny+hs[yidx-1]),style.expressionUnderpainting)
                draw.text((lb+nx,ub+ny+hs[yidx-1]-nowf.size-2),i,style.expressionTextColor,nowf)
            elif bMode2:
                drawEffect.rectangle((lb+nx,ub+ny+hs[yidx-1]-nowf.size-2,lb+nx+xs,ub+ny+hs[yidx-1]),style.insertCodeUnderpating)
                draw.text((lb+nx,ub+ny+hs[yidx-1]-nowf.size-2),i,style.insertCodeTextColor,nowf)
        elif codeMode:
            draw.text((lb+nx,ub+ny+hs[yidx-1]-nowf.size-2),i,style.codeBlockTextColor,nowf,**{key:False for key in ["use_under_line_mode","use_delete_line_mode","use_blod_mode"]})
        else:
            draw.text((lb+nx,ub+ny+hs[yidx-1]-nowf.size),i,normalColor,nowf)
        
        if debug:
            sz = nowf.GetSize(i)
            draw.rectangle((lb+nx,ub+ny+hs[yidx-1]-nowf.size,lb+nx+sz[0],ub+ny+hs[yidx-1]),None,(255,0,0))
            draw.text((lb,ub+ny-fontC.size),f"hs:{hs[yidx-1]} {yidx}/{len(hs)}",(255,0,0),fontC)
            draw.line((lb-3,ub+ny,lb-3,ub+ny+hs[yidx-1]),(255,0,0))

        xidx += 1
        nx += xs
        nmaxh = int(max(nmaxh,nowObjH))
    
    ChangeLockColor(None)
    ChangeBlodMode(False)
    ChangeDeleteLineMode(False)
    ChangeLinkMode(False)

    fSize = fontR.GetSize(title)
    x = style.remarkCoordinate[0] if style.remarkCoordinate[0] >= 0 else imgText.size[0]+style.remarkCoordinate[0]-fSize[0]
    y = style.remarkCoordinate[1] if style.remarkCoordinate[1] >= 0 else imgText.size[1]+style.remarkCoordinate[1]-fSize[1]
    draw.text((x,y),title,style.remarkColor,fontR)

    imgEffect.alpha_composite(imgText)
    imgEffect.alpha_composite(imgImages)

    playbackSequence = [1]

    for imgUnder in imgUnders.values():
        if logoFile:
            logo = Image.open(LOGO_PATH / logoFile).convert("RGBA")
            if imgUnder.width<logo.width or imgUnder.height<logo.height:
                continue
            imgUnder.alpha_composite(logo, (int(imgUnder.width - logo.width),0))
        imgUnder.alpha_composite(imgEffect)

        if bt and paintImage:
            imgUnder.alpha_composite(paintImage,(int(txs-rb-paintImage.size[0]),tys-paintImage.size[1]-db))
    
    if style.decorates:

        if gifPage:
            for num in set(style.decorates.playbackSequence):
                imgUnder = imgUnders[num]
                imgUnder.alpha_composite(style.decorates.DrawTop(int(txs),tys,num))
        else:
            imgUnders[1].alpha_composite(style.decorates.DrawTop(int(txs),tys))
        
        playbackSequence = style.decorates.playbackSequence

    if gifPage and len(imgUnders) > 1:
        ftype = "gif"
    else:
        ftype = "png"

    outImages = [imgUnders[1]]
    
    if ftype == "gif":
        outImages = [imgUnders[idx] for idx in playbackSequence]
        outImage = outImages[0]
        outImage.info["duration"] = gifDuratio * 1000
    else:
        outImage = imgUnders[1]

    for i in range(dldImageNum):
        try:
            os.remove(IMAGE_DOWNLOAD_PATH / f"{drawId}_{i}.png")
        except:
            pass
    
    return MdRenderResult(
        image = outImage,
        imageType = ftype,
        gifDuratio = gifDuratio,
        images = outImages,
    )