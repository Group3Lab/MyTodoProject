# Python 环境使用说明

本文档说明如何在本地搭好 MyTodoProject 的 Python 运行环境，面向**第一次 clone 仓库**的组员。
照着做一遍即可跑起程序，不需要额外的 IDE 配置知识。

---

## 一、需要什么

| 项 | 要求 | 说明 |
| --- | --- | --- |
| Python | **3.10 及以上**（推荐 3.12） | 代码用了 `list[Task]`、`tuple[...]` 等泛型语法，3.9 会报错 |
| 第三方库 | `opencv-python`、`numpy` | **只有统计图表功能用到**（`Menus/ChartMenu.py`）；其余功能是纯标准库 |
| 包管理器 | `pip`（Python 自带） | 无需 conda |

> 不装 `opencv-python` 也能跑所有**必做功能**；只有主菜单「9.任务统计图表」会因为 `import cv2` 失败。为了完整，建议按下面装好。

---

## 二、快速开始（三步）

在**仓库根目录**执行。Windows 用 `python`，macOS/Linux 若同时装了 2.x/3.x 请用 `python3`。

### 第 1 步：创建虚拟环境

```bash
# Windows
python -m venv .venv

# macOS / Linux
python3 -m venv .venv
```

### 第 2 步：激活虚拟环境

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

激活成功后命令行前面会多出 `(.venv)` 前缀。

> **PowerShell 报「禁止运行脚本」**？执行一次：
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
> 或者不激活，直接用 `.venv\Scripts\python.exe` 代替 `python`（见第四节）。

### 第 3 步：安装依赖

```bash
pip install -r requirements.txt
```

装完即可运行：

```bash
python src/main.py      # 运行程序
python run_tests.py     # 跑测试
```

---

## 三、依赖说明（requirements.txt）

仓库根目录的 [requirements.txt](../requirements.txt) 固定了本项目的第三方依赖：

```
opencv-python
numpy
```

- 只有 `Menus/ChartMenu.py`（生成 `chart.png` 统计图）用得到它们。
- `numpy` 通常是 `opencv-python` 的连带依赖，但显式写上更稳妥。
- 其余全部功能（增删改查、搜索筛选、统计、导出报告、数据保存）**只用标准库**，不需要额外安装。

> 如果只是来改必做功能的代码、不碰统计图，可以不装这两个库，直接跑 `python src/main.py` 也不会报错（只在使用图表菜单时才需要）。

---

## 四、不激活虚拟环境也能跑（推荐给怕麻烦的人）

虚拟环境的意义只是隔离依赖，不激活也行——直接指定解释器路径即可：

```bash
# Windows
.venv\Scripts\python.exe src\main.py
.venv\Scripts\python.exe run_tests.py

# macOS / Linux
.venv/bin/python src/main.py
.venv/bin/python run_tests.py
```

项目里的 [run_tests.py](../run_tests.py) 与 [tests/helpers.py](../tests/helpers.py) 会**自动优先使用 `.venv` 里的 Python**，所以只要你建好 `.venv`，跑测试时不必先激活。

---

## 五、常见问题

### Q1：`python` 命令找不到？
- Windows：装 Python 时勾选 **Add Python to PATH**；或重装勾上。
- 已装仍找不到：用 `py -3 -m venv .venv` 代替 `python -m venv .venv`（Windows 的 `py` 启动器）。

### Q2：`ModuleNotFoundError: No module named 'cv2'`
没装依赖，或装到了别的 Python 环境里。确认已激活 `.venv` 后执行：

```bash
pip install -r requirements.txt
```

### Q3：装依赖时报权限错误（Permission denied / 拒绝访问）
说明你在往**系统 Python** 里装而不是虚拟环境。先按第二节建好并激活 `.venv`，再装。

### Q4：`Set-ExecutionPolicy` 会不会有安全风险？
`RemoteSigned` 只对"从网上下载的脚本"要求签名，本地自己写的脚本可正常跑，是微软推荐的开发档位，风险很低。

### Q5：网络慢 / pip 安装超时？
换国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q6：`.venv` 要提交到 Git 吗？
**不要。** [.gitignore](../.gitignore) 已忽略 `.venv/`、`venv/`。每个人本地各建一份；依赖靠 `requirements.txt` 共享，不要提交虚拟环境文件夹。

### Q7：`data/`、`chart.png`、`reports/` 是啥？要提交吗？
都是**程序运行产生的输出**（任务数据、统计图、导出报告），已被 `.gitignore` 忽略，不需要也不应该提交。详见 [测试指南](./测试指南.md) 的「数据隔离与自动清理」。

---

## 六、一句话总结

```bash
python -m venv .venv
# 激活（或直接用 .venv/Scripts/python.exe）
pip install -r requirements.txt
python src/main.py
```

- 依赖清单：[requirements.txt](../requirements.txt)
- 加功能看：[添加新功能指南](./添加新功能指南.md)
- 改完自测：[测试指南](./测试指南.md)
