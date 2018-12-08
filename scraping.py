import urllib.request
import re
from multiprocessing import Pool
from pathlib import Path
from progress.bar import Bar


def download(url):
    filename = "output/"+url[-9:]
    file = Path(filename)
    if not file.is_file():
        count = 0
        while True:
            # print("Downloading "+filename)
            try:
                urllib.request.urlretrieve(url,filename)
                break
            except:
                print("Retrying...")
                count = count +1
                if count == 5:
                    print("Failed to download "+filename)
                    file.unlink()
                    break



def main():
    p = re.compile(r'http://oceans11.*?\.vti')
    with open("yA31.html",'r',encoding='utf-8') as html:
        text = html.read()
        url = p.findall(text)
        bar = Bar('Downloading',max = len(url))
        pool = Pool(processes=1) # change the para task number
        for _ in pool.imap(download, url):
            bar.next()
        bar.finish()


if __name__ == '__main__':
    main()