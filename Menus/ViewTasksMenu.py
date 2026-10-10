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

        for i in range(count):
            task = self.__task_system.get_by_index(i)

            # 状态：把 True/False 转成中文
            status = "已完成" if task.is_completed else "未完成"

            # 优先级：task.priority 是枚举，.value 拿到中文 "高"/"中"/"低"
            priority = task.priority.value

            # 截止日期：如果有就格式化成 YYYY-MM-DD，没有就显示"无截止日期"
            if task.has_due_date:
                due_date = task.due_date.strftime("%Y-%m-%d")
            else:
                due_date = "无截止日期"

            # 打印：编号、优先级、标题、截止日期、状态
            print(f"{i + 1}. [{priority}] {task.title} | 截止日期: {due_date} | 状态: {status}")