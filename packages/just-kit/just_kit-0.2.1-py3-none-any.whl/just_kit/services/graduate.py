from just_kit.services.service import ServieProvider
from just_kit.auth import Authenticator
from just_kit.utils import *
import json
import time

from typing import TypedDict, List

class Term(TypedDict):
    termcode: str
    termname: str
    selected: bool

class Course(TypedDict):
    name: str
    teacher: str
    location: str
    weekday: str
    weeks: List[int]
    time: List[int] # 例如[1,2]或者[5,6,7,8]

TermsList = List[Term]

import re

def parse_timetable(data:TermsList):
    '''
    解析并提取时间表数据。
    参数：
    data (str): 包含时间表数据的字符串。
    返回：
    list: 包含解析后的时间表数据的列表。
    '''
    
    # 周几到z字段的映射
    week_to_z = {
        'Monday': 'z1',
        'Tuesday': 'z2',
        'Wednesday': 'z3',
        'Thursday': 'z4',
        'Friday': 'z5',
        'Saturday': 'z6',
        'Sunday': 'z7'
    }
    
    current_week = data['week'] #当前是星期几

    
    parsed_courses:List[Course] = []
    
    for row in data['rows']:
        time = 0
        if row['mc'].startswith('上午'):
            time = int(row['mc'].replace('上午',''))
        for z in range(1,8): # z1-7
            z_field = 'z' + str(z)
            if(row[z_field] == None):
                continue
            courses = row[z_field].split('<br/><br/>')
            for course in courses:
                #解析每一个course
                course = course.replace('<br/>','')
                match = re.match(r"(.*?)\[(.*)\] *(.*?)\[(.*?)\]",course)
                if match:
                    groups = match.groups()
                    weeks = re.match(r'连续周 (\d+)-(\d+)周',groups[1]).groups()
                    week_start = int(weeks[0])
                    week_end = int(weeks[1])
                    _c:Course = {
                        'name':groups[0],
                        'teacher':groups[2],
                        'location':groups[3],
                        'weekday':list(week_to_z.values())[z-1],
                        'weeks': list(range(week_start,week_end+1)),
                        'time':time
                    }
                    parsed_courses.append(_c)

    # 合并具有相同weekday和weeks的课程
    merged_courses = {}
    for course in parsed_courses:
        key = (course['weekday'], tuple(course['weeks']))  # 使用weekday和weeks作为键
        if key not in merged_courses:
            merged_courses[key] = course.copy()
            merged_courses[key]['time'] = [course['time']]
        else:
            if course['time'] not in merged_courses[key]['time']:
                merged_courses[key]['time'].append(course['time'])
                merged_courses[key]['time'].sort()  # 保持时间顺序
    
    # 将合并后的课程转换回列表
    parsed_courses = list(merged_courses.values())
    
    
    return parsed_courses


class GraduateServiceProvider(ServieProvider):
    """研究生系统数据提供者"""
    
    SERVICE_URL='http://gmis.just.edu.cn/gmis5/(S(sjma2mgmsw1bjnkgws1g2osy))/oauthlogin/jskjdx'

    def __init__(self, auth:Authenticator):
        """
        初始化查询类
        :param auth: Authenticator实例
        """
        super().__init__(auth)
        self.base = ""
    
    async def get_schedule(self, session, semester):
        """获取指定学期的课表数据
        
        Args:
            session: 已登录的会话
            semester: 学期标识
            
        Returns:
            课表数据列表
        """
        params = {
            "xnxqid": semester
        }
        
        async with session.get(self.base_url, params=params) as resp:
            data = await resp.json()
            return data.get("datas", [])
    
    def login(self):
        resp = self.session.get('http://gmis.just.edu.cn/gmis5/oauthlogin/jskjdx')
        self.base = resp.url # 根据oauth的url作为base url

    def terms(self)->TermsList:
        url = self.base.replace("default/index","default/bindterm") + "?_=" + str(int(time.time() * 1000))  # 添加时间戳参数
        return json.loads(decrypt2(self.session.get(url).text))
    
    def courses(self,term):
        return parse_timetable(json.loads(decrypt2(self.session.post(
            self.base.replace("default/index","pygl/py_kbcx_ew"), #这个表示课程数据的加密地址
            data={
                "kblx": "xs",
                "termcode": term
            }
        ).text)))


