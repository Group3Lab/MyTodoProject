from copy import deepcopy
from datetime import datetime
import keyword
from unittest import result

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

    def add(self, newtask: Task) -> Task:
            self.__tasks.append(newtask)
            return newtask

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
    
    def get_filtered_tasks(self, filter_type: str):
        """根据状态筛选任务"""
        from datetime import datetime
        result = []
        if filter_type == "unfinished":
            result = [t for t in self.__tasks if not t.is_completed]
        elif filter_type == "finished":
            result = [t for t in self.__tasks if t.is_completed]
        elif filter_type == "overdue":
            now = datetime.now()
            for t in self.__tasks:
                if not t.is_completed and t.due_date:
                    try:
                        due = datetime.strptime(t.due_date, "%Y-%m-%d")
                        if due < now:
                            result.append(t)
                    except Exception:
                        pass
        return [deepcopy(t) for t in result]

    def search_tasks(self, keyword: str):
           def search_tasks(self, keyword: str):
            """根据关键字搜索任务，并按匹配度排序"""
            if not keyword:
                return [] 
            
            
            keyword = keyword.lower()
    def search_tasks(self, keyword: str):
        """根据关键字搜索任务，并按匹配度排序"""
        if not keyword:
            return []  # 关键字为空直接返回空列表
            
        keyword = keyword.lower()
        scored_results = []  # 用来存 (匹配得分, 任务) 的元组

        for t in self.__tasks:
            title = getattr(t, 'title', '')
            if not isinstance(title, str):
                continue
                
            title_lower = title.lower()
            if keyword in title_lower:
                # 计算匹配度得分：完全匹配 > 开头匹配 > 包含匹配
                if title_lower == keyword:
                    score = 3  # 完全匹配（比如搜"吃饭"，标题就是"吃饭"）
                elif title_lower.startswith(keyword):
                    score = 2  # 开头匹配（比如搜"吃"，标题是"吃饭"）
                else:
                    score = 1  # 包含匹配（比如搜"吃"，标题是"去吃饭"）
                    
                scored_results.append((score, t))

        # 根据得分降序排列（得分高的排在最前面）
        scored_results.sort(key=lambda x: x[0], reverse=True)

        # 提取排好序的任务列表，并返回深拷贝
        result = [item[1] for item in scored_results]
        return [deepcopy(t) for t in result]

    def sort_tasks(self, sort_by: str):
        """对任务进行排序"""
        if sort_by == "priority":
            result = sorted(self.__tasks, key=lambda x: x.priority)
        elif sort_by == "due_date":
            result = sorted(self.__tasks, key=lambda x: x.due_date if x.due_date else "9999-99-99")
        else:
            result = self.__tasks
        return [deepcopy(t) for t in result]