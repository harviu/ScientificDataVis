from PIL import Image
import glob, os, re
from pathlib import Path

dir1 = "output_test/"
dir2 = "output_test_2/"
dir3 = "output_slice_yA31_combine/"



p = re.compile(r'http://oceans11.*?\.vti')
with open("yA31.html",'r',encoding='utf-8') as html:
    text = html.read()
    indices = []
    for url in p.finditer(text):
        name = url.group(0)[-9:-4]+".png"
        file1 = Path(dir1+name)
        file2 = Path(dir2+name)
        if file1.is_file() and file2.is_file():
            im = Image.open(dir1+name)
            im2 = Image.open(dir2+name)

            im3 = Image.blend(im,im2,alpha=0.5)

            im3.save(dir3+name,"png")

        