"""
查看所有任务菜单
使用依赖注入获取 TaskSystem 实例
"""

from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem


class ViewTasksMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__(
            "查看全部任务",
            "显示所有任务的详细信息"
        )
        self.__task_system = task_system

    def execute(self) -> int:
        """查看任务的核心逻辑"""
        try:
            print("\n" + "="*50)
            print("任务清单")
            print("="*50 + "\n")

            self.__print_all_tasks()

            print("\n" + "="*50)
            return 0

        except Exception as e:
            print(f"[错误] 查看失败: {e}")
            return -1

    def __print_all_tasks(self):
        """列出所有任务"""
        count = self.__task_system.get_task_count()
        if count == 0:
            print("当前没有任务")
            return

        #for i in range(count):
        #    task = self.__task_system.get_by_index(i)
        #    status = "已完成" if task.is_completed else "未完成"
        #    print(f"{i + 1}. {task.title} [{status}]")
