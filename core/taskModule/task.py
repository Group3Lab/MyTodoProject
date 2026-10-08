"""
任务数据模型
定义任务类及其相关操作
"""

class Task:

    # 有新属性要初始化默认值做好封装
    def __init__(self, title, is_completed: bool=False):
        if not title or not title.strip():
            raise ValueError("任务标题不能为空")

        self.__title = title.strip()
        #self.__is_completed = is_completed

    @property
    def title(self) -> str:
        return self.__title

    #@property
    #def is_completed(self) -> bool:
    #    return self.__is_completed

    #@is_completed.setter
    #def is_completed(self, value: bool):
    #    # 补充防乱写入逻辑
    #    self.__is_completed = value

    #def to_string(self):
    #    # 提示：老师要求的格式更复杂，包含优先级和日期，自己改！
    #    return f"{self.title}|{self.is_completed}"