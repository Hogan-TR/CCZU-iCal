import requests
import json
import sys
import copy
import datetime
import time
from random import Random
from lxml import etree


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
        print("Failed to pick up details of LoginPage.")
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
        print("Failed to Login, please check the username and password.")
        sys.exit(0)

    # Intercept jump link
    try:
        tmp = session.get(
            'http://jwcas.cczu.edu.cn/login?service=http://219.230.159.132/login7_jwgl.aspx', headers=headers)
        tmp_html = etree.HTML(tmp.text)
        Rurl = tmp_html.xpath('//a[@href and text()]/@href')[0]
    except:
        print("Failed to pick up JumpPage's URL.")
        sys.exit(0)

    # Get Cookies we need from DirectPage
    try:
        tmp2 = session.get(Rurl, headers=headers)
    except:
        print("Failed to pick up Cookies of DirectPage.")
        sys.exit(0)

    # Extract the cookies dictionary and return it.
    print("Getting Cookies Successfully.")
    return tmp2.cookies.get_dict()


def GetClass(cookies: dict) -> list:
    url = "http://219.230.159.132/web_jxrw/cx_kb_xsgrkb.aspx"

    try:
        rep = requests.get(url, headers=headers, cookies=cookies)
        rep.raise_for_status()
        rep = rep.text
    except requests.exceptions.HTTPError:  # If get the status code - 500
        return None

    html = etree.HTML(rep)
    gClass = html.xpath(
        '//div[@id="UpdatePanel4"]//tr[position()>1]/td/text()')

    return gClass


def ClassProcess(gClass: list):
    # Format the schedule according to the week
    index = 0
    cScheduleTemp = [list() for _ in range(7)]
    for get in gClass:
        if index % 8 == 0:
            pass
        else:
            cScheduleTemp[index % 8 - 1].append(get)
        index += 1

    classInfoTemp = list()
    global classInfoList
    for i in range(7):  # Traverse each day in turn
        num = 0
        classToday = list()  # A list contains today's class schedules 经过格式化处理的今日课
        # Every day of the week
        for info in cScheduleTemp[i]:  # cScheduleTemp[i]存储一天的课程
            num += 1
            if info == '\xa0':  # 此节课没有课
                continue  # No processing without class
            infoList = info.split('/')[:-1]  # ex: ['计算机科学与技术导论 W1102  13-16,']
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
                temp.append(i + 1)  # What day of the week. 星期几
                temp.append(num)  # What class is it. 第几节课

                # temp 标准范例：['概率论与数理统计', 'W15阶', '3', '2-5,8-16', 1, 7]
                # temp 格式注释：[课程名称, 上课地点, 单双周, 哪几周上课, 星期几, 第几节课]

                classToday.append(temp)

        # Configure the start and end time of the class.
        # Consolidated classes.
        classDict = dict()
        for eclass in classToday:
            className = eclass[0]  # 课程名称
            classPlace = eclass[1]  # 课程地点
            if (className+classPlace) not in classDict:
                eclass.append(1)
                classDict[className+classPlace] = eclass
            else:
                # If the class already exists in classDict
                # Plus the Class Hours(+1)
                classDict[className+classPlace][6] += 1

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

    print("Processing Class Schedule Successfully.")


def setFirstWeekDate(firstWeekDate):
    global DONE_firstWeekDate
    DONE_firstWeekDate = time.strptime(firstWeekDate, '%Y%m%d')
    print("SetFirstWeekDate:", DONE_firstWeekDate)


def setReminder(reminder):
    global DONE_reminder
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
    print("SetReminder:", reminder)


def setClassTime():
    data = []
    with open('conf_classTime.json', 'r') as f:
        data = json.load(f)
    global classTimeList
    classTimeList = data["classTime"]
    print("Setting ClassTime Successfully.")


def classInfoHandle():
    global DONE_firstWeekDate, NO, YES
    global classInfoList
    for classInfo in classInfoList:
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

        global DONE_CreatedTime, DONE_EventUID
        CreateTime()
        classInfo.append(DONE_CreatedTime)
        classInfo.append(DONE_CreatedTime)
        UID_List = []
        for date in dateList:
            UID_List.append(UID_Create())
        classInfo.append(UID_List)
    print("ClassInfo Handled Successfully.")


def random_str(randomlength):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def CreateTime():
    # Generate CREATED
    global DONE_CreatedTime
    date = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    DONE_CreatedTime = date + "Z"


def UID_Create():
    return random_str(20) + "&Jacob.com"


def uniteSetting():
    global DONE_ALARMUID
    DONE_ALARMUID = random_str(30) + "&Jacob.com"

    global DONE_UnitUID
    DONE_UnitUID = random_str(20) + "&Jacob.com"
    print("Setting Unite Successfully.")


def save(string):
    f = open("class.ics", 'wb')
    f.write(string.encode("utf-8"))
    f.close()


def icsCreateAndSave():
    icsString = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:课程表\nPRODID:-//Apple Inc.//Mac OS X 10.12//EN\nX-APPLE-CALENDAR-COLOR:#FC4208\nX-WR-TIMEZONE:Asia/Shanghai\nCALSCALE:GREGORIAN\nBEGIN:VTIMEZONE\nTZID:Asia/Shanghai\nBEGIN:STANDARD\nTZOFFSETFROM:+0900\nRRULE:FREQ=YEARLY;UNTIL=19910914T150000Z;BYMONTH=9;BYDAY=3SU\nDTSTART:19890917T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0800\nEND:STANDARD\nBEGIN:DAYLIGHT\nTZOFFSETFROM:+0800\nDTSTART:19910414T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0900\nRDATE:19910414T000000\nEND:DAYLIGHT\nEND:VTIMEZONE\n"
    global classTimeList, DONE_ALARMUID, DONE_UnitUID, classInfoList
    eventString = ""
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
            eventString = eventString + "\nDTSTAMP:" + \
                DONE_CreatedTime  # classInfo["CREATED"]
            eventString = eventString + "\nSEQUENCE:0\nBEGIN:VALARM\nX-WR-ALARMUID:" + DONE_ALARMUID
            eventString = eventString + "\nUID:" + DONE_UnitUID
            eventString = eventString + "\nTRIGGER:" + DONE_reminder
            eventString = eventString + \
                "\nDESCRIPTION:事件提醒\nACTION:DISPLAY\nEND:VALARM\nEND:VEVENT\n"

            index += 1
    icsString = icsString + eventString + "END:VCALENDAR"
    save(icsString)
    print("File Saved Successfully.")


if __name__ == "__main__":
    # Initialize variables
    YES = 0
    NO = 1
    DONE_firstWeekDate = time.time()
    DONE_reminder = ""
    DONE_EventUID = ""
    DONE_UnitUID = ""
    DONE_CreatedTime = ""
    DONE_ALARMUID = ""
    classInfoList = list()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}

    UserInfo = input(
        'Please input your Username and Password to Login(Separated by Space in one line): ').split()
    try:
        print("Getting Cookies...")
        gCookie = LoginCookie(UserInfo[0], UserInfo[1])  # Type: Dict
    except:
        print('Meet the error when try to Login, please try again.')
        sys.exit(0)

    # gCookie = {'ASP.NET_SessionId': ''}

    print("Getting Class Schedule...")
    gClass = GetClass(gCookie)
    if not gClass:
        print('Meet the error when try to get RawClass, please try again.')
        sys.exit(0)
    else:
        print("Getting Class Schedule Successfully")

    print("Processing Class Schedule...")
    ClassProcess(gClass)

    firstWeekDate = input(
        'Please set the Monday date of the first week (eg 20160905):')  # Date of the first week of Monday
    print("Setting The First WeekDate...")
    setFirstWeekDate(firstWeekDate)

    reminder = input(
        'The reminder function is being configured, please enter the number to select the reminder time\n[0]Do not reminder\n[1]Reminder 10 minutes before class\n[2]Reminder 30 minutes before class reminder\n[3]Reminder 1 hour before class reminder\n[4]Reminder 2 hours before class reminder\n[5]Reminder 1 day before class reminder \n')
    print("Setting Reminder...")
    setReminder(reminder)

    print("Setting ClassTime...")
    setClassTime()

    print("Handling ClassInfo...")
    classInfoHandle()

    print("Setting Unite...")
    uniteSetting()

    print("Creating and Saving ICS file...")
    icsCreateAndSave()
