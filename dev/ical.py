import time
import datetime
import uuid
from icalendar import Calendar, Event


class ICal(object):
    def __init__(self, firstWeekDate, schedule, courseInfo):
        self.firstWeekDate = firstWeekDate
        self.schedule = schedule
        self.courseInfo = courseInfo

    @classmethod
    def withStrDate(cls, strdate, *args):
        firstWeekDate = time.strptime(strdate, "%Y%m%d")
        return cls(firstWeekDate, *args)

    def handler(self, info):
        weekday = info["day"]
        oe = info["oe"]
        firstDate = datetime.datetime.fromtimestamp(
            int(time.mktime(self.firstWeekDate)))
        info['daylist'] = list()

        for weeks in info["week"]:
            startWeek, endWeek = map(int, weeks.split('-'))
            startDate, endDate = firstDate + datetime.timedelta(days=(float(
                (startWeek - 1) * 7) + weekday - 1)), firstDate + datetime.timedelta(days=(float((endWeek - 1) * 7) + weekday - 1))

            status = True
            date = startDate
            w = startWeek
            while(status):
                if(oe == 3 or (oe == 1) and (w % 2 == 1) or (oe == 2) and(w % 2 == 0)):
                    info['daylist'].append(date.strftime("%Y%m%d"))
                date = date + datetime.timedelta(days=7.0)
                w = w + 1
                if(date > endDate):
                    status = False
        return info

    def to_ical(self):
        prop = {
            'PRODID': '-//Google Inc//Google Calendar 70.9054//EN',
            'VERSION': '2.0',
            'CALSCALE': 'GREGORIAN',
            'METHOD': 'PUBLISH',
            'X-WR-CALNAME': '课程表',
            'X-WR-TIMEZONE': 'Asia/Shanghai'
        }
        cal = Calendar()
        for key, value in prop.items():
            cal.add(key, value)

        courseInfo = map(self.handler, self.courseInfo)
        for course in courseInfo:
            startTime = self.schedule[course['classtime'][0]-1]['startTime']
            endTime = self.schedule[course['classtime'][-1]-1]['endTime']
            createTime = datetime.datetime.now()
            for day in course['daylist']:
                sub_prop = {
                    'CREATED': createTime,
                    'SUMMARY': "{0} | {1}".format(course['classname'], course['classroom']),
                    'UID': uuid.uuid4().hex + '@google.com',
                    'DTSTART': datetime.datetime.strptime(day+startTime, '%Y%m%d%H%M'),
                    'DTEND': datetime.datetime.strptime(day+endTime, '%Y%m%d%H%M'),
                    'DTSTAMP': createTime,
                    'LAST-MODIFIED': createTime,
                    'SEQUENCE': '0',
                    'TRANSP': 'OPAQUE',
                    'X-APPLE-TRAVEL-ADVISORY-BEHAVIOR': 'AUTOMATIC'
                }
                event = Event()
                for key, value in sub_prop.items():
                    event.add(key, value)
                cal.add_component(event)

        return bytes.decode(cal.to_ical(), encoding='utf-8').replace('\r\n', '\n').strip()
