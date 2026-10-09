"""
完成标记菜单
使用依赖注入获取 TaskSystem 实例
"""

from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem


class MarkDoneMenu(Menu):
    def __init__(self, task_system: TaskSystem):
         super().__init__(
         "标记任务完成",
         "将指定编号的任务标记为已完成状态"
         )
         self.__task_system=task_system


    def execute(self) -> int:
        """菜单的核心逻辑"""
        task_list=self.__task_system.get_task_list()
        if not task_list:
            print("没有任务可标记。")
            return 0
        print("当前任务列表：")
        for idx, task in enumerate(task_list):
               status = "已完成" if task.completed else "未完成"
               print(f"{idx+1}: {task.title} - {status}")
        try:
              show_num=int(input("请输入任务编号："))
              idx=show_num-1
              if idx<0 or idx>=len(task_list):
                  print("任务编号无效，请输入有效的编号。")
                  return 0
              success=self.__task_system.update_completed(idx,True)
              if success:
                   print("标记任务为已完成")
              else:
                   print("任务编号不存在，标记失败")
              return 0
        except Exception as e:
            print(f"错误：{e}")
        return -1 
    
              
        

