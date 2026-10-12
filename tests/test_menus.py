"""白盒单测：菜单系统与各菜单 execute 的返回码/边界行为。

覆盖：MenuSystem 注册与分发、各菜单空清单处理、非法输入的返回值、
搜索相关度排序、OpenCV 统计图表（ChartMenu），
以及回归验证 MarkDoneMenu / SetPriorityMenu / MyDeleteTaskMenu 的已知缺陷已修复。
"""

import io
import sys
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
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


class TestSearchRelevance(unittest.TestCase):
    """关键字搜索的关联度排序（回归：曾按「关键字出现位置」排序）。"""

    @staticmethod
    def _do_search(titles, keyword):
        """跑一次搜索菜单（选 4 按关键字搜索），返回打印出来的结果标题顺序。"""
        ts = TaskSystem()
        for title in titles:
            ts.add(Task(title))
        # 菜单内部会先问「请选择操作」，选 4 后才问「请输入搜索关键字」
        with patch("builtins.input", side_effect=["4", keyword]):
            with patch("sys.stdout", new=io.StringIO()) as out:
                ret = SearchTasksMenu(ts).execute()
        assert ret == 0, f"搜索菜单应返回 0，实际为 {ret}"
        # 结果行形如 "1. 标题 | 优先级 | 截止日期 | 状态"；菜单选项行没有 " | "
        results = []
        for line in out.getvalue().splitlines():
            head, sep, rest = line.partition(". ")
            if sep and head.isdigit() and " | " in rest:
                results.append(rest.split(" | ")[0])
        return results

    def test_relevance_order(self):
        """完全匹配 > 出现多次的长标题 > 词尾匹配 > 靠后出现；不匹配的被过滤"""
        titles = ["作业", "写作业", "今天写作业", "作业很多，先写数学作业", "背书"]
        self.assertEqual(
            self._do_search(titles, "作业"),
            ["作业", "作业很多，先写数学作业", "写作业", "今天写作业"],
        )

    def test_no_match_returns_empty(self):
        self.assertEqual(self._do_search(["写作业", "背书"], "不存在的词"), [])

    def test_case_insensitive(self):
        """英文关键字不区分大小写，且整词匹配排在嵌入匹配之前"""
        self.assertEqual(
            self._do_search(["abc", "ab", "xxab"], "AB"),
            ["ab", "abc", "xxab"],
        )

    def test_empty_keyword_shows_all(self):
        """空关键字不筛选，按原顺序返回全部任务"""
        titles = ["任务A", "任务B", "任务C"]
        self.assertEqual(self._do_search(titles, "   "), titles)

    def test_long_title_does_not_beat_multiple_hits(self):
        """长标题不因长度被倒扣，出现次数多仍排在短标题前面"""
        titles = ["今天作业作业作业" * 10, "今天写作业"]
        self.assertEqual(
            self._do_search(titles, "作业"),
            ["今天作业作业作业" * 10, "今天写作业"],
        )

    def test_keyword_special_chars_are_literal(self):
        """关键字含正则元字符时按字面匹配，不作为模式解析"""
        self.assertEqual(
            self._do_search(["a.*b", "aXXb", "a.b"], ".*"),
            ["a.*b"],
        )


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


class TestChartMenu(unittest.TestCase):
    """OpenCV 统计图表菜单（Menus/ChartMenu.py）。

    图表固定输出到仓库根的 data/chart.png；测试通过 monkeypatch 把输出目录
    指到临时目录，避免污染真实的 data/。
    """

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self._dir = Path(self._tmp.name) / "data"
        from Menus import ChartMenu as chart_mod
        self._chart_mod = chart_mod
        self._old_dir = chart_mod._CHART_DIR
        self._old_file = chart_mod._CHART_FILE
        chart_mod._CHART_DIR = self._dir
        chart_mod._CHART_FILE = self._dir / "chart.png"

    def tearDown(self):
        self._chart_mod._CHART_DIR = self._old_dir
        self._chart_mod._CHART_FILE = self._old_file
        self._tmp.cleanup()

    @staticmethod
    def _make_priority_ts():
        ts = make_ts(0)
        for priority, n in ((Priority.High, 2), (Priority.Medium, 3), (Priority.Low, 1)):
            for _ in range(n):
                t = Task("任务")
                t.priority = priority
                ts.add(t)
        return ts

    def _run(self, ts):
        with patch("sys.stdout", new=io.StringIO()):
            ret = self._chart_mod.ChartMenu(ts).execute()
        chart = self._dir / "chart.png"
        exists = chart.exists()
        size = chart.stat().st_size if exists else 0
        return ret, exists, size

    def test_generates_chart_png(self):
        ret, exists, size = self._run(self._make_priority_ts())
        self.assertEqual(ret, 0)
        self.assertTrue(exists, "应生成 chart.png")
        self.assertGreater(size, 0, "chart.png 不应为空")

    def test_valid_png_header(self):
        """生成的文件应是合法 PNG（头 8 字节固定）。"""
        self._run(self._make_priority_ts())
        head = (self._dir / "chart.png").read_bytes()[:8]
        self.assertEqual(head, b"\x89PNG\r\n\x1a\n")

    def test_empty_list_does_not_crash(self):
        """空清单也应返回 0 并出图（内部用 max(...,1) 防除零）。"""
        ret, exists, size = self._run(make_ts(0))
        self.assertEqual(ret, 0)
        self.assertTrue(exists)
        self.assertGreater(size, 0)

    def test_creates_data_dir_if_missing(self):
        """输出目录不存在时应自动创建。"""
        self.assertFalse(self._dir.exists())
        ret, exists, _ = self._run(self._make_priority_ts())
        self.assertEqual(ret, 0)
        self.assertTrue(self._dir.exists())
        self.assertTrue(exists)

    def test_counts_ignore_completed(self):
        """统计应忽略已完成任务：高2/中3/低1，另有已完成的高/中不计数。"""
        ts = self._make_priority_ts()
        done_high = Task("已完成高")
        done_high.priority = Priority.High
        done_high.is_completed = True
        ts.add(done_high)
        done_mid = Task("已完成中")
        done_mid.priority = Priority.Medium
        done_mid.is_completed = True
        ts.add(done_mid)

        menu = self._chart_mod.ChartMenu(ts)
        with patch("sys.stdout", new=io.StringIO()):
            result = menu._ChartMenu__count_by_priority()
        self.assertEqual(result, (2, 3, 1))

    def test_all_priorities_counted(self):
        """三档优先级都能被统计到。"""
        ts = make_ts(0)
        for priority in (Priority.High, Priority.Medium, Priority.Low):
            t = Task("任务")
            t.priority = priority
            ts.add(t)
        menu = self._chart_mod.ChartMenu(ts)
        with patch("sys.stdout", new=io.StringIO()):
            result = menu._ChartMenu__count_by_priority()
        self.assertEqual(result, (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
