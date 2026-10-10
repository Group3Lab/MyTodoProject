from copy import deepcopy

from core.taskModule.taskSL import taskSave

from .task import Priority, Task


class TaskSystem:
    """任务管理系统"""

    def __init__(self):
        self.__tasks = []

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

    def _get_by_index(self, idx: int) -> Task:
        if 0 <= idx <= len(self.__tasks)-1:
            return self.__tasks[idx]
        return None

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


    def update_completed(self, idx: int, status: bool) -> bool:
       """更新任务的完成状态"""
       task = self._get_by_index(idx)
       if task:
            task.is_completed = status
            return True
       return False
    def update_due_date(self, idx: int, due_date: str) -> bool:
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

    from datetime import datetime

    def get_filtered_tasks(self, filter_type: str):
        """根据状态筛选任务"""
        from datetime import datetime  # 保证 import 在函数内部
        result = []  # 必须初始化
        if filter_type == "unfinished":
            result = [t for t in self._tasks if not t.is_completed]
        elif filter_type == "finished":
            result = [t for t in self._tasks if t.is_completed]
        elif filter_type == "overdue":
            now = datetime.now()
            for t in self._tasks:
                if not t.is_completed and t.due_date:
                    try:
                        due = datetime.strptime(t.due_date, "%Y-%m-%d")
                        if due < now:
                            result.append(t)
                    except Exception:
                        pass
        return [deepcopy(t) for t in result]

        def search_tasks(self, keyword: str):
            keyword = keyword.lower()
        result = []
        for t in self._tasks:
            title = getattr(t, 'title', '')
            if isinstance(title, str) and keyword in title.lower():
                result.append(t)
        return [deepcopy(t) for t in result]

    def sort_tasks(self, sort_by: str):
        """对任务进行排序"""
        if sort_by == "priority":
            result = sorted(self._tasks, key=lambda x: x.priority)
        elif sort_by == "due_date":
            result = sorted(self._tasks, key=lambda x: x.due_date if x.due_date else "9999-99-99")
        else:
            result = self._tasks
        return [deepcopy(t) for t in result]