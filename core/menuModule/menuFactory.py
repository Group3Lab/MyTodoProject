'''
菜单设置工厂
负责创建和注册所有菜单，解耦 main 与具体菜单实现
'''

from .menuSystem import MenuSystem
from core.taskModule.taskSystem import TaskSystem

from menus.MenuA import MenuA
from menus.ViewTasksMenu import ViewTasksMenu
from menus.AddTaskMenu import AddTaskMenu
from menus.DeleteTaskMenu import DeleteTaskMenu
from menus.MarkDoneMenu import MarkDoneMenu
from menus.MyDeleteTaskMenu import MyDeleteTaskMenu
class MenuFactory:
    """菜单工厂，负责创建和配置菜单系统"""

    @staticmethod
    def create_menu_system() -> MenuSystem:
        """
        创建并配置完整的菜单系统
        使用依赖注入将 TaskSystem 实例传递给各个菜单
        :return: 配置好的 MenuSystem 实例
        """
        menu_sys = MenuSystem()

        # 创建共享的 TaskSystem 实例
        task_system = TaskSystem()

        # 注册所有菜单，注入依赖
        MenuFactory._register_menus(menu_sys, task_system)

        return menu_sys

    @staticmethod
    def _register_menus(menu_sys: MenuSystem, task_system: TaskSystem) -> None:
        """
        注册所有菜单项
        通过依赖注入将 task_system 传递给需要的菜单
        添加新菜单只需在这里添加一行注册代码
        """
        # 功能菜单
        menu_sys.register(MenuA())
        menu_sys.register(ViewTasksMenu(task_system))
        menu_sys.register(AddTaskMenu(task_system))
        menu_sys.register(DeleteTaskMenu(task_system))
        menu_sys.register(MarkDoneMenu(task_system))
        menu_sys.register(MyDeleteTaskMenu(task_system))
