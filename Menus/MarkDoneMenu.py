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
        try:
              idx=int(input("请输入任务下标："))
              success=self.__task_system.update_completed(idx,True)
              if success:
                   print("标记任务为已完成")
              else:
                   print("任务下标不存在，标记失败")
              return 0
        except Exception as e:
            print(f"错误：{e}")
        return -1 
    
              
        

