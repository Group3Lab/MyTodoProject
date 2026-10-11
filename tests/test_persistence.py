"""白盒单测：持久化层 taskSL（core/taskModule/taskSL.py）。

覆盖：保存/读取往返、BOM 兼容、缺失文件、损坏数据、目录自动创建。
测试通过 monkeypatch 把 _DATA_DIR/_DATA_FILE 指到临时目录，隔离真实数据。
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.taskModule import taskSL
from core.taskModule.task import Priority, Task


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self._dir = Path(self._tmp.name) / "data"
        # monkeypatch 模块级路径常量
        self._old_dir = taskSL._DATA_DIR
        self._old_file = taskSL._DATA_FILE
        taskSL._DATA_DIR = self._dir
        taskSL._DATA_FILE = self._dir / "tasks.json"

    def tearDown(self):
        taskSL._DATA_DIR = self._old_dir
        taskSL._DATA_FILE = self._old_file
        self._tmp.cleanup()

    def _sample(self):
        t1 = Task("写高数作业")
        t1.priority = Priority.High
        t1.due_date = datetime(2026, 10, 8)
        t2 = Task("背书")
        t2.priority = Priority.Low
        t2.is_completed = True
        return [t1, t2]

    def test_save_creates_dir_and_file(self):
        self.assertFalse(self._dir.exists())
        self.assertTrue(taskSL.taskSave(self._sample()))
        self.assertTrue(taskSL._DATA_FILE.exists())

    def test_roundtrip(self):
        original = self._sample()
        self.assertTrue(taskSL.taskSave(original))
        loaded = taskSL.taskLoad()
        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].title, "写高数作业")
        self.assertEqual(loaded[0].priority, Priority.High)
        self.assertEqual(loaded[0].due_date, datetime(2026, 10, 8))
        self.assertFalse(loaded[0].is_completed)
        self.assertEqual(loaded[1].title, "背书")
        self.assertTrue(loaded[1].is_completed)
        self.assertFalse(loaded[1].has_due_date)

    def test_load_missing_file_returns_empty_list(self):
        self.assertEqual(taskSL.taskLoad(), [])

    def test_saved_file_has_no_bom(self):
        taskSL.taskSave(self._sample())
        raw = taskSL._DATA_FILE.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), "自写文件不应带 BOM")

    def test_load_utf8_with_bom(self):
        """兼容记事本另存产生的带 BOM 文件（回归用例）。"""
        content = '[{"title": "测试", "priority": "高", "due_date": null, "is_completed": false}]'
        self._dir.mkdir(parents=True, exist_ok=True)
        taskSL._DATA_FILE.write_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))
        loaded = taskSL.taskLoad()
        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].title, "测试")

    def test_load_corrupt_json_returns_none(self):
        self._dir.mkdir(parents=True, exist_ok=True)
        taskSL._DATA_FILE.write_text("{ not valid json", encoding="utf-8")
        self.assertIsNone(taskSL.taskLoad())

    def test_load_skips_corrupt_records(self):
        """单条记录损坏时应跳过它，但保留其它正常记录。"""
        content = (
            '[{"title": "正常", "priority": "高", "due_date": null, "is_completed": false},'
            ' {"title": "损坏", "priority": "unknown", "due_date": null, "is_completed": false}]'
        )
        self._dir.mkdir(parents=True, exist_ok=True)
        taskSL._DATA_FILE.write_text(content, encoding="utf-8")
        loaded = taskSL.taskLoad()
        self.assertEqual([t.title for t in loaded], ["正常"])

    def test_save_overwrites_previous(self):
        taskSL.taskSave(self._sample())
        taskSL.taskSave([Task("only")])
        loaded = taskSL.taskLoad()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].title, "only")


if __name__ == "__main__":
    unittest.main()
