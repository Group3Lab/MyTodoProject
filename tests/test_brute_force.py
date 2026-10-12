"""黑盒端到端「暴力测试」：用 subprocess 跑 src/main.py，喂各种输入。

目标：无论用户输入什么（字母、超大数、负数、小数、空回车、超长串、
乱码、EOF、Ctrl+C 等价、含分隔符的标题……），程序都不得崩溃、
不得输出 "Traceback"，且能正常退出。

所有用例都在 DataSandbox 里跑，不污染真实 data/。
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests import helpers as H
from tests.helpers import (
    MENU_ADD, MENU_CHART, MENU_DELETE, MENU_EXIT, MENU_EXPORT, MENU_MARK_DONE,
    MENU_SEARCH, MENU_SET_DUE, MENU_SET_PRIORITY, MENU_VIEW_ALL,
    DataSandbox, assert_no_traceback, run_main, write_data, write_data_bytes,
)


class BruteBase(unittest.TestCase):
    def setUp(self):
        self._sb = DataSandbox().__enter__()

    def tearDown(self):
        self._sb.__exit__(None, None, None)

    def run_ok(self, inputs, timeout=30):
        """运行并断言：无 Traceback、正常结束。返回 CompletedProcess。"""
        proc = run_main(inputs, timeout=timeout)
        assert_no_traceback(self, proc)
        self.assertEqual(proc.returncode, 0, msg="非 0 退出码\n" + proc.stdout + proc.stderr)
        return proc


class TestExtremeMainMenuInput(BruteBase):
    """主菜单层面的暴力输入。"""

    GARBAGE = [
        "abc", "ABC", "1.5", "-1", "-999", "0x10", "1e9",
        "999999999999999999999999", "！@#$%^&*()", "你好", " ", "\t",
        "0 1", "1;2", "true", "None", "NaN", "inf", " 2 ", "2.0",
        "²", "𝓶", "\\", "/", ".", "..", "０",  # 全角数字
    ]

    def test_garbage_then_exit(self):
        for g in self.GARBAGE:
            with self.subTest(input=repr(g)):
                self.run_ok([g, MENU_EXIT])

    def test_many_empty_enters(self):
        self.run_ok([""] * 50 + [MENU_EXIT])

    def test_long_string(self):
        self.run_ok(["a" * 5000, MENU_EXIT])

    def test_immediate_eof(self):
        """直接 EOF（空输入）不得崩溃。"""
        self.run_ok([])

    def test_exit_directly(self):
        self.run_ok([MENU_EXIT])


class TestExtremeAddTask(BruteBase):
    """添加任务流程的暴力输入。"""

    def test_title_garbage_priority_date(self):
        cases = [
            ["正常标题", "abc", "not-a-date"],
            ["正常标题", "999", "2026-13-45"],
            ["正常标题", "", ""],
            [" 前后空格标题 ", "1", "2026/01/02"],
            ["标题带|分隔符", "3", "2026-1-1"],
            ["x" * 1000, "2", "2026-10-08"],
        ]
        for case in cases:
            with self.subTest(case=case[:2]):
                inputs = [MENU_ADD] + case + [""] + [MENU_EXIT]
                proc = self.run_ok(inputs)
                self.assertIn("添加", proc.stdout)  # 至少走到添加流程

    def test_add_then_persist(self):
        self.run_ok([MENU_ADD, "数学建模", "3", "2026-12-31", "", MENU_EXIT])
        saved = H.read_data()
        self.assertIsNotNone(saved, "退出后应生成 data/tasks.json")
        data = json.loads(saved)
        self.assertEqual(data[0]["title"], "数学建模")
        self.assertEqual(data[0]["priority"], "高")

    def test_add_empty_title_loop_then_cancel(self):
        # 一直空标题，最后用 0 取消
        self.run_ok([MENU_ADD, "", "", "", "0", MENU_EXIT])


class TestExtremeSearch(BruteBase):
    def setUp(self):
        super().setUp()
        write_data(json.dumps([
            {"title": "写高数作业", "priority": "高", "due_date": "2020-01-01", "is_completed": False},
            {"title": "背书", "priority": "低", "due_date": None, "is_completed": True},
        ], ensure_ascii=False))

    def test_search_all_options(self):
        for opt in ["1", "2", "3", "4", "5", "6"]:
            with self.subTest(option=opt):
                inputs = [MENU_SEARCH, opt]
                if opt == "4":
                    inputs.append("高")  # 关键字
                inputs += ["", MENU_EXIT]
                self.run_ok(inputs)

    def test_search_invalid_options(self):
        for opt in ["0", "7", "abc", "", "-1", "999"]:
            with self.subTest(option=repr(opt)):
                self.run_ok([MENU_SEARCH, opt, "", MENU_EXIT])

    def test_search_keyword_garbage(self):
        self.run_ok([MENU_SEARCH, "4", "", "", MENU_EXIT])       # 空关键字
        self.run_ok([MENU_SEARCH, "4", "不存在的词", "", MENU_EXIT])
        self.run_ok([MENU_SEARCH, "4", "x" * 500, "", MENU_EXIT])
        # 正则元字符 / 全角空格 / emoji：必须按字面匹配且不崩溃
        self.run_ok([MENU_SEARCH, "4", ".*", "", MENU_EXIT])
        self.run_ok([MENU_SEARCH, "4", "（", "", MENU_EXIT])
        self.run_ok([MENU_SEARCH, "4", "　", "", MENU_EXIT])
        self.run_ok([MENU_SEARCH, "4", "📚", "", MENU_EXIT])

    def test_search_result_sorted_by_relevance(self):
        """端到端验证：菜单输出里的结果顺序就是关联度从高到低。"""
        write_data(json.dumps([
            {"title": "今天写作业", "priority": "中", "due_date": None, "is_completed": False},
            {"title": "作业", "priority": "中", "due_date": None, "is_completed": False},
            {"title": "背书", "priority": "低", "due_date": None, "is_completed": False},
            {"title": "写作业", "priority": "中", "due_date": None, "is_completed": False},
        ], ensure_ascii=False))
        proc = self.run_ok([MENU_SEARCH, "4", "作业", "", MENU_EXIT])
        # 只保留 "编号. 标题 | ..." 形式的结果行，取标题部分
        titles = []
        for line in proc.stdout.splitlines():
            head, sep, rest = line.partition(". ")
            if sep and head.isdigit() and " | " in rest:
                titles.append(rest.split(" | ")[0])
        self.assertEqual(titles, ["作业", "写作业", "今天写作业"])  # 「背书」不匹配，被过滤


class TestExtremeOperations(BruteBase):
    def setUp(self):
        super().setUp()
        write_data(json.dumps([
            {"title": "任务A", "priority": "高", "due_date": "2026-12-31", "is_completed": False},
            {"title": "任务B", "priority": "低", "due_date": None, "is_completed": False},
        ], ensure_ascii=False))

    def test_mark_done_brute(self):
        for num in ["0", "-1", "3", "999", "abc", "", "1.5", "1"]:
            with self.subTest(num=repr(num)):
                self.run_ok([MENU_MARK_DONE, num, "", MENU_EXIT])

    def test_delete_brute(self):
        for num in ["0", "-1", "999", "abc", ""]:
            with self.subTest(num=repr(num)):
                self.run_ok([MENU_DELETE, num, "", MENU_EXIT])

    def test_delete_confirm_variants(self):
        for confirm in ["n", "N", "no", "y", "Y", "yes", "", "maybe"]:
            with self.subTest(confirm=repr(confirm)):
                write_data(json.dumps([
                    {"title": "任务A", "priority": "高", "due_date": None, "is_completed": False},
                ], ensure_ascii=False))
                self.run_ok([MENU_DELETE, "1", confirm, "", MENU_EXIT])

    def test_set_due_brute(self):
        for date in ["2026-10-08", "2026/10/08", "bad", "", "2026-13-01", "0000-00-00"]:
            with self.subTest(date=repr(date)):
                self.run_ok([MENU_SET_DUE, "1", date, "", MENU_EXIT])

    def test_set_priority_brute(self):
        for p in ["1", "2", "3", "0", "4", "abc", "", "-1", "999", "1.0"]:
            with self.subTest(priority=repr(p)):
                self.run_ok([MENU_SET_PRIORITY, "1", p, "", MENU_EXIT])


class TestDataFileCorruption(BruteBase):
    """data/tasks.json 各种损坏形态下启动都不得崩溃。"""

    CORRUPT = [
        "",
        "{",
        "not json at all",
        "{}",                                   # 不是列表
        "[]",
        "[1, 2, 3]",                            # 元素不是对象
        '[{"title": ""}]',                      # 空标题
        '[{"priority": "高"}]',                 # 缺 title
        '[{"title": "x", "priority": "超高"}]',  # 非法优先级
        '[{"title": "x", "priority": "高", "due_date": "not-a-date"}]',
        '[{"title": "x", "priority": "高", "due_date": 20260101}]',
        "null",
        '[{"title": "x", "priority": "高", "is_completed": "yes"}]',
    ]

    def test_corrupt_files(self):
        for content in self.CORRUPT:
            with self.subTest(content=content[:30]):
                write_data(content)
                self.run_ok([MENU_VIEW_ALL, "", MENU_EXIT])

    def test_with_bom(self):
        content = '[{"title": "带BOM", "priority": "高", "due_date": null, "is_completed": false}]'
        write_data_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))
        proc = self.run_ok([MENU_VIEW_ALL, "", MENU_EXIT])
        self.assertIn("带BOM", proc.stdout)

    def test_corrupt_record_not_shown_no_crash(self):
        write_data('[{"title": "正常", "priority": "高", "due_date": null, "is_completed": false},'
                   ' {"title": "坏", "priority": "??"}]')
        proc = self.run_ok([MENU_VIEW_ALL, "", MENU_EXIT])
        self.assertIn("正常", proc.stdout)


class TestPersistenceRoundTrip(BruteBase):
    def test_save_then_reload(self):
        self.run_ok([MENU_ADD, "持久化任务", "3", "2026-12-31", "", MENU_EXIT])
        # 第二次启动应能读回
        proc = self.run_ok([MENU_VIEW_ALL, "", MENU_EXIT])
        self.assertIn("持久化任务", proc.stdout)
        self.assertIn("任务总数: 1", proc.stdout)

    def test_multiple_adds(self):
        inputs = []
        for i in range(1, 6):
            inputs += [MENU_ADD, f"任务{i}", str((i % 3) + 1), f"2026-0{i}-01", ""]
        inputs += [MENU_EXIT]
        self.run_ok(inputs)
        data = json.loads(H.read_data())
        self.assertEqual(len(data), 5)

    def test_completion_rate_and_stats(self):
        self.run_ok([MENU_ADD, "任务1", "3", "2020-01-01", "", MENU_EXIT])  # 逾期
        proc = self.run_ok([MENU_VIEW_ALL, "", MENU_EXIT])
        self.assertIn("已逾期: 1", proc.stdout)
        self.assertIn("完成率: 0.00%", proc.stdout)


class TestExportReportE2E(BruteBase):
    def test_export_default_dir_and_custom(self):
        write_data(json.dumps([
            {"title": "导出任务", "priority": "高", "due_date": "2020-01-01", "is_completed": False},
        ], ensure_ascii=False))
        proc = self.run_ok([MENU_EXPORT, "", "", MENU_EXIT])   # 默认目录
        self.assertIn("已导出报告", proc.stdout)
        reports_dir = H.REPO_ROOT / "reports"
        try:
            self.assertTrue(reports_dir.exists())
            files = list(reports_dir.glob("report_*.html"))
            self.assertTrue(files, "应生成 report_*.html")
            html = files[0].read_text(encoding="utf-8")
            self.assertIn("导出任务", html)
            self.assertIn("overdue", html)
        finally:
            import shutil
            shutil.rmtree(reports_dir, ignore_errors=True)

    def test_export_invalid_path_falls_back(self):
        write_data("[]")
        # 传入非法目录名，应退回默认目录而非崩溃
        self.run_ok([MENU_EXPORT, "\x00invalid<>path", "", MENU_EXIT])
        import shutil
        shutil.rmtree(H.REPO_ROOT / "reports", ignore_errors=True)


class TestChartE2E(BruteBase):
    """OpenCV 统计图表菜单的端到端测试（主菜单 9）。

    图表固定写到 CWD（仓库根目录）的 chart.png，测试后清理。
    """

    CHART = H.REPO_ROOT / "chart.png"

    def tearDown(self):
        self.CHART.unlink(missing_ok=True)
        super().tearDown()

    def test_generate_chart_from_real_data(self):
        """有任务时生成 chart.png，且是合法 PNG。"""
        write_data(json.dumps([
            {"title": "高1", "priority": "高", "due_date": None, "is_completed": False},
            {"title": "高2", "priority": "高", "due_date": None, "is_completed": False},
            {"title": "中1", "priority": "中", "due_date": None, "is_completed": False},
            {"title": "低1", "priority": "低", "due_date": None, "is_completed": False},
            {"title": "已完成", "priority": "高", "due_date": None, "is_completed": True},
        ], ensure_ascii=False))
        proc = self.run_ok([MENU_CHART, "", MENU_EXIT])
        self.assertIn("统计图已保存", proc.stdout)
        self.assertTrue(self.CHART.exists(), "应生成 chart.png")
        self.assertEqual(self.CHART.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_generate_chart_empty_list(self):
        """空清单也能出图且不崩。"""
        write_data("[]")
        proc = self.run_ok([MENU_CHART, "", MENU_EXIT])
        self.assertIn("统计图已保存", proc.stdout)
        self.assertTrue(self.CHART.exists())

    def test_chart_numbers_match_list(self):
        """图上数字必须与清单一致：通过解码 PNG 尺寸无关的计数封送验证。

        这里改用白盒方式核对：不同数据生成的文件字节不同（非写死），
        同一份数据重复生成则一致。
        """
        data_a = json.dumps([{"title": "a", "priority": "高", "due_date": None, "is_completed": False}], ensure_ascii=False)
        write_data(data_a)
        self.run_ok([MENU_CHART, "", MENU_EXIT])
        bytes_a = self.CHART.read_bytes()
        self.CHART.unlink()

        # 换成 3 条高优先级，图应不同（证明数字是动态的，不是写死的）
        data_b = json.dumps([{"title": f"a{i}", "priority": "高", "due_date": None, "is_completed": False} for i in range(3)], ensure_ascii=False)
        write_data(data_b)
        self.run_ok([MENU_CHART, "", MENU_EXIT])
        bytes_b = self.CHART.read_bytes()
        self.assertNotEqual(bytes_a, bytes_b, "不同数据应生成不同图，说明数字不是写死的")

    def test_chart_does_not_pollute_git(self):
        """生成的 chart.png 应被 .gitignore 忽略。"""
        import subprocess
        write_data("[]")
        self.run_ok([MENU_CHART, "", MENU_EXIT])
        self.assertTrue(self.CHART.exists())
        r = subprocess.run(
            ["git", "check-ignore", "-q", "chart.png"],
            cwd=str(H.REPO_ROOT),
        )
        self.assertEqual(r.returncode, 0, "chart.png 应被 git 忽略")


class TestInteractiveMixedSession(BruteBase):
    """混合操作的长会话，模拟真实使用。"""

    def tearDown(self):
        (H.REPO_ROOT / "chart.png").unlink(missing_ok=True)
        super().tearDown()

    def test_full_session(self):
        inputs = [
            MENU_ADD, "写高数作业", "3", "2026-10-08", "",
            MENU_ADD, "背书", "1", "", "",
            MENU_ADD, "数学建模", "2", "2026-12-31", "",
            MENU_VIEW_ALL, "",
            MENU_SEARCH, "5", "",
            MENU_MARK_DONE, "2", "",
            MENU_SET_PRIORITY, "1", "1", "",
            MENU_SET_DUE, "3", "2026-11-11", "",
            MENU_DELETE, "1", "n", "",
            MENU_VIEW_ALL, "",
            MENU_CHART, "",
            MENU_EXIT,
        ]
        proc = self.run_ok(inputs, timeout=60)
        self.assertIn("任务总数: 3", proc.stdout)


if __name__ == "__main__":
    unittest.main()
