from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem
from core.taskModule.task import Task, Priority
from datetime import datetime

class AddTaskMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__(
            "添加任务",
            "输入标题新建一条任务"
        )
        self.task_system = task_system

    def execute(self) -> int:
        """添加任务的核心逻辑"""
        try:
            print("\n" + "="*50)
            print("添加任务")
            print("="*50 + "\n")

            title = input("请输入任务标题（输入 0 取消）：").strip()
            if title == "0":
                print("已取消添加")
                return 0

            while not title:
                print("任务标题不能为空")
                title = input("请输入任务标题（输入 0 取消）：").strip()
                if title == "0":
                    print("已取消添加")
                    return 0

            # 1. 创建 Task 对象
            new_task = Task(title)
            
            # 2. 调用底层的 add 方法
            task = self.task_system.add(new_task)
            print(f"\n添加成功！{task.title}")

            # 3. 获取索引并补充日期和优先级
            new_index = self.task_system.get_task_count() - 1

            due_date = input("请输入截止日期 (YYYY-MM-DD，回车跳过)：").strip()
            if due_date:
                try:
                    date_obj = datetime.strptime(due_date, "%Y-%m-%d")
                    self.task_system.update_due_date(new_index, date_obj)
                except ValueError:
                    print("[警告] 日期格式不对，已跳过。")

            priority_input = input("请输入优先级 (1-3，回车跳过)：").strip()
            if priority_input:
                try:
                    # 把输入的数字转换成 Priority 枚举
                    p_val = int(priority_input)
                    if p_val == 1:
                        prio = Priority.High
                    elif p_val == 2:
                        prio = Priority.Medium
                    else:
                        prio = Priority.Low
                    self.task_system.update_priority(new_index, prio)
                except ValueError:
                    print("[警告] 优先级输入无效，已跳过。")

            print("\n" + "="*50)
            input("按回车键继续...")
            return 0

        except Exception as e:
            print(f"[错误] 添加失败：{e}")
            return -1