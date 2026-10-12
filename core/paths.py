"""运行期根目录定位：开发时用项目根目录，打包成 exe 后用 exe 所在目录。

打包后（PyInstaller）模块的 __file__ 指向内部解包目录（onefile 的临时目录、
onedir 的 _internal），把数据写在那里会导致：
- onefile：程序退出即被删除，数据丢失；
- onedir：数据埋在 _internal 里，用户找不到。

因此统一以「可写根目录」为基准：
- 已打包（sys.frozen 为真）：返回 exe 所在目录；
- 未打包：返回项目根目录（core 的上一级）。
"""

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """返回可写的根目录，data/ 与 reports/ 都放在它下面。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent
