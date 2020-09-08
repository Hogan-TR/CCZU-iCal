import time
import datetime


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

    def test(self):
        x = map(self.handler, self.courseInfo)
        from pprint import pprint
        pprint(list(x))


ge = ICal.withStrDate('20200914', [], [{
    "classname": "信息安全",
    "classtime": [8, 9],
    "day": 5,
    "week": ['1-16'],
    "oe": 1,
    "classroom": ["W1101"],
    "teacher": ["王波", "Joh"],
}])

ge.test()
