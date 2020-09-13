import re
import uuid
import json
from ical import ICal
from lxml import etree


def classHandler(table):
    classmatrix = [tr.xpath('./td[position()>1]/text()')
                   for tr in table.xpath('tr[position()>1]')]
    classmatrixT = [each for each in zip(*classmatrix)]
    oeDict = {'单': 1, '双': 2}
    courseInfo = dict()

    for day, courses in enumerate(classmatrixT):
        for time, course_cb in enumerate(courses):
            course_list = list(filter(None, course_cb.split('/')))
            for course in course_list:
                id = uuid.uuid3(uuid.NAMESPACE_DNS, course+str(day)).hex
                if course != '\xa0' and (not time or id not in courseInfo.keys()):
                    res = re.match(
                        r'(\S+) *(\w+)? *([单双]?) *((\d+-\d+,?)+)', course)
                    assert res, "Course information parsing abnormal"
                    info = {
                        'classname': res.group(1),
                        'classtime': [time+1],
                        'day': day+1,
                        'week': list(filter(None, res.group(4).split(','))),
                        'oe': oeDict.get(res.group(3), 3),
                        'classroom': res.group(2),
                    }
                    courseInfo[id] = info
                elif course != '\xa0' and id in courseInfo.keys():
                    courseInfo[id]['classtime'].append(time+1)

    return [course for course in courseInfo.values()]


if __name__ == '__main__':
    with open('./note', 'r', encoding='utf-8') as f:
        text = etree.HTML(f.read())
    with open('../conf_classTime.json', encoding='utf-8') as f:
        schedule = json.load(f)['classTime']
    tbody = text.xpath('//div/table/tbody')[0]
    courseInfo = classHandler(tbody)
    iCal = ICal.withStrDate('20200914', schedule, courseInfo)
    res = iCal.to_ical()
    with open('./class.ics', 'w', encoding='utf-8') as f:
        f.write(res)
