from PIL import Image, ImageDraw
import random

def Sample(xs:int,ys:int) -> Image.Image:
    image = Image.new("RGBA",(xs,ys),color=(0,0,0))

    drawUnder = ImageDraw.Draw(image)
    for i in range(11):
        drawUnder.rectangle((0,i*int(ys/10),xs,(i+1)*int(ys/10)),(52-3*i,73-4*i,94-2*i))

    imgUnder2 = Image.new("RGBA",(xs,ys),color=(0,0,0,0))
    drawUnder2 = ImageDraw.Draw(imgUnder2)
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