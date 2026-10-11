"""白盒单测：TaskSystem（core/taskModule/taskSystem.py）。

覆盖：增删、按索引读取（返回内部引用）、计数、更新方法、越界处理。
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.taskModule.task import Priority, Task
from core.taskModule.taskSystem import TaskSystem


def make_ts(n=0):
    ts = TaskSystem()
    for i in range(n):
        ts.add(Task(f"任务{i + 1}"))
    return ts


class TestAddAndCount(unittest.TestCase):
    def test_add_returns_task(self):
        ts = TaskSystem()
        t = Task("x")
        self.assertIs(ts.add(t), t)
        self.assertEqual(ts.get_task_count(), 1)

    def test_add_many(self):
        ts = make_ts(5)
        self.assertEqual(ts.get_task_count(), 5)


class TestCreateFromList(unittest.TestCase):
    def test_from_list(self):
        ts = TaskSystem.CreateFromList([Task("a"), Task("b")])
        self.assertEqual(ts.get_task_count(), 2)

    def test_from_empty(self):
        self.assertEqual(TaskSystem.CreateFromList([]).get_task_count(), 0)

    def test_from_none(self):
        self.assertEqual(TaskSystem.CreateFromList(None).get_task_count(), 0)

    def test_copies_list_not_alias(self):
        src = [Task("a")]
        ts = TaskSystem.CreateFromList(src)
        src.append(Task("b"))
        self.assertEqual(ts.get_task_count(), 1, "应复制列表，不受外部追加影响")


class TestIndexAccess(unittest.TestCase):
    def test_get_by_index_returns_reference(self):
        """已移除 deepcopy 保护：get_by_index 返回内部引用，改动会直接生效。"""
        ts = make_ts(1)
        got = ts.get_by_index(0)
        self.assertIs(got, ts.get_by_index(0))  # 同一个对象（引用）
        got.is_completed = True
        self.assertTrue(ts.get_by_index(0).is_completed)

    def test_get_out_of_range_returns_none(self):
        ts = make_ts(2)
        self.assertIsNone(ts.get_by_index(-1))
        self.assertIsNone(ts.get_by_index(2))
        self.assertIsNone(ts.get_by_index(999))

    def test_get_all_tasks_returns_reference(self):
        """已移除 deepcopy 保护：get_all_tasks 返回内部列表引用。"""
        ts = make_ts(2)
        all_tasks = ts.get_all_tasks()
        self.assertIs(all_tasks, ts.get_all_tasks())  # 同一个列表对象（引用）
        all_tasks.pop()
        self.assertEqual(ts.get_task_count(), 1)


class TestDelete(unittest.TestCase):
    def test_delete_valid(self):
        ts = make_ts(3)
        self.assertTrue(ts.delete(1))
        self.assertEqual(ts.get_task_count(), 2)

    def test_delete_invalid(self):
        ts = make_ts(1)
        self.assertFalse(ts.delete(5))
        self.assertFalse(ts.delete(-1))
        self.assertEqual(ts.get_task_count(), 1)


class TestUpdateMethods(unittest.TestCase):
    def test_update_completed(self):
        ts = make_ts(1)
        self.assertTrue(ts.update_completed(0, True))
        self.assertTrue(ts.get_by_index(0).is_completed)

    def test_update_priority(self):
        ts = make_ts(1)
        self.assertTrue(ts.update_priority(0, Priority.High))
        self.assertEqual(ts.get_by_index(0).priority, Priority.High)

    def test_update_due_date(self):
        ts = make_ts(1)
        self.assertTrue(ts.update_due_date(0, datetime(2026, 1, 1)))
        self.assertEqual(ts.get_by_index(0).due_date, datetime(2026, 1, 1))

    def test_updates_out_of_range_return_false(self):
        ts = make_ts(1)
        self.assertFalse(ts.update_completed(9, True))
        self.assertFalse(ts.update_priority(9, Priority.High))
        self.assertFalse(ts.update_due_date(9, datetime(2026, 1, 1)))


if __name__ == "__main__":
    unittest.main()
