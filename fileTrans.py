# -*- coding: UTF-8 -*-
import json
import pprint
import copy
import time
import datetime
import sys
from lxml import etree
from random import Random

filename = ['18-19-1.html', '18-19-2.html', '19-20-1.html']

with open('{}'.format(filename[1]), 'r', encoding='utf-8') as f:
    text = f.read()

tree = etree.HTML(text)
gClass = tree.xpath('//div[@id="UpdatePanel4"]//tr[position()>1]/td/text()')

# 格式化
index = 0
cTableTemp = [[], [], [], [], [], [], []]
cTable = ([], [], [], [], [], [], [])
for get in gClass:
    if index % 8 == 0:
        pass
    else:
        cTableTemp[index % 8 - 1].append(get)
    index += 1

classInfoTemp = list()
classInfoList = list()
for i in range(7):
    num = 0
    classToday = list()  # 包含今日课表的列表
    for info in cTableTemp[i]:
        num += 1
        if info == '\xa0':
            continue  # 没有课不进行处理
        infoList = info.split('/')[:-1]  # ex: ['计算机科学与技术导论 W1102  13-16,']
        for x in infoList:
            temp = x.split()  # ex: ['计算机科学与技术导论', 'W1102', '13-16,']
            if len(temp) == 2:
                temp.insert(1, 'Unknow')
            if len(temp) == 3:
                temp.insert(2, '3')
            if len(temp) == 4:  # 3:不分 1:单周 2:双周
                if temp[2] == '单':
                    temp[2] = '1'
                elif temp[2] == '双':
                    temp[2] = '2'
            temp.append(i + 1)  # 星期几
            temp.append(num)  # 第几节课

            classToday.append(temp)

    # 配置课的开始结束时间(课)
    classDict = dict()
    for eclass in classToday:
        className = eclass[0]
        if className not in classDict:
            eclass.append(1)
            classDict[className] = eclass
        else:
            classDict[className][6] += 1

    # 生成课程信息列表
    for eclass in classDict.values():
        classInfoTemp.append(eclass)

for eclass in classInfoTemp:
    cWeek = eclass[3].split(',')
    del eclass[3]
    for week in cWeek:
        if week != '':
            gweek = map(int, week.split('-'))
            tpweek = copy.deepcopy(eclass)
            tpweek.extend(gweek)
            classInfoList.append(tpweek)

pprint.pprint(classInfoList)
"""
[    0  ,  1 ,  2  , 3  ,    4    ,      5    ,  6  ,   7  ,   8       ,  9    ,  10   , 11]
[课程名称,教室,单双周,星期,第一课时间,一次的课时数,开始周,结束周,上课日期List,CREATED,DTSTAMP,UID]
"""


checkFirstWeekDate = 0
checkReminder = 1

YES = 0
NO = 1

DONE_firstWeekDate = time.time()
DONE_reminder = ""
DONE_EventUID = ""
DONE_UnitUID = ""
DONE_CreatedTime = ""
DONE_ALARMUID = ""


classTimeList = []


def main():

    basicSetting()
    uniteSetting()
    classInfoHandle()
    icsCreateAndSave()


def save(string):
    f = open("class.ics", 'wb')
    f.write(string.encode("utf-8"))
    f.close()


def icsCreateAndSave():
    icsString = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:课程表\nPRODID:-//Apple Inc.//Mac OS X 10.12//EN\nX-APPLE-CALENDAR-COLOR:#FC4208\nX-WR-TIMEZONE:Asia/Shanghai\nCALSCALE:GREGORIAN\nBEGIN:VTIMEZONE\nTZID:Asia/Shanghai\nBEGIN:STANDARD\nTZOFFSETFROM:+0900\nRRULE:FREQ=YEARLY;UNTIL=19910914T150000Z;BYMONTH=9;BYDAY=3SU\nDTSTART:19890917T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0800\nEND:STANDARD\nBEGIN:DAYLIGHT\nTZOFFSETFROM:+0800\nDTSTART:19910414T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0900\nRDATE:19910414T000000\nEND:DAYLIGHT\nEND:VTIMEZONE\n"
    global classTimeList, DONE_ALARMUID, DONE_UnitUID
    eventString = ""
    for classInfo in classInfoList:
        # i = int(classInfo["classTime"]-1)
        classBegin = classInfo[4]-1
        classTimes = classInfo[5]
        className = classInfo[0]+"|"+classInfo[1]
        endTime = classTimeList[classBegin+classTimes-1]["endTime"]
        startTime = classTimeList[classBegin]["startTime"]
        index = 0
        for date in classInfo[8]:
            eventString = eventString + \
                "BEGIN:VEVENT\nCREATED:"+classInfo[9]
            eventString = eventString+"\nUID:"+classInfo[11][index]
            eventString = eventString+"\nDTEND;TZID=Asia/Shanghai:"+date+"T"+endTime
            eventString = eventString + \
                "00\nTRANSP:OPAQUE\nX-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\nSUMMARY:"+className
            eventString = eventString+"\nDTSTART;TZID=Asia/Shanghai:"+date+"T"+startTime+"00"
            eventString = eventString+"\nDTSTAMP:" + \
                DONE_CreatedTime  # classInfo["CREATED"]
            eventString = eventString+"\nSEQUENCE:0\nBEGIN:VALARM\nX-WR-ALARMUID:"+DONE_ALARMUID
            eventString = eventString+"\nUID:"+DONE_UnitUID
            eventString = eventString+"\nTRIGGER:"+DONE_reminder
            eventString = eventString+"\nDESCRIPTION:事件提醒\nACTION:DISPLAY\nEND:VALARM\nEND:VEVENT\n"

            index += 1
    icsString = icsString + eventString + "END:VCALENDAR"
    save(icsString)
    print("icsCreateAndSave")


def classInfoHandle():
    global classInfoList
    global DONE_firstWeekDate
    i = 0

    for classInfo in classInfoList:
        # 具体日期计算出来

        startWeek = classInfo[6]
        endWeek = classInfo[7]
        weekday = classInfo[3]
        week = int(classInfo[2])
        dateLength = float((startWeek - 1) * 7)
        startDate = datetime.datetime.fromtimestamp(int(time.mktime(
            DONE_firstWeekDate))) + datetime.timedelta(days=dateLength + weekday - 1)
        string = startDate.strftime('%Y%m%d')

        dateLength = float((endWeek - 1) * 7)
        endDate = datetime.datetime.fromtimestamp(int(time.mktime(
            DONE_firstWeekDate))) + datetime.timedelta(days=dateLength + weekday - 1)


        date = startDate
        dateList = []
        if (week == 3): dateList.append(string)
        if ((week == 2) and (startWeek%2==0)): dateList.append(string)
        if ((week == 1) and (startWeek%2==1)): dateList.append(string)
        i = NO
        w = startWeek+1
        while (i):
            date = date + datetime.timedelta(days = 7.0)
            if(date > endDate):
                i = YES
            if(week == 3):
                string = date.strftime('%Y%m%d')
                dateList.append(string)
            if ((week == 1) and (w%2 == 1)):
                string = date.strftime('%Y%m%d')
                dateList.append(string)
            if ((week == 2) and (w%2 == 0)):
                string = date.strftime('%Y%m%d')
                dateList.append(string)
            w=w+1
        classInfo.append(dateList)

        # 设置 UID
        global DONE_CreatedTime, DONE_EventUID
        CreateTime()
        classInfo.append(DONE_CreatedTime)
        classInfo.append(DONE_CreatedTime)
        UID_List = []
        for date in dateList:
            UID_List.append(UID_Create())
        classInfo.append(UID_List)
    print("classInfoHandle")


def UID_Create():
    return random_str(20) + "&Chanjh.com"


def CreateTime():
    # 生成 CREATED
    global DONE_CreatedTime
    date = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    DONE_CreatedTime = date + "Z"
    # 生成 UID
    # global DONE_EventUID
    # DONE_EventUID = random_str(20) + "&Chanjh.com"

    print("CreateTime")


def uniteSetting():
    #
    global DONE_ALARMUID
    DONE_ALARMUID = random_str(30) + "&Chanjh.com"
    #
    global DONE_UnitUID
    DONE_UnitUID = random_str(20) + "&Chanjh.com"
    print("uniteSetting")


def setClassTime():
    data = []
    with open('conf_classTime.json', 'r') as f:
        data = json.load(f)
    global classTimeList
    classTimeList = data["classTime"]
    print("setclassTime")

# def setClassInfo():
# 	data = []
# 	with open('conf_classInfo.json', 'r') as f:
# 		data = json.load(f)
# 	global classInfoList
# 	classInfoList = data["classInfo"]
# 	print("setClassInfo:")


def setFirstWeekDate(firstWeekDate):
    global DONE_firstWeekDate
    DONE_firstWeekDate = time.strptime(firstWeekDate, '%Y%m%d')
    print("setFirstWeekDate:", DONE_firstWeekDate)


def setReminder(reminder):
    global DONE_reminder
    reminderList = ["-PT10M", "-PT30M", "-PT1H", "-PT2H", "-P1D"]
    if(reminder == "1"):
        DONE_reminder = reminderList[0]
    elif(reminder == "2"):
        DONE_reminder = reminderList[1]
    elif(reminder == "3"):
        DONE_reminder = reminderList[2]
    elif(reminder == "4"):
        DONE_reminder = reminderList[3]
    elif(reminder == "5"):
        DONE_reminder = reminderList[4]
    else:
        DONE_reminder = "NULL"

    print("setReminder", reminder)


def checkReminder(reminder):
    # TODO

    print("checkReminder:", reminder)
    List = ["0", "1", "2", "3", "4", "5"]
    for num in List:
        if (reminder == num):
            return YES
    return NO


def checkFirstWeekDate(firstWeekDate):
    # 长度判断
    if(len(firstWeekDate) != 8):
        return NO

    year = firstWeekDate[0:4]
    month = firstWeekDate[4:6]
    date = firstWeekDate[6:8]
    dateList = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # 年份判断
    if(int(year) < 1970):
        return NO
    # 月份判断
    if(int(month) == 0 or int(month) > 12):
        return NO
    # 日期判断
    if(int(date) > dateList[int(month)-1]):
        return NO

    print("checkFirstWeekDate:", firstWeekDate)
    return YES


def basicSetting():
    info = "欢迎使用课程表生成工具。\n接下来你需要设置一些基础的信息方便生成数据\n"
    print(info)

    info = "请设置第一周的星期一日期(如：20160905):\n"
    firstWeekDate = input(info)
    checkInput(checkFirstWeekDate, firstWeekDate)

    info = "正在配置上课时间信息……\n"
    print(info)
    try:
        setClassTime()
        print("配置上课时间信息完成。\n")
    except:
        print('Error')

    # info = "正在配置课堂信息……\n"
    # print(info)
    # try :
    # 	setClassInfo()
    # 	print("配置课堂信息完成。\n")
    # except :
    # 	print('Error')

    info = "正在配置提醒功能，请输入数字选择提醒时间\n【0】不提醒\n【1】上课前 10 分钟提醒\n【2】上课前 30 分钟提醒\n【3】上课前 1 小时提醒\n【4】上课前 2 小时提醒\n【5】上课前 1 天提醒\n"
    reminder = input(info)
    checkInput(checkReminder, reminder)


def checkInput(checkType, input):
    if(checkType == checkFirstWeekDate):
        if (checkFirstWeekDate(input)):
            info = "输入有误，请重新输入第一周的星期一日期(如：20160905):\n"
            firstWeekDate = input(info)
            checkInput(checkFirstWeekDate, firstWeekDate)
        else:
            setFirstWeekDate(input)
    elif(checkType == checkReminder):
        if(checkReminder(input)):
            info = "输入有误，请重新输入\n【1】上课前 10 分钟提醒\n【2】上课前 30 分钟提醒\n【3】上课前 1 小时提醒\n【4】上课前 2 小时提醒\n【5】上课前 1 天提醒\n"
            reminder = input(info)
            checkInput(checkReminder, reminder)
        else:
            setReminder(input)

    else:
        print("程序出错了……")
    # end


def random_str(randomlength):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


main()
