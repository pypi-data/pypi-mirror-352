import numpy as np
from pyimager import *
from PIL import ImageFont, ImageDraw, Image
import cv2
import time

## Make canvas and set the color
b,g,r,a = 0,255,0,128
img = new_img(background=COL.red)
text = time.strftime("%Y/%m/%d %H:%M:%S %Z", time.localtime())
img.write_centered(text, [RES.resolution[0]/2, RES.resolution[1]/4], (r, g, b), 3, 3, lineType=2)

## Use simsum.ttc to write Chinese.
fontpath = "/usr/share/fonts/google-noto-sans-cjk-vf-fonts/NotoSansCJK-VF.ttc" # <== 这里是宋体路径
font = ImageFont.truetype(fontpath, 100)
txt = "端午节就要到了。。。"
img_pil = Image.fromarray(img.img)
draw = ImageDraw.Draw(img_pil)
_, _, w, h = draw.textbbox((0, 0), txt, font=font)
draw.text([RES.resolution[0]/2-w/2, RES.resolution[1]/2-h/2], txt, stroke_width=3, font = font, fill = (b, g, r, a))
img.img = np.array(img_pil)
img.write_centered("--- by Silencer", [RES.resolution[0]/2, RES.resolution[1]*0.75], (r, g, b), 3, 3, lineType=2)

img.build()
while img.is_opened():
    img.show()