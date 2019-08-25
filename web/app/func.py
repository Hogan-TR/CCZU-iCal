import requests
from lxml import etree


class iCal(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}

    def LoginCookie(self, username: str, passwd: str) -> dict:
        session = requests.session()
        url = "http://jwcas.cczu.edu.cn/login"

        # Get the random data to login
        try:
            html = session.get(url, headers=self.headers)
            html.encoding = html.apparent_encoding
            html = html.text
        except:
            return "获取教务系统登录页错误，请稍后重试"

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
            'username': username,
            'password': passwd,
            'warn': 'true',
            'lt': gAll['lt'],
            'execution': gAll['execution'],
            '_eventId': gAll['_eventId']
        }

        # Official Login
        sc = session.post(url, headers=self.headers, data=data)
        if not sc.cookies.get_dict():
            return "用户名或密码错误，请检查重试"

        # Intercept jump link
        try:
            tmp = session.get(
                'http://jwcas.cczu.edu.cn/login?service=http://219.230.159.132/login7_jwgl.aspx', headers=self.headers)
            tmp_html = etree.HTML(tmp.text)
            Rurl = tmp_html.xpath('//a[@href and text()]/@href')[0]
        except:
            return "获取教务系统跳转链接错误，请稍后重试"

        # Get Cookies we need from DirectPage
        try:
            tmp2 = session.get(Rurl, headers=self.headers)
        except:
            return "获取教务系统Cookies错误，请稍后重试"

        # Extract the cookies dictionary and return it.
        return tmp2.cookies.get_dict()
