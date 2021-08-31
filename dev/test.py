import sys
import requests
import asyncio
import aiohttp
import random
import logging
from lxml import etree
from generator import classHandler


def LoginCookie(user: str, passwd: str) -> dict:
    session = requests.session()
    url = "http://jwcas.cczu.edu.cn/login"

    # Get the random data to login
    try:
        html = session.get(url, headers=headers)
        html.raise_for_status()
        html.encoding = html.apparent_encoding
        html = html.text
    except:
        print("从登录页获取随机信息失败")
        sys.exit(0)

    # Initialize the string, which makes it available to the function of xpath
    html = etree.HTML(html)
    # Get the name and value of random data
    # Type of gName, gValue: list
    gName = html.xpath('//input[@type="hidden"]/@name')
    gValue = html.xpath('//input[@type="hidden"]/@value')

    gAll = {}
    for i in range(3):
        gAll[gName[i]] = gValue[i]

    # Post data
    data = {
        'username': user,
        'password': passwd,
        'warn': 'true',
        'lt': gAll['lt'],
        'execution': gAll['execution'],
        '_eventId': gAll['_eventId']
    }

    # Official Login
    sc = session.post(url, headers=headers, data=data)
    if not sc.cookies.get_dict():
        print("用户名或密码错误，请检查重试")
        sys.exit(0)

    # Intercept jump link
    try:
        tmp = session.get(
            'http://jwcas.cczu.edu.cn/login?service=http://219.230.159.132/login7_jwgl.aspx', headers=headers)
        tmp_html = etree.HTML(tmp.text)
        Rurl = tmp_html.xpath('//a[@href and text()]/@href')[0]
    except:
        print("获取跳转链接失败")
        sys.exit(0)

    # Get Cookies we need from DirectPage
    try:
        tmp2 = session.get(Rurl, headers=headers)
    except:
        print("获取实用Cookies失败")
        sys.exit(0)

    # Extract the cookies dictionary and return it.
    print("获取Cookies成功")
    return tmp2.cookies.get_dict()


def extraIds(cookies: dict) -> list:
    url = 'http://219.230.159.132/web_jxrw/cx_kb_bjxzall.aspx'
    session = requests.session()
    get = session.get(url, headers=headers, cookies=cookies).text
    html = etree.HTML(get)
    data = {
        'ScriptManager1': 'UpdatePanel2|Cxbj_all1$Btbjall',
        'DDxq': '19-20-1',
        'Cxbj_all1$DDDnj': '2020',
        'Cxbj_all1$Txtbj': '',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': html.xpath('//input[@id="__VIEWSTATE"]/@value')[0],
        '__VIEWSTATEGENERATOR': html.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0],
        '__ASYNCPOST': 'true',
        'Cxbj_all1$Btbjall': '所有班级',
    }
    get = session.post(url, headers=headers, data=data).text
    html = etree.HTML(get)
    pars = html.xpath('//select/option/@value')
    return pars


def genUrls(ids: list, xq: str):
    url = 'http://219.230.159.132/web_jxrw/cx_kb_bjkb_bj.aspx?xsbh={}&xq={}'
    return random.sample([url.format(id, xq) for id in ids], 20)


class AsyncGrad(object):
    def __init__(self, urls, max_threads, cookies) -> None:
        self.urls = urls
        self.max_threads = max_threads
        self.cookies = cookies

    async def g(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=self.cookies, timeout=30) as response:
                assert response.status == 200
                return await response.read()

    async def taskhandler(self, task_id, work_queue):
        while not work_queue.empty():
            cur_url = await work_queue.get()
            html = bytes.decode(await self.g(cur_url), encoding='utf-8')
            html = etree.HTML(html)
            if html.xpath('//div[@id="Panel1"]//table') == []:
                continue
            table = html.xpath('//div[@id="Panel2"]//table')[0]
            courseInfo = classHandler(table)
            logging.debug(courseInfo)

    def eventloop(self):
        q = asyncio.Queue()
        [q.put_nowait(url) for url in self.urls]
        loop = asyncio.get_event_loop()
        tasks = [self.taskhandler(id, q) for id in range(self.max_threads)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
    logging.basicConfig(
        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=logging.DEBUG)
    # cookies = LoginCookie('', '')
    cookies = {'ASP.NET_SessionId': 'asq5cb45daonxp45gtorhq45'}
    ids = extraIds(cookies)
    urls = genUrls(ids, '20-21-1')
    test = AsyncGrad(urls, 10, cookies)
    test.eventloop()
