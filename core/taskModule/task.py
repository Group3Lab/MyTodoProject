"""
任务数据模型
定义任务类及其相关操作
"""
from datetime import date, datetime
from enum import Enum
class Priority(Enum):
    High="高" 
    Medium="中"
    Low="低"

class Task:

    # 有新属性要初始化默认值做好封装
    # 不要动参数列表，有新参数先创建在修改
    def __init__(self, title):
        if not title or not title.strip():
            raise ValueError("任务标题不能为空")

        self.__title = title.strip()
        self.__is_completed = False
        self.__has_due_date: bool = False
        self.__due_date:datetime=datetime.now()
        self.__priority:Priority=Priority.Medium

    @property
    def title(self) -> str:
        return self.__title

    @property
    def is_completed(self) -> bool:
        return self.__is_completed

    @is_completed.setter
    def is_completed(self, value: bool):
    #   # 补充防乱写入逻辑    
        if not isinstance(value, bool):
            raise ValueError("is_completed must be a boolean value")
        self.__is_completed = value
    @property
    def due_date(self) -> datetime:
        return self.__due_date
    @due_date.setter
    def due_date(self, value: datetime):
        if not isinstance(value, datetime):
            raise ValueError("due_date must be a datetime object")
        self.__due_date = value
        self.__has_due_date = True
    @property
    def has_due_date(self) -> bool:
        return self.__has_due_date
    @property
    def priority(self) -> Priority:
        return self.__priority
    @priority.setter
    def priority(self, value: Priority):
        if not isinstance(value, Priority):
            raise ValueError("priority must be an instance of Priority Enum")
        self.__priority = value


    def to_string(self):
        """把任务信息转成一行字符串"""
        # 状态：把 True/False 转成中文
        status = "已完成" if self.is_completed else "未完成"

        # 优先级：枚举 .value 拿到中文 "高"/"中"/"低"
        priority = self.priority.value

        # 截止日期：如果有就格式化成 YYYY-MM-DD，没有就显示"无截止日期"
        if self.has_due_date:
            due_date = self.due_date.strftime("%Y-%m-%d")
        else:
            due_date = "无截止日期"

        # 返回：标题、优先级、截止日期、是否完成

        return f"{self.title} | {priority} | {due_date} | {status}"