import requests
import time
import re
import sys
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

Headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 52.0 .2743 .116 Safari / 537.36 '}

#获取所有目标页面的html
def get_all_html(start, end):

    htmls = []
    root_url = 'http://www.liuli.pl/wp/anime.html/page/'
    for i in range(start, end + 1):
        try:
            url = root_url + str(i)
            r = requests.get(url, headers=Headers, timeout=10)
            r.raise_for_status()
            r.encoding = 'utf-8'
            htmls.append(r.text)
            print('Get page %d successfully!' % i)
        except:
            print('Something is wrong when get html. May be timeout.')
    return htmls


#对于单个包含磁链的页面进行信息采集
def get_magnetic(url):
    time.sleep(2)
    html = requests.get(url, headers=Headers)
    print("craw html:", url)
    soup = BeautifulSoup(html.content, 'html.parser')
    res_title = soup.find('h1', {'class': 'entry-title'})
    resource = soup.find_all(text = re.compile('([0-9a-fA-F]{40})'))
    res_set = set(resource)
    with open('magnet.txt', 'a+', encoding='utf-8') as f:
        if res_title is not None:
            print(res_title.get_text())
            f.write(res_title.get_text() + '\n')
            for res in res_set:
                f.write('       magnet:?xt=urn:btih:' + res.strip() + '\n')
        else:
            print("Skip it!")
            return

#用每个page页面的html得到资源页面的url并进行资源采集
def get_all_magnetic(htmls):
    urls = []
    print("Preparing...")
    for html in htmls:
        soup = BeautifulSoup(html, 'html.parser')
        pageList = soup.find_all('h1', {'class': 'entry-title'})
        for page in pageList:
            target_page = page.a['href']
            urls.append(target_page)
            # get_magnetic(target_page)
    pool = ThreadPool(8)
    pool.map(get_magnetic, urls)
    pool.close()
    pool.join()

if __name__ == '__main__':
    htmls = get_all_html(1, 17)
    get_all_magnetic(htmls)