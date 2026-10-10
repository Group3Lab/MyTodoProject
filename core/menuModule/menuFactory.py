'''
菜单设置工厂
负责创建和注册所有菜单，解耦 main 与具体菜单实现
'''

from core.taskModule.taskSL import taskLoad

from .menuSystem import MenuSystem
from core.taskModule.taskSystem import TaskSystem

from menus.MenuA import MenuA
from menus.ViewTasksMenu import ViewTasksMenu
from menus.AddTaskMenu import AddTaskMenu
from menus.DeleteTaskMenu import DeleteTaskMenu
from menus.MyDeleteTaskMenu import MyDeleteTaskMenu
from menus.MarkDoneMenu import MarkDoneMenu
from menus.SetDueDateMenu import SetDueDateMenu
from menus.SetPriorityMenu import SetPriorityMenu
from menu.ExportReportMenu import ExportReportMenu


class MenuFactory:
    """菜单工厂，负责创建和配置菜单系统"""

    # 返回tuple[MenuSystem, TaskSystem]，主要产物和副产物属于是，因为main需要访问TaskSystem的Save
    @staticmethod
    def create_menu_system() -> tuple[MenuSystem, TaskSystem]:
        """
        创建并配置完整的菜单系统
        使用依赖注入将 TaskSystem 实例传递给各个菜单
        :return: (配置好的 MenuSystem 实例, 本次创建的 TaskSystem 实例)，供 main 保存数据使用
        """
        menu_sys = MenuSystem()

        # 加载任务列表（taskLoad 失败时返回 None）
        tasks = taskLoad()
        if tasks is None:
            # 加载失败不能把 None 注入给菜单，否则调用时才报错、且根因被 try 掩盖
            print("[错误] 任务数据加载失败，本次以空清单启动")
            tasks = []

        # 用任务列表构造 TaskSystem 实例
        task_system = TaskSystem.CreateFromList(tasks)

        # 注册所有菜单，注入依赖
        MenuFactory._register_menus(menu_sys, task_system)

        # 连同 task_system 一起返回，供 main 持有并在退出前保存数据
        return menu_sys, task_system

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
        #menu_sys.register(DeleteTaskMenu(task_system)) # 大肥鱼写的藏代码，弃用了
        menu_sys.register(MyDeleteTaskMenu(task_system))
        menu_sys.register(MarkDoneMenu(task_system))
        menu_sys.register(SetDueDateMenu(task_system))
        menu_sys.register(SetPriorityMenu(task_system))
        menu_sys.register(ExportReportMenu(task_system))