'''
菜单设置工厂
负责创建和注册所有菜单，解耦 main 与具体菜单实现
'''

from .menuSystem import MenuSystem

from Menus.MenuA import MenuA

class MenuFactory:
    """菜单工厂，负责创建和配置菜单系统"""

    @staticmethod
    def create_menu_system() -> MenuSystem:
        """
        创建并配置完整的菜单系统
        :return: 配置好的 MenuSystem 实例
        """
        menu_sys = MenuSystem()

        # 注册所有菜单
        MenuFactory._register_menus(menu_sys)

        return menu_sys

    @staticmethod
    def _register_menus(menu_sys: MenuSystem) -> None:
        """
        注册所有菜单项
        添加新菜单只需在这里添加一行注册代码
        """
        # 功能菜单
        menu_sys.register(MenuA())
