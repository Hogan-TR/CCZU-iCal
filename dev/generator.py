import re
import uuid
import json
from ical import ICal
from lxml import etree


def classHandler(text):
    # structure text
    textDom = etree.HTML(text)
    tables = textDom.xpath('//div/table')
    tableup, tabledown = tables[1], tables[2]
    # extract all class names
    classNameList = tableup.xpath(
        './tr[@class="dg1-item"]/td[position()=2]/text()')
    # extract class info of from the table
    classmatrix = [tr.xpath('./td[position()>1]/text()')
                   for tr in tabledown.xpath('tr[position()>1]')]
    classmatrixT = [each for each in zip(*classmatrix)]
    oeDict = {'单': 1, '双': 2}
    courseInfo = dict()
    courseList = dict()

    # day: day of week / courses: all courses in a day
    for day, courses in enumerate(classmatrixT):
        # time: the rank of lesson / course_cb: one item in table cell
        for time, course_cb in enumerate(courses):
            course_list = list(filter(None, course_cb.split('/')))
            for course in course_list:
                id = uuid.uuid3(uuid.NAMESPACE_DNS, course+str(day)).hex
                if course != '\xa0' and (not time or id not in courseInfo.keys()):
                    nl = list(
                        filter(lambda x: course.startswith(x), classNameList))
                    assert len(nl) == 1, "Unable to resolve course name correctly"
                    classname = nl[0]
                    course = course.replace(classname, '').strip()
                    res = re.match(
                        r'(\w+)? *([单双]?) *((\d+-\d+,?)+)', course)
                    assert res, "Course information parsing abnormal"
                    info = {
                        'classname': classname,
                        'classtime': [time+1],
                        'day': day+1,
                        'week': list(filter(None, res.group(3).split(','))),
                        'oe': oeDict.get(res.group(2), 3),
                        'classroom': [res.group(1)],
                    }
                    courseInfo[id] = info
                elif course != '\xa0' and id in courseInfo.keys():
                    courseInfo[id]['classtime'].append(time+1)

    for course in courseInfo.values():
        purecourse = {key: value for key,
                      value in course.items() if key != "classroom"}
        if str(purecourse) in courseList:
            courseList[str(purecourse)]["classroom"].append(
                course["classroom"][0])
        else:
            courseList[str(purecourse)] = course

    return [course for course in courseList.values()]


if __name__ == '__main__':
    with open('./note', 'r', encoding='utf-8') as f:
        text = f.read()
    with open('../conf_classTime.json', encoding='utf-8') as f:
        schedule = json.load(f)['classTime']
    courseInfo = classHandler(text)
    # with open("save.json", "w", encoding="utf-8") as f:
    #     import json
    #     json.dump(courseInfo, f, ensure_ascii=False)
    iCal = ICal.withStrDate('20200914', schedule, courseInfo)
    res = iCal.to_ical()
    with open('./class.ics', 'w', encoding='utf-8') as f:
        f.write(res)
