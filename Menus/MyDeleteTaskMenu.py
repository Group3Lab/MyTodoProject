"""
删除任务菜单
使用依赖注入获取 TaskSystem 实例
"""

from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem


class MyDeleteTaskMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__("删除任务", "删除指定编号的任务")
        self._task_system = task_system
    def execute(self) -> int:
        """菜单的核心逻辑：删除任务"""
        total_tasks = self._task_system.get_task_count()
        if total_tasks == 0:
            print("没有任务可删除。")
            return 0
        print(f"当前共有 {total_tasks} 个任务。")
        print("任务列表：")
        for idx in range(total_tasks):
            task = self._task_system.get_by_index(idx)
    
            print(f"{idx + 1}: {task.title}") 
        try:
            show_num = int(input("请输入要删除的任务编号："))
            idx = show_num - 1
            if idx < 0 or idx >= total_tasks:
                print("任务编号无效，请输入有效的编号。")
                return 0
            confirm = input(f"确认删除任务 '{self._task_system.get_by_index(idx).title}' 吗？(y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("删除操作已取消。")
                return 0
            if self._task_system.delete(idx):
                print("任务已删除。")
            else:
                print("任务编号不存在，删除失败。")
        except ValueError:
            print("输入错误，请输入数字。")
            return 0
