from core.menuModule.menu import Menu
from core.taskModule.task import Priority

class SetPriorityMenu(Menu):
    def __init__(self, task_system):
        super().__init__(
            "设置任务优先级",
            "设置指定任务的优先级",
        )
        self.__task_system = task_system

    def execute(self) -> int:
        total_tasks = self.__task_system.get_task_count()
        if total_tasks == 0:
            print("====任务列表====")
            print("可选优先级:1=LOW低  2=MEDIUM中  3=HIGH高")
        for idx in range(total_tasks):
            task = self.__task_system.get_by_index(idx)
            print(f"{idx + 1}: {task.title}  当前优先级：{task.priority.name}")

        try:
            input_num = int(input("请输入要设置的任务编号: ").strip())
            target_idx = input_num - 1
            if target_idx < 0:
                print("任务编号超出范围！")
                return 0

            p_num = int(input("输入优先级数字(1/2/3): ").strip())
            if p_num == 1:
                p = Priority.LOW
            elif p_num == 2:
                p = Priority.MEDIUM
            elif p_num == 3:
                p = Priority.HIGH
            else:
                print("只能输入1、2、3")
                return 0

            result = self.__task_system.update_priority(target_idx, p)
            if result:
                print("优先级设置成功")
            else:
                print("任务不存在，设置失败")

        except ValueError:
            print("输入格式错误！")
        return 0
