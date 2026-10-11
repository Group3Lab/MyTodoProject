#导入datetime, Menu,TaskSystem 类,及需要用到的类和模块
from datetime import datetime
from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem

#定义 SetDueDateMenu 类，继承自 Menu 类
class SetDueDateMenu(Menu):
    #初始化 SetDueDateMenu 类的构造函数，接收一个 TaskSystem 实例作为参数
    def __init__(self, task_system: TaskSystem):
        # 调用父类 Menu 的构造函数
        super().__init__( 
            # 设置菜单标题和描述
            "设置截止日期",
            "为指定任务设置截止日期",
        )
        #把传入的 TaskSystem 实例赋值给私有属性 __task_system
        self.__task_system=task_system
        
    #定义 execute 方法，返回类型为 int
    def execute(self) -> int:
        #调用任务系统的 get_task_count 方法获取任务总数
        total_tasks = self.__task_system.get_task_count()
        if total_tasks == 0:
            print("暂无任务，无法设置截止日期")
            return 0

        print("====任务列表====")
        #遍历任务列表，显示每个任务的标题和截止日期状态
        for idx in range(total_tasks):
            #调用任务系统的 get_by_index 方法获取指定索引的任务
            task = self.__task_system.get_by_index(idx)
            #根据任务是否设置了截止日期，显示不同的状态信息
            status = "已设置截止日期" if task.has_due_date else "未设置截止日期"
            #用户界面显示任务编号（从1开始）、标题和截止日期状态
            print(f"{idx + 1}: {task.title}  {status}")
    
        #提示用户输入要设置截止日期的任务编号
        try:
            #提示用户输入任务编号，并将输入转换为整数
            input_num = int(input("请输入要设置的任务编号："))
            #将用户输入的任务编号转换为索引（从0开始）
            target_idx = input_num - 1
            #检查用户输入的任务编号是否在有效范围内
            if target_idx < 0 or target_idx >= total_tasks:
                #规定上界，任务编号上下界校验
                print("任务编号超出范围！")
                return 0

            #提示用户输入截止日期，支持两种格式：yyyy-mm-dd 或 yyyy/mm/dd
            date_input = input("输入截止日期(支持 yyyy-mm-dd / yyyy/mm/dd): ").strip()
            #根据用户输入的日期格式，使用 datetime.strptime 方法解析日期字符串为 datetime 对象
            if "/" in date_input:
                parsed_date = datetime.strptime(date_input, "%Y/%m/%d")
            else:
                parsed_date = datetime.strptime(date_input, "%Y-%m-%d")
          #调用任务系统的 update_due_date 方法更新指定任务的截止日期
            result = self.__task_system.update_due_date(target_idx, parsed_date)
            #根据更新结果，提示用户设置截止日期是否成功
            if result:
                print("截止日期设置成功")
            else:
                print("任务不存在，设置失败")

        except ValueError:
            print("输入格式错误！")
        return 0