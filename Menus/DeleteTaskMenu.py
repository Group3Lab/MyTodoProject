"""
删除任务菜单
使用依赖注入获取 TaskSystem 实例
"""

from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem


class DeleteTaskMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__(
            "删除任务",
            "按编号删除任务，删除前需要二次确认"
        )
        self.__task_system = task_system

    def execute(self) -> int:
        """删除任务的核心逻辑"""
        try:
            print("\n" + "="*50)
            print("删除任务")
            print("="*50 + "\n")

            count = self.__task_system.get_task_count()
            if count == 0:
                print("当前没有任务")
                print("\n" + "="*50)
                return 0

            self.__print_all_tasks(count)

            # 编号以「查看全部任务」的编号为准
            index = self.__read_index(count)
            if index < 0:
                print("已取消删除")
                return 0

            task = self.__task_system.get_by_index(index)

            # 二次确认，避免误删
            confirm = input(f"确认删除「{task.title}」吗？(y/N): ").strip().lower()
            if confirm != "y":
                print("已取消删除")
                return 0

            if self.__task_system.delete(index):
                print("\n删除成功")
            else:
                print("\n删除失败，任务不存在")

            print("\n" + "="*50)
            return 0

        except Exception as e:
            print(f"[错误] 删除失败: {e}")
            return -1

    def __print_all_tasks(self, count: int):
        """列出所有任务，供用户选择编号"""
        print("当前任务清单：\n")
        for i in range(count):
            task = self.__task_system.get_by_index(i)
            print(f"{i + 1}. {task.title}")
        print()

    def __read_index(self, count: int) -> int:
        """读取要删除的任务编号，返回下标；取消或非法输入返回 -1"""
        raw = input("请输入要删除的任务编号（输入 0 取消）: ").strip()
        try:
            number = int(raw)
        except ValueError:
            print("非法输入，请重新选择")
            return -1

        if number == 0:
            return -1

        if number < 1 or number > count:
            print("输入超出范围，请重新选择")
            return -1

        return number - 1
