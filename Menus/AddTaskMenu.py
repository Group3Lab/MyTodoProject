"""
添加任务菜单
使用依赖注入获取 TaskSystem 实例
"""

from datetime import datetime

from core.menuModule.menu import Menu
from core.taskModule.task import Priority, Task
from core.taskModule.taskSystem import TaskSystem


class AddTaskMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__(
            "添加任务",
            "输入标题、优先级和截止日期新建一条任务"
        )
        self.__task_system = task_system

    @staticmethod
    def __parse_due_date(date_input: str) -> datetime:
        """把用户输入的日期字符串解析成 datetime，支持 yyyy-mm-dd / yyyy/mm/dd"""
        if "/" in date_input:
            return datetime.strptime(date_input, "%Y/%m/%d")
        return datetime.strptime(date_input, "%Y-%m-%d")

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

            # 标题合法后再创建任务，非法数据由 Task 抛异常兜底
            task = Task(title)

            # 优先级：留空默认「中」，其余按数字映射
            priority_input = input("输入优先级数字(1=低/2=中/3=高，留空默认中): ").strip()
            if priority_input:
                if priority_input == "1":
                    task.priority = Priority.Low
                elif priority_input == "2":
                    task.priority = Priority.Medium
                elif priority_input == "3":
                    task.priority = Priority.High
                else:
                    print("优先级数字无效，已使用默认优先级「中」")

            # 截止日期：留空表示没有截止日期
            date_input = input("输入截止日期(支持 yyyy-mm-dd / yyyy/mm/dd，留空则无): ").strip()
            if date_input:
                try:
                    task.due_date = self.__parse_due_date(date_input)
                except ValueError:
                    print("日期格式错误，已跳过截止日期设置")

            self.__task_system.add(task)
            print(f"\n添加成功：{task.to_string()}")

            print("\n" + "="*50)
            return 0

        except Exception as e:
            print(f"[错误] 添加失败: {e}")
            return -1
