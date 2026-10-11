"""
查看所有任务菜单
使用依赖注入获取 TaskSystem 实例
"""
from datetime import date

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
            self.__print_statistics()

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

            # 调用 Task 自带的 to_string 方法显示完整信息
            print(f"{i + 1}. {task.to_string()}")

    def __print_statistics(self):
        """统计并展示任务完成情况"""
        count = self.__task_system.get_task_count()
        completed = 0
        incomplete = 0
        overdue = 0

        for i in range(count):
            task = self.__task_system.get_by_index(i)
            if task.is_completed:
                completed += 1
            else:
                incomplete += 1
                # 已逾期：有截止日期、未完成、且截止日期早于今天
                if task.has_due_date and task.due_date.date() < date.today():
                    overdue += 1

        # 完成率 = 已完成 / 总数 * 100，保留两位小数
        completion_rate = (completed / count * 100) if count > 0 else 0

        print("\n" + "=" * 50)
        print("统计信息")
        print("=" * 50)
        print(f"任务总数: {count}")
        print(f"已完成: {completed}")
        print(f"未完成: {incomplete}")
        print(f"已逾期: {overdue}")
        print(f"完成率: {completion_rate:.2f}%")