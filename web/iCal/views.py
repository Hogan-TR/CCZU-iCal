from django.shortcuts import render
import requests
import copy
import time
import json
import datetime
import os
from random import Random
from lxml import etree


def index(request):
    return render(request, 'iCal/index.html')


class iCal(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.classInfoList = None  # Formatted schedule
        self.classTimeList = None  # Loaded schedule time
        self.DONE_firstWeekDate = None  # Processed first week datet
        self.DONE_reminder = None  # Processed reminder time
        self.DONE_ALARMUID = None
        self.DONE_UnitUID = None

    def LoginCookie(self, username: str, passwd: str) -> dict:  # Or: Error Str
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

    def GetClass(self, cookies: dict) -> list:  # Or: Error None
        url = "http://219.230.159.132/web_jxrw/cx_kb_xsgrkb.aspx"

        try:
            rep = requests.get(url, headers=self.headers, cookies=cookies)
            rep = rep.text
        except requests.exceptions.HTTPError:  # If get the status code - 500
            return "获取课表错误，请稍后重试"

        html = etree.HTML(rep)
        gClass = html.xpath(
            '//div[@id="UpdatePanel4"]//tr[position()>1]/td/text()')

        return gClass

    def ClassProcess(self, gClass: list) -> list:  # classInfoList
        # Format the schedule according to the week
        classInfoList = list()  # Final return
        index = 0
        cScheduleTemp = [list() for _ in range(7)]
        for get in gClass:
            if index % 8 == 0:
                pass
            else:
                cScheduleTemp[index % 8 - 1].append(get)
            index += 1

        classInfoTemp = list()
        for i in range(7):  # Traverse each day in turn
            num = 0
            classToday = list()  # A list contains today's class schedules
            # Every day of the week
            for info in cScheduleTemp[i]:
                num += 1
                if info == '\xa0':
                    continue  # No processing without class
                # ex: ['计算机科学与技术导论 W1102  13-16,']
                infoList = info.split('/')[:-1]
                # The situation of different classes in different weeks in the same class
                for x in infoList:
                    temp = x.split()  # ex: ['计算机科学与技术导论', 'W1102', '13-16,']
                    if len(temp) == 2:
                        temp.insert(1, 'Unknow')
                    if len(temp) == 3:
                        temp.insert(2, '3')
                    if len(temp) == 4:  # 3: All Weeks 1: Single Weeks 2: Double Weeks
                        if temp[2] == '单':
                            temp[2] = '1'
                        elif temp[2] == '双':
                            temp[2] = '2'
                    temp.append(i + 1)  # What day of the week.
                    temp.append(num)  # What class is it.

                    classToday.append(temp)

            # Configure the start and end time of the class.
            # Consolidated classes.
            classDict = dict()
            for eclass in classToday:
                className = eclass[0]
                if className not in classDict:
                    eclass.append(1)
                    classDict[className] = eclass
                else:
                    # If the class already exists in classDict
                    # Plus the Class Hours(+1)
                    classDict[className][6] += 1

            # Generating a list of class information (Temporary)
            for eclass in classDict.values():
                classInfoTemp.append(eclass)

        # Generating a list of single class information (Completely)
        # Divide the weeks of the class
        for eclass in classInfoTemp:
            cWeek = eclass[3].split(',')
            del eclass[3]
            for week in cWeek:
                if week != '':
                    gweek = map(int, week.split('-'))
                    tpweek = copy.deepcopy(eclass)
                    tpweek.extend(gweek)
                    classInfoList.append(tpweek)
        self.classInfoList = classInfoList

    def setFirstWeekDate(self, firstWeekDate: str):  # DONE_firstWeekDate
        self.DONE_firstWeekDate = time.strptime(
            firstWeekDate, '%Y%m%d')  # firstWeekDate Ex: 20190902

    def setReminder(self, reminder: str):  # DONE_reminder
        reminderList = ["-PT10M", "-PT30M", "-PT1H", "-PT2H", "-P1D"]
        if (reminder == "1"):
            DONE_reminder = reminderList[0]
        elif (reminder == "2"):
            DONE_reminder = reminderList[1]
        elif (reminder == "3"):
            DONE_reminder = reminderList[2]
        elif (reminder == "4"):
            DONE_reminder = reminderList[3]
        elif (reminder == "5"):
            DONE_reminder = reminderList[4]
        else:
            DONE_reminder = "NULL"
        self.DONE_reminder = DONE_reminder

    def setClassTime(self):  # classTimeList
        data = []
        with open('../../conf_classTime.json', 'r') as f:
            data = json.load(f)
        classTimeList = data["classTime"]
        self.classTimeList = classTimeList

    def uniteSetting(self):  # DONE_ALARMUID, DONE_UnitUID
        self.DONE_ALARMUID = self.random_str(30) + "&Jacob.com"
        self.DONE_UnitUID = self.random_str(20) + "&Jacob.com"

    def classInfoHandle(self):  # classInfo
        NO = 1
        YES = 0
        DONE_firstWeekDate = self.DONE_firstWeekDate

        for classInfo in self.classInfoList:
            startWeek = classInfo[6]
            endWeek = classInfo[7]
            weekday = classInfo[3]
            week = int(classInfo[2])  # 1/2/3  Single/Double/All

            dateLength = float((startWeek - 1) * 7)
            startDate = datetime.datetime.fromtimestamp(int(time.mktime(
                DONE_firstWeekDate))) + datetime.timedelta(days=dateLength + weekday - 1)
            string = startDate.strftime('%Y%m%d')

            dateLength = float((endWeek - 1) * 7)
            endDate = datetime.datetime.fromtimestamp(int(time.mktime(
                DONE_firstWeekDate))) + datetime.timedelta(days=dateLength + weekday - 1)

            date = startDate
            dateList = []
            if (week == 3):
                dateList.append(string)
            if ((week == 2) and (startWeek % 2 == 0)):
                dateList.append(string)
            if ((week == 1) and (startWeek % 2 == 1)):
                dateList.append(string)
            i = NO
            w = startWeek + 1
            while (i):
                date = date + datetime.timedelta(days=7.0)
                if (date > endDate):
                    i = YES
                if (week == 3):
                    string = date.strftime('%Y%m%d')
                    dateList.append(string)
                if ((week == 1) and (w % 2 == 1)):
                    string = date.strftime('%Y%m%d')
                    dateList.append(string)
                if ((week == 2) and (w % 2 == 0)):
                    string = date.strftime('%Y%m%d')
                    dateList.append(string)
                w = w + 1
            classInfo.append(dateList)

            DONE_CreatedTime = self.CreateTime()
            classInfo.append(DONE_CreatedTime)
            classInfo.append(DONE_CreatedTime)
            UID_List = []
            for date in dateList:
                UID_List.append(self.UID_Create())
            classInfo.append(UID_List)

    def random_str(self, randomlength):
        string = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        random = Random()
        for _ in range(randomlength):
            string += chars[random.randint(0, length)]
        return string

    def CreateTime(self):  # DONE_CreatedTime
        # Generate CREATED
        date = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        DONE_CreatedTime = date + "Z"
        return DONE_CreatedTime

    def UID_Create(self):
        return self.random_str(20) + "&Jacob.com"

    def save(self, string, username):
        f = open(f"../tempics/class_{username}.ics", 'wb')
        f.write(string.encode("utf-8"))
        f.close()

    def icsCreateAndSave(self, username):
        icsString = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:课程表\nPRODID:-//Apple Inc.//Mac OS X 10.12//EN\nX-APPLE-CALENDAR-COLOR:#FC4208\nX-WR-TIMEZONE:Asia/Shanghai\nCALSCALE:GREGORIAN\nBEGIN:VTIMEZONE\nTZID:Asia/Shanghai\nBEGIN:STANDARD\nTZOFFSETFROM:+0900\nRRULE:FREQ=YEARLY;UNTIL=19910914T150000Z;BYMONTH=9;BYDAY=3SU\nDTSTART:19890917T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0800\nEND:STANDARD\nBEGIN:DAYLIGHT\nTZOFFSETFROM:+0800\nDTSTART:19910414T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0900\nRDATE:19910414T000000\nEND:DAYLIGHT\nEND:VTIMEZONE\n"
        eventString = ""
        classInfoList = self.classInfoList
        classTimeList = self.classTimeList
        DONE_ALARMUID = self.DONE_ALARMUID
        DONE_UnitUID = self.DONE_UnitUID
        DONE_reminder = self.DONE_reminder

        for classInfo in classInfoList:
            # i = int(classInfo["classTime"]-1)
            classBegin = classInfo[4] - 1
            classTimes = classInfo[5]
            className = classInfo[0] + " | " + classInfo[1]
            endTime = classTimeList[classBegin + classTimes - 1]["endTime"]
            startTime = classTimeList[classBegin]["startTime"]
            index = 0
            for date in classInfo[8]:
                eventString = eventString + \
                    "BEGIN:VEVENT\nCREATED:" + classInfo[9]
                eventString = eventString + "\nUID:" + classInfo[11][index]
                eventString = eventString + "\nDTEND;TZID=Asia/Shanghai:" + date + "T" + endTime
                eventString = eventString + \
                    "00\nTRANSP:OPAQUE\nX-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\nSUMMARY:" + className
                eventString = eventString + "\nDTSTART;TZID=Asia/Shanghai:" + \
                    date + "T" + startTime + "00"
                eventString = eventString + "\nDTSTAMP:" + classInfo[9]
                eventString = eventString + "\nSEQUENCE:0\nBEGIN:VALARM\nX-WR-ALARMUID:" + DONE_ALARMUID
                eventString = eventString + "\nUID:" + DONE_UnitUID
                eventString = eventString + "\nTRIGGER:" + DONE_reminder
                eventString = eventString + \
                    "\nDESCRIPTION:事件提醒\nACTION:DISPLAY\nEND:VALARM\nEND:VEVENT\n"

                index += 1
        icsString = icsString + eventString + "END:VCALENDAR"
        self.save(icsString, username)


class iCalPro(iCal):
    def __init__(self):
        super(iCalPro, self).__init__()

    def iCalPro(self, username, password, date, reminder) -> tuple:
        Cookies = self.LoginCookie(username, password)
        if isinstance(Cookies, str):
            return False, Cookies  # Error Reason
        ClassList = self.GetClass(Cookies)
        if isinstance(ClassList, str):
            return False, ClassList  # Error Reason

        try:
            # Main
            self.ClassProcess(ClassList)
            # Prepare Info
            self.setFirstWeekDate(date)
            self.setReminder(reminder)
            self.uniteSetting()
            self.setClassTime()
            # Return Main
            self.classInfoHandle()
            self.icsCreateAndSave(username)
            return True, "课表生成成功"
        except:
            return False, "处理课表数据是遇到未知错误"


test = iCalPro()
res = test.iCalPro('18416328','194117','20190902','1')
print(res)