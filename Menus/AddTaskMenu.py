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

            while not title:
                print("任务标题不能为空")
                title = input("请输入任务标题（输入 0 取消）: ").strip()
                if title == "0":
                    print("已取消添加")
                    return 0

            task = self.__task_system.add(title)
            print("\n添加成功！")

            new_index = self.__task_system.get_task_count() - 1
            
            due_date = input("请输入截止日期 ( YYYY-MM-DD，可直接回车跳过)：").strip()
            
            if due_date:
                from datetime import datetime
                try:
                    date_obj = datetime.strptime(due_date, "%Y-%m-%d")
                    self.__task_system.update_due_date(new_index, date_obj)
                except ValueError:
                    print("[警告] 日期格式不对，已跳过设置日期。")
                
            priority_input = input("请输入优先级 (1-3，1为最高，可直接回车跳过)：").strip()
            if priority_input:
                self.__task_system.update_priority(new_index, priority_input)
           
            print("\n" + "="*50)
            return 0

        except Exception as e:
            print(f"[错误] 添加失败: {e}")
            return -1
