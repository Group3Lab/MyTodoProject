from copy import deepcopy
from datetime import datetime

from core.taskModule.taskSL import taskSave

from .task import Priority, Task


class TaskSystem:
    """任务管理系统"""

    def __init__(self):
        self.__tasks = []

    # 备用构造函数：用已有的任务列表创建一个 TaskSystem
    @classmethod
    def CreateFromList(cls, tasks: list[Task]) -> "TaskSystem":
        obj = cls()
        if tasks:
            obj.__tasks = list(tasks)
        return obj

    def add(self, title: str) -> Task:
        task = Task(title)
        self.__tasks.append(task)
        return task

    # 返回本身（引用）,内部使用，修改数据请走专用方法
    def _get_by_index(self, idx: int) -> Task:
        if 0 <= idx <= len(self.__tasks)-1:
            return self.__tasks[idx]
        return None

    # 返回副本，只给查不给改
    def get_by_index(self, idx):
        task = self._get_by_index(idx)
        if task:
            return deepcopy(task)
        return None

    def delete(self, idx: int) -> bool:
        task = self._get_by_index(idx)
        if task:
            self.__tasks.pop(idx)
            return True
        return False

    def get_task_count(self) -> int:
        """获取任务总数"""
        return len(self.__tasks)

    # 保存数据
    def Save(self) -> bool:
        return taskSave(self.__tasks)

    # -----------分割线------------
    # 修改属性的代码写在后面，注意属性和修改的方法一一对应

    def update_completed(self, idx: int, status: bool) -> bool:
       """更新任务的完成状态"""
       task = self._get_by_index(idx)
       if task:
            task.is_completed = status
            return True
       return False
    def update_due_date(self, idx: int, due_date: datetime) -> bool:
        """更新任务的截止日期"""
        task = self._get_by_index(idx)
        if task:
            task.due_date = due_date
            return True
        return False
    
    def update_priority(self, idx: int, priority: Priority) -> bool:
        """更新任务的优先级"""
        task = self._get_by_index(idx)
        if task:
            task.priority = priority
            return True
        return False
