# CCZU-iCal

一个从常州大学教务系统快速提取课表，生成iCal格式文件(.ics)，从而实现**全平台**原生日历显示课表的脚本工具。



## 特点

- 在Windows、macOS、iOS、Android、Windows Phone等系统，以及各大邮箱服务都有着强大的**原生支持**
- 免去第三方课表应用的流氓推广、无用社交功能，以及保持后台提醒推送时的耗电情况，实现功能的**轻量化**
- 得益于云同步的功能，只需一个设备导入课表，其他关联设备都可**同步显示**

小贴士：现在几乎所有手机的左侧副屏都有日历提醒功能哦，真的巨方便



## 运行

开始前请先确认已具备Python3环境

```shell
# 下载代码
git clone https://github.com/Hogan-TR/CCZU-iCal.git
cd CCZU-iCal

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate    # Windows
source ./venv/bin/activate # Linux

# 安装依赖
pip install -r requirements.txt

# 运行
python script.py           # Windows
sudo python3 script.py     # Linux

# 然后根据提示一次键入
* 教务系统学号 + 密码
* 学期第一周周一日期
* 课前提醒时间
```



## ics文件使用

这边有超详细的使用指南（本人太**，直接上链接）

 :star2:  ​[华南师范大学 iCal课表使用指引](https://i.scnu.edu.cn/ical/doc#%E5%AF%BC%E5%85%A5%E7%9A%84%E6%AD%A5%E9%AA%A4)



## 待办

- [x] 课前提醒功能

- [x] 课程的单双周差异，及特殊情况

- [ ] 不同校区作息时间不同

- [ ] 搭建网页，实现可视化日历**订阅**，降低使用门槛

  

## ideal Get

:pray:  贴个友链： [Gill Blog](http://chanjh.com/post/0031/)  (感谢这位大佬提供的ideal)
