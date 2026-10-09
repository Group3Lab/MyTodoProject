from datetime import datetime
from core.menuModule.menu import Menu
from taskSystem import TaskSystem

class SetDueDateMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__(
            "设置截止日期",
            "为指定任务设置截止日期",
        )
        self.__task_system=task_system

    def execute(self) -> int:
        total_tasks = self.__task_system.get_task_count()
        if total_tasks == 0:
            print("暂无任务，无法设置截止日期")
            return 0

        print("====任务列表====")
        for idx in range(total_tasks):
            task = self.__task_system.get_by_index(idx)
            status = "已设置截止日期" if task.has_due_date else "未设置截止日期"
            print(f"{idx + 1}: {task.title}  {status}")

        try:
            input_num = int(input("请输入要设置的任务编号："))
            target_idx = input_num - 1
            if target_idx < 0 or target_idx >= total_tasks:
                #规定上界，任务编号上下界校验
                print("任务编号超出范围！")
                return 0

            date_input = input("输入截止日期(支持 yyyy-mm-dd / yyyy/mm/dd): ").strip()
            if "/" in date_input:
                parsed_date = datetime.strptime(date_input, "%Y/%m/%d")
            else:
                parsed_date = datetime.strptime(date_input, "%Y-%m-%d")

            result = self.__task_system.update_due_date(target_idx, parsed_date)
            if result:
                print("截止日期设置成功")
            else:
                print("任务不存在，设置失败")

        except ValueError:
            print("输入格式错误！")
        return 0