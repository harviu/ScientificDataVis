import urllib.request
import re


def download(dataName):
    p = re.compile(r'http://oceans11.*?\.vti')
    with open(dataName+".html",'r',encoding='utf-8') as html:
        text = html.read()
        for url in p.finditer(text):
            filename = url[0][-9:] #url[0] is the match 
            urllib.request.urlretrieve(url[0],dataName+"/"+filename)

#uncomment the line to download the data
# download("yA31")
# download("yC31")