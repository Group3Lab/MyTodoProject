"""
搜索筛选菜单
使用依赖注入获取 TaskSystem 实例
筛选、排序全部在本菜单内完成，TaskSystem 只提供完整列表副本
"""

from datetime import date

from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem


class SearchTasksMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__(
            "搜索与筛选",
            "查看未完成/已完成/已逾期，按关键字搜索，按优先级或截止日期排序"
        )
        self.__task_system = task_system

    def execute(self) -> int:
        """搜索与筛选的核心逻辑"""
        try:
            tasks = self.__task_system.get_all_tasks()
            if not tasks:
                print("当前没有任务，无法搜索或筛选")
                return 0

            self.__print_options()
            choice = input("请选择操作（输入 0 返回）: ").strip()
            if choice == "0":
                print("已取消")
                return 0

            matched = self.__select_tasks(tasks, choice)
            if matched is None:
                print("无效的选择，请重新进入菜单")
                return 0

            self.__print_tasks(matched)
            return 0

        except Exception as e:
            print(f"[错误] 搜索失败: {e}")
            return -1

    @staticmethod
    def __print_options():
        print("\n" + "=" * 50)
        print("搜索与筛选")
        print("=" * 50)
        print("1. 只看未完成")
        print("2. 只看已完成")
        print("3. 只看已逾期")
        print("4. 按关键字搜索")
        print("5. 按优先级排序查看")
        print("6. 按截止日期排序查看")
        print("=" * 50)

    def __select_tasks(self, tasks, choice):
        """根据用户选择返回筛选/排序后的任务列表，选择非法时返回 None"""
        if choice == "1":
            return [t for t in tasks if not t.is_completed]
        if choice == "2":
            return [t for t in tasks if t.is_completed]
        if choice == "3":
            return [t for t in tasks if self.__is_overdue(t)]
        if choice == "4":
            return self.__search_by_keyword(tasks)
        if choice == "5":
            return self.__sort_by_priority(tasks)
        if choice == "6":
            return self.__sort_by_due_date(tasks)
        return None

    @staticmethod
    def __is_overdue(task) -> bool:
        """已逾期：未完成、有截止日期、且截止日期早于今天"""
        return (not task.is_completed) and task.has_due_date and task.due_date.date() < date.today()

    def __search_by_keyword(self, tasks):
        """按关键字搜索标题（不区分大小写），结果按关键字在标题中出现的位置排序"""
        keyword = input("请输入搜索关键字: ").strip()
        if not keyword:
            print("关键字为空，显示全部任务")
            return tasks
        lowered = keyword.lower()
        matched = [t for t in tasks if lowered in t.title.lower()]
        # 关键字出现的位置越靠前，排得越前；位置相同按标题字母顺序
        return sorted(matched, key=lambda t: (t.title.lower().find(lowered), t.title.lower()))

    @staticmethod
    def __sort_by_priority(tasks):
        """按优先级排序：高 -> 中 -> 低；同优先级时截止日期早的在前，无截止日期排最后"""
        return sorted(
            tasks,
            key=lambda t: (
                ["高", "中", "低"].index(t.priority.value),
                not t.has_due_date,
                t.due_date,
            ),
        )

    @staticmethod
    def __sort_by_due_date(tasks):
        """按截止日期排序：早的在前，没有截止日期的排最后"""
        return sorted(tasks, key=lambda t: (not t.has_due_date, t.due_date))

    @staticmethod
    def __print_tasks(tasks):
        """打印筛选/排序结果，为空时给出提示"""
        if not tasks:
            print("\n没有符合条件的任务")
            return

        print(f"\n共 {len(tasks)} 条符合条件的任务：")
        for i, task in enumerate(tasks, start=1):
            # 复用 Task 自带的 to_string，保证显示格式与「查看全部」一致
            print(f"{i}. {task.to_string()}")
