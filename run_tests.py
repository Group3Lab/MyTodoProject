#!/usr/bin/env python3
"""MyTodoProject 全自动测试脚本。

用法（在仓库根目录执行）：
    python run_tests.py            # 运行全部测试
    python run_tests.py -v         # 详细输出
    python run_tests.py brute      # 只跑黑盒暴力测试
    python run_tests.py unit       # 只跑白盒单测
    python run_tests.py -k task    # 只跑名字含 "task" 的用例

特性：
- 纯标准库，无需安装任何依赖。
- 自动发现 tests/ 下所有 test_*.py 并运行。
- 结束后自动清理测试产生的 data/、reports/ 等临时产物。
- 退出码：0=全部通过，1=有失败。
"""

import argparse
import shutil
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
TESTS_DIR = REPO_ROOT / "tests"
sys.path.insert(0, str(REPO_ROOT))

# 测试可能产生的临时产物（结束后清理）
_ARTIFACTS = [REPO_ROOT / "data", REPO_ROOT / "reports"]


def _cleanup():
    for p in _ARTIFACTS:
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)


def _select_suite(args):
    """根据命令行参数挑选要运行的用例。"""
    loader = unittest.TestLoader()
    if args.group == "brute":
        return loader.discover(str(TESTS_DIR), pattern="test_brute_force.py")
    if args.group == "unit":
        suite = unittest.TestSuite()
        for pattern in ("test_task_model.py", "test_task_system.py",
                        "test_persistence.py", "test_menus.py"):
            suite.addTests(loader.discover(str(TESTS_DIR), pattern=pattern))
        return suite
    if args.keyword:
        return loader.discover(str(TESTS_DIR), pattern="test_*.py",
                               top_level_dir=str(REPO_ROOT))
    return loader.discover(str(TESTS_DIR), pattern="test_*.py",
                           top_level_dir=str(REPO_ROOT))


def main():
    parser = argparse.ArgumentParser(description="MyTodoProject 全自动测试")
    parser.add_argument("group", nargs="?", default="all",
                        choices=["all", "brute", "unit"],
                        help="测试分组：all/brute/unit")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("-k", "--keyword", default=None,
                        help="按关键字过滤测试方法名")
    args, _ = parser.parse_known_args()

    # 运行前先清理，保证起点干净
    _cleanup()

    suite = _select_suite(args)

    if args.keyword:
        filter_suite = unittest.TestSuite()
        for test in _iter_tests(suite):
            if args.keyword.lower() in test.id().lower():
                filter_suite.addTest(test)
        suite = filter_suite

    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)

    print("=" * 64)
    print("MyTodoProject 测试")
    print(f"仓库根目录: {REPO_ROOT}")
    print(f"分组: {args.group}   用例总数: {suite.countTestCases()}")
    print("=" * 64)

    result = runner.run(suite)

    # 结束清理
    _cleanup()

    print("=" * 64)
    failed = len(result.failures) + len(result.errors)
    if failed == 0:
        print(f"全部通过 ✓  共 {result.testsRun} 个用例")
    else:
        print(f"失败/错误 {failed} 个（共 {result.testsRun} 个用例）")
    print("=" * 64)
    return 0 if failed == 0 else 1


def _iter_tests(suite):
    """递归展开 suite，得到所有 TestCase 实例。"""
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _iter_tests(item)
        else:
            yield item


if __name__ == "__main__":
    sys.exit(main())
