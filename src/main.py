import sys
import os

# 添加 core 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.menuModule.menuFactory import MenuFactory


def toNum(s: str) -> int:
    """将字符串转换为整数，转换失败返回 -1"""
    try:
        return int(s)
    except (ValueError, TypeError):
        return -1


def clear_screen() -> None:
    """清屏，失败时忽略（不影响主流程）"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        pass


def safe_input(prompt: str):
    """安全读取用户输入：EOF 或中断都不会让主循环崩溃

    - Ctrl+C：当作空输入返回，回到主菜单继续运行
    - EOF（输入流结束，如管道输入耗尽）：返回 None，由调用方决定退出
    """
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print()
        return ""
    except EOFError:
        print()
        return None


def pause(prompt: str = "\n按回车键继续...") -> None:
    """安全暂停：EOF 或中断时直接跳过"""
    try:
        input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()


def main() -> None:
    # 使用工厂创建菜单系统（创建失败不进入主循环，直接给出提示并退出）
    try:
        menu_sys = MenuFactory.create_menu_system()
    except Exception as e:
        print(f"[错误] 初始化菜单系统失败: {e}")
        return

    # 主循环：任何单次操作的异常都不会让程序崩溃
    while True:
        try:
            clear_screen()  # 每次循环开始时清屏

            print("\n" + "="*50)
            print("MyTodo - 待办任务管理系统")
            print("="*50)

            # 显示菜单
            menu_sys.printMenu()
            print("0: 退出")

            # 获取用户输入
            userInput = safe_input("\n请选择功能: ")  # 删掉字符串开头和结尾的空白字符

            # 输入流已结束：无法再获取输入，直接安全退出，避免空转
            if userInput is None:
                print("\n输入已结束，程序退出。")
                return

            choice: int = toNum(userInput)  # 输入转Int

            clear_screen()  # 选择后清屏

            print("\n" + "="*50)

            if choice == -1:
                print("非法输入，请重新选择")
                pause()
                continue

            if choice < 0 or choice > menu_sys.countId:
                print("输入超出范围，请重新选择")
                pause()
                continue

            # 处理退出
            if choice == 0:
                print("感谢使用，再见！")
                break

            # 执行菜单并处理返回的错误码（0 表示成功，非 0 表示失败）
            try:
                result: int = menu_sys.execute(choice)
            except Exception as e:
                print(f"[错误] 功能执行异常: {e}")
                result = -1

            if result is not None and result != 0:
                print(f"功能执行失败，错误码：{result}")
                print("请返回主菜单后重试")

            # 等待继续
            pause()

            print("\n" + "="*50)

        except KeyboardInterrupt:
            # 兜底：Ctrl+C 不会让程序抛出堆栈，回到主菜单继续
            print("\n已取消当前操作，返回主菜单")
            pause()
            continue
        except Exception as e:
            # 兜底：循环体任何未预料的异常都不终止主循环
            print(f"\n[错误] 出现未预期的异常: {e}")
            pause()
            continue

if __name__ == "__main__":
    main()
