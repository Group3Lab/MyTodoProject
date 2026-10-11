"""白盒单测：Task 类（core/taskModule/task.py）。

覆盖：标题校验、优先级/日期/完成状态封装、to_string 格式。
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.taskModule.task import Priority, Task


class TestTaskConstruction(unittest.TestCase):
    def test_valid_title(self):
        t = Task("写高数作业")
        self.assertEqual(t.title, "写高数作业")

    def test_title_stripped(self):
        t = Task("  写作业  ")
        self.assertEqual(t.title, "写作业")

    def test_empty_title_raises(self):
        for bad in ["", "   ", "\t", "\n", " \t "]:
            with self.subTest(title=repr(bad)):
                with self.assertRaises(ValueError):
                    Task(bad)

    def test_none_title_raises(self):
        with self.assertRaises((ValueError, AttributeError)):
            Task(None)

    def test_defaults(self):
        t = Task("x")
        self.assertFalse(t.is_completed)
        self.assertFalse(t.has_due_date)
        self.assertEqual(t.priority, Priority.Medium)


class TestTaskPriority(unittest.TestCase):
    def test_set_valid_priority(self):
        t = Task("x")
        for p in (Priority.High, Priority.Medium, Priority.Low):
            t.priority = p
            self.assertEqual(t.priority, p)

    def test_set_invalid_priority_raises(self):
        t = Task("x")
        for bad in ["高", 1, None, 3.5]:
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError):
                    t.priority = bad

    def test_priority_values_are_chinese(self):
        self.assertEqual(Priority.High.value, "高")
        self.assertEqual(Priority.Medium.value, "中")
        self.assertEqual(Priority.Low.value, "低")


class TestTaskDueDate(unittest.TestCase):
    def test_set_due_date_flags_has_due_date(self):
        t = Task("x")
        t.due_date = datetime(2026, 10, 8)
        self.assertTrue(t.has_due_date)
        self.assertEqual(t.due_date, datetime(2026, 10, 8))

    def test_set_invalid_due_date_raises(self):
        t = Task("x")
        for bad in ["2026-10-08", 20261008, None]:
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError):
                    t.due_date = bad

    def test_has_due_date_readonly(self):
        """has_due_date 是只读属性，赋值应报错。"""
        t = Task("x")
        with self.assertRaises(AttributeError):
            t.has_due_date = True


class TestTaskCompleted(unittest.TestCase):
    def test_set_bool(self):
        t = Task("x")
        t.is_completed = True
        self.assertTrue(t.is_completed)
        t.is_completed = False
        self.assertFalse(t.is_completed)

    def test_set_non_bool_raises(self):
        t = Task("x")
        for bad in [1, 0, "true", None, []]:
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError):
                    t.is_completed = bad


class TestTaskToString(unittest.TestCase):
    def test_format_with_due_date(self):
        t = Task("写高数作业")
        t.priority = Priority.High
        t.due_date = datetime(2026, 10, 8)
        self.assertEqual(t.to_string(), "写高数作业 | 高 | 2026-10-08 | 未完成")

    def test_format_without_due_date(self):
        t = Task("背书")
        t.priority = Priority.Low
        self.assertEqual(t.to_string(), "背书 | 低 | 无截止日期 | 未完成")

    def test_format_completed(self):
        t = Task("任务")
        t.is_completed = True
        self.assertIn("已完成", t.to_string())

    def test_format_uses_pipe_separator(self):
        t = Task("a | b")  # 标题里含分隔符也应原样输出
        self.assertTrue(t.to_string().startswith("a | b |"))


if __name__ == "__main__":
    unittest.main()
