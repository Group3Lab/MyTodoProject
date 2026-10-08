"""
添加任务菜单
使用依赖注入获取 TaskSystem 实例
"""

from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem


class AddTaskMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__(
            "添加任务",
            "输入标题新建一条任务"
        )
        self.__task_system = task_system

    def execute(self) -> int:
        """添加任务的核心逻辑"""
        try:
            print("\n" + "="*50)
            print("添加任务")
            print("="*50 + "\n")

            title = input("请输入任务标题（输入 0 取消）: ").strip()
            if title == "0":
                print("已取消添加")
                return 0

            # 标题为空时重新询问，避免创建非法任务
            while not title:
                print("任务标题不能为空")
                title = input("请输入任务标题（输入 0 取消）: ").strip()
                if title == "0":
                    print("已取消添加")
                    return 0

            task = self.__task_system.add(title)
            print(f"\n添加成功：{task.title}")

            print("\n" + "="*50)
            return 0

        except Exception as e:
            print(f"[错误] 添加失败: {e}")
            return -1
