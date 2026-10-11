"""白盒单测：菜单系统与各菜单 execute 的返回码/边界行为。

覆盖：MenuSystem 注册与分发、各菜单空清单处理、非法输入的返回值，
以及回归验证 MarkDoneMenu / SetPriorityMenu / MyDeleteTaskMenu 的已知缺陷已修复。
"""

import io
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.menuModule.menu import Menu
from core.menuModule.menuSystem import MenuSystem
from core.taskModule.task import Priority, Task
from core.taskModule.taskSystem import TaskSystem
from Menus.AddTaskMenu import AddTaskMenu
from Menus.ExportReportMenu import ExportReportMenu
from Menus.MarkDoneMenu import MarkDoneMenu
from Menus.MyDeleteTaskMenu import MyDeleteTaskMenu
from Menus.SearchTasksMenu import SearchTasksMenu
from Menus.SetDueDateMenu import SetDueDateMenu
from Menus.SetPriorityMenu import SetPriorityMenu
from Menus.ViewTasksMenu import ViewTasksMenu


def make_ts(n=0):
    ts = TaskSystem()
    for i in range(n):
        t = Task(f"任务{i + 1}")
        ts.add(t)
    return ts


class _DummyMenu(Menu):
    def __init__(self, ret=0):
        super().__init__("dummy", "dummy")
        self._ret = ret

    def execute(self) -> int:
        return self._ret


class TestMenuSystem(unittest.TestCase):
    def test_register_assigns_sequential_ids(self):
        ms = MenuSystem()
        # 用菜单的 name 无法直接断言，改用 countId 与 execute 行为
        ms.register(_DummyMenu(11))
        ms.register(_DummyMenu(22))
        self.assertEqual(ms.countId, 2)
        self.assertEqual(ms.execute(1), 11)
        self.assertEqual(ms.execute(2), 22)

    def test_execute_invalid_returns_minus_one(self):
        ms = MenuSystem()
        ms.register(_DummyMenu(0))
        self.assertEqual(ms.execute(0), -1)
        self.assertEqual(ms.execute(5), -1)

    def test_execute_on_empty_returns_minus_one(self):
        self.assertEqual(MenuSystem().execute(1), -1)

    def test_print_menu_runs(self):
        ms = MenuSystem()
        ms.register(_DummyMenu())
        with patch("sys.stdout", new=io.StringIO()) as out:
            ms.printMenu()
        self.assertIn("dummy", out.getvalue())


class TestMenuEmptyListBehavior(unittest.TestCase):
    """所有菜单在空清单下都应以成功码返回且不索要输入。"""

    def test_all_menus_handle_empty_list(self):
        cases = {
            "ViewTasksMenu": ViewTasksMenu(make_ts(0)),
            "MarkDoneMenu": MarkDoneMenu(make_ts(0)),
            "MyDeleteTaskMenu": MyDeleteTaskMenu(make_ts(0)),
            "SetDueDateMenu": SetDueDateMenu(make_ts(0)),
            "SetPriorityMenu": SetPriorityMenu(make_ts(0)),
            "SearchTasksMenu": SearchTasksMenu(make_ts(0)),
        }
        for name, menu in cases.items():
            with self.subTest(menu=name):
                with patch("builtins.input", side_effect=AssertionError("空清单不应调用 input")):
                    with patch("sys.stdout", new=io.StringIO()):
                        ret = menu.execute()
                self.assertEqual(ret, 0)


class TestMenuReturnCodes(unittest.TestCase):
    """所有菜单的成功路径都应返回 int 0（回归：曾隐式返回 None）。"""

    def _assert_int_zero(self, menu, inputs):
        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()):
                with patch("subprocess.run"):  # 导出菜单可能触发外部? 这里不用
                    ret = menu.execute()
        self.assertIsInstance(ret, int)
        self.assertEqual(ret, 0)

    def test_mark_done_valid(self):
        ts = make_ts(1)
        self._assert_int_zero(MarkDoneMenu(ts), ["1"])
        self.assertTrue(ts.get_by_index(0).is_completed)

    def test_mark_done_bad_input(self):
        self._assert_int_zero(MarkDoneMenu(make_ts(1)), ["abc"])

    def test_mark_done_out_of_range(self):
        self._assert_int_zero(MarkDoneMenu(make_ts(1)), ["99"])

    def test_delete_valid(self):
        ts = make_ts(2)
        self._assert_int_zero(MyDeleteTaskMenu(ts), ["1", "y"])
        self.assertEqual(ts.get_task_count(), 1)

    def test_delete_cancel(self):
        ts = make_ts(1)
        self._assert_int_zero(MyDeleteTaskMenu(ts), ["1", "n"])
        self.assertEqual(ts.get_task_count(), 1)

    def test_delete_bad_input(self):
        self._assert_int_zero(MyDeleteTaskMenu(make_ts(1)), ["abc"])

    def test_set_priority_valid(self):
        ts = make_ts(1)
        with patch.object(sys, "stdout", new=io.StringIO()):
            self._assert_int_zero(SetPriorityMenu(ts), ["1", "3"])
        self.assertEqual(ts.get_by_index(0).priority, Priority.High)

    def test_set_due_date_valid(self):
        ts = make_ts(1)
        self._assert_int_zero(SetDueDateMenu(ts), ["1", "2026-10-08"])
        self.assertEqual(ts.get_by_index(0).due_date, datetime(2026, 10, 8))

    def test_search_invalid_choice(self):
        self._assert_int_zero(SearchTasksMenu(make_ts(1)), ["x"])


class TestAddTaskMenu(unittest.TestCase):
    def test_add_valid(self):
        ts = make_ts(0)
        menu = AddTaskMenu(ts)
        with patch("builtins.input", side_effect=["写作业", "3", "2026-10-08"]):
            with patch("sys.stdout", new=io.StringIO()):
                ret = menu.execute()
        self.assertEqual(ret, 0)
        self.assertEqual(ts.get_task_count(), 1)
        t = ts.get_by_index(0)
        self.assertEqual(t.title, "写作业")
        self.assertEqual(t.priority, Priority.High)
        self.assertEqual(t.due_date, datetime(2026, 10, 8))

    def test_add_cancel(self):
        ts = make_ts(0)
        with patch("builtins.input", side_effect=["0"]):
            with patch("sys.stdout", new=io.StringIO()):
                ret = AddTaskMenu(ts).execute()
        self.assertEqual(ret, 0)
        self.assertEqual(ts.get_task_count(), 0)

    def test_add_empty_title_then_retry(self):
        ts = make_ts(0)
        with patch("builtins.input", side_effect=["", "", "有效标题", "", ""]):
            with patch("sys.stdout", new=io.StringIO()):
                ret = AddTaskMenu(ts).execute()
        self.assertEqual(ret, 0)
        self.assertEqual(ts.get_task_count(), 1)
        self.assertEqual(ts.get_by_index(0).title, "有效标题")

    def test_add_invalid_date_skipped(self):
        ts = make_ts(0)
        with patch("builtins.input", side_effect=["任务", "2", "不是日期"]):
            with patch("sys.stdout", new=io.StringIO()):
                ret = AddTaskMenu(ts).execute()
        self.assertEqual(ret, 0)
        self.assertFalse(ts.get_by_index(0).has_due_date)


class TestExportReport(unittest.TestCase):
    def test_export_creates_html_with_stats(self):
        from tempfile import TemporaryDirectory
        ts = make_ts(0)
        t = Task("过期任务")
        t.priority = Priority.High
        t.due_date = datetime(2020, 1, 1)  # 已过期
        ts.add(t)
        with TemporaryDirectory() as tmp:
            menu = ExportReportMenu(ts)
            with patch("builtins.input", side_effect=[tmp]):
                with patch("sys.stdout", new=io.StringIO()):
                    ret = menu.execute()
            self.assertEqual(ret, 0)
            reports = list(Path(tmp).glob("report_*.html"))
            self.assertEqual(len(reports), 1, "应生成 report_YYYY-MM-DD.html")
            html = reports[0].read_text(encoding="utf-8")
            self.assertIn("任务清单报告", html)
            self.assertIn("overdue", html)      # 逾期样式
            self.assertIn("过期任务", html)


if __name__ == "__main__":
    unittest.main()
