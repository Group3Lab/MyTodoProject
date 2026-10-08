import sys
import os

# 添加 core 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.menuModule.menuFactory import MenuFactory


def toNum(s: str) -> int:
    """将字符串转换为整数，转换失败返回 -1"""
    try:
        return int(s)
    except ValueError:
        return -1


def clear_screen() -> None:
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def main() -> None:
    # 使用工厂创建菜单系统
    menu_sys = MenuFactory.create_menu_system()

    # 主循环
    while True:
        clear_screen()  # 每次循环开始时清屏

        print("\n" + "="*50)
        print("MyTodo - 待办任务管理系统")
        print("="*50)

        # 显示菜单
        menu_sys.printMenu()
        print("0: 退出")

        # 获取用户输入
        userInput:str = input("\n请选择功能: ").strip() #删掉字符串开头和结尾的空白字符

        choice:int = toNum(userInput) # 输入转Int

        clear_screen()  # 选择后清屏

        print("\n" + "="*50)

        if choice == -1:
            print("非法输入，请重新选择")
            input("\n按回车键继续...")
            continue

        if choice < 0 or choice > menu_sys.countId:
            print("输入超出范围，请重新选择")
            input("\n按回车键继续...")
            continue

        # 处理退出
        if choice == 0:
            print("感谢使用，再见！")
            break

        menu_sys.execute(choice)

        # 等待继续
        input("\n按回车键继续...")

        print("\n" + "="*50)

if __name__ == "__main__":
    main()
