"""测试公共工具：路径定位、端到端运行 main.py、数据文件隔离。

设计要点：
- 黑盒测试通过 subprocess 运行 src/main.py，并用 stdin 喂入模拟按键。
- 数据文件位于 <repo>/data/tasks.json。为避免污染真实数据，E2E 测试在运行前
  备份真实的 data/ 目录，运行后恢复；同时每个用例可指定初始数据。
- 所有与 main.py 交互都通过 run_main()，输入用 "\\n" 连接，模拟用户逐行回车。
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# 仓库根目录（tests/ 的上一级）
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_MAIN = REPO_ROOT / "src" / "main.py"
DATA_DIR = REPO_ROOT / "data"
DATA_FILE = DATA_DIR / "tasks.json"

# 优先用项目自带 venv 的 python，其次退回当前解释器
_VENV_PY = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
if not _VENV_PY.exists():
    _VENV_PY = REPO_ROOT / ".venv" / "bin" / "python"  # 兼容 Linux/macOS
PYTHON = str(_VENV_PY) if _VENV_PY.exists() else sys.executable

# 当前菜单编号（与 core/menuModule/menuFactory.py 的注册顺序一致）
MENU_VIEW_ALL = 1        # 查看全部任务
MENU_ADD = 2             # 添加任务
MENU_SEARCH = 3          # 搜索与筛选
MENU_DELETE = 4          # 删除任务
MENU_MARK_DONE = 5       # 标记任务完成
MENU_SET_DUE = 6         # 设置截止日期
MENU_SET_PRIORITY = 7    # 设置任务优先级
MENU_EXPORT = 8          # 任务清单导出
MENU_EXIT = 0            # 退出


class DataSandbox:
    """上下文管理器：备份并隔离真实的 data/ 目录。

    进入时把已有 data/ 移走并记录；退出时删除测试产生的 data/ 并恢复原目录。
    这样暴力测试可以随便写 data/tasks.json 而不影响用户真实数据。
    """

    def __init__(self):
        self._backup = None

    def __enter__(self):
        if DATA_DIR.exists():
            self._backup = Path(tempfile.mkdtemp(prefix="mytodo_backup_")) / "data"
            shutil.move(str(DATA_DIR), str(self._backup))
        return self

    def __exit__(self, exc_type, exc, tb):
        if DATA_DIR.exists():
            shutil.rmtree(DATA_DIR, ignore_errors=True)
        if self._backup is not None and self._backup.exists():
            shutil.move(str(self._backup), str(DATA_DIR))
            shutil.rmtree(self._backup.parent, ignore_errors=True)
        return False


def write_data(content: str, encoding: str = "utf-8"):
    """写入 data/tasks.json，content 是原始文本（便于测 BOM / 损坏数据）。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(content, encoding=encoding)


def write_data_bytes(raw: bytes):
    """写入 data/tasks.json 的原始字节（便于测 BOM）。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_bytes(raw)


def read_data() -> str:
    """读取当前 data/tasks.json 文本，不存在返回 None。"""
    if not DATA_FILE.exists():
        return None
    return DATA_FILE.read_text(encoding="utf-8")


def cleanup_data():
    """删除测试产生的 data/ 目录。"""
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR, ignore_errors=True)


def run_main(inputs, timeout: int = 30, env_extra: dict = None):
    """端到端运行 src/main.py，喂入 inputs（字符串列表，逐行）。

    返回 CompletedProcess，text 模式。stdout/stderr 已合并? 否——分开返回，
    这样测试可以断言"stderr 里不应有 Traceback"。
    """
    if isinstance(inputs, str):
        payload = inputs
    else:
        payload = "\n".join(str(i) for i in inputs)
        if payload and not payload.endswith("\n"):
            payload += "\n"

    env = os.environ.copy()
    # 强制 UTF-8，避免 Windows 控制台编码干扰断言
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    if env_extra:
        env.update(env_extra)

    return subprocess.run(
        [PYTHON, str(SRC_MAIN)],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        cwd=str(REPO_ROOT),
        env=env,
    )


def assert_no_traceback(testcase, proc):
    """断言进程输出里没有未捕获异常。"""
    combined = (proc.stdout or "") + (proc.stderr or "")
    testcase.assertNotIn("Traceback (most recent call last)", combined,
                         msg="程序抛出了未捕获异常:\n" + combined)
