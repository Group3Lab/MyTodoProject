from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem

class SearchAndFilterMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__("搜索与筛选", "查找或过滤任务")
        self.task_system = task_system

    def execute(self) -> int:
        print("\n" + "="*50)
        print("1. 只看未完成")
        print("2. 只看已完成")
        print("3. 只看已逾期")
        print("4. 按关键字搜索")
        print("5. 按优先级排序")
        print("6. 按截止日期排序")
        print("="*50)
        
        choice = input("请选择操作（按回车返回）：")
        result = []
        
        if choice == "1":
            result = self.task_system.get_filtered_tasks("unfinished")
        elif choice == "2":
            result = self.task_system.get_filtered_tasks("finished")
        elif choice == "3":
            result = self.task_system.get_filtered_tasks("overdue")
        elif choice == "4":
            kw = input("请输入关键字：")
            result = self.task_system.search_tasks(kw)
        elif choice == "5":
            result = self.task_system.sort_tasks("priority")
        elif choice == "6":
            result = self.task_system.sort_tasks("due_date")
        else:
            return 0
            
        if not result:
            print("\n没有找到符合条件的任务。")
        else:
            print(f"\n找到了 {len(result)} 个任务：")
            for t in result:
                # 注意：如果这里报错 task.title，改成实际字段名，比如 task.name
                print(f"- {t.title} (完成: {t.is_completed})")
                
        input("\n按回车键继续...")
        return 0
