from typing import Dict
from .menu import Menu


class MenuSystem:

    def __init__(self):
        self.__menus: Dict[int, Menu] = {}
        self.__count_id: int = 0  # 实例变量，从1开始计数

    @property
    def countId(self) -> int:
        """获取当前已注册的菜单数量"""
        return self.__count_id

    def register(self, menu: Menu):
        self.__count_id += 1
        self.__menus[self.__count_id] = menu

    def printMenu(self):
        for key, menu in self.__menus.items():
            print(f"{key}.{menu.name}:{menu.info}")
            print()

    def execute(self, choice: int) -> int:
        if not self.__menus:
            return -1
        menu = self.__menus.get(choice)
        if menu is None:
            return -1
        return menu.execute()

