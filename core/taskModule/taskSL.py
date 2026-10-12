import json#实现保存和读取
from pathlib import Path#实现存放文件
from datetime import datetime#获取时间
from core.taskModule.task import Task,Priority
from core.paths import get_base_dir

"""实现文件存在可写根目录的 /data 之中"""
_DATA_DIR = get_base_dir() / "data"
_DATA_FILE = _DATA_DIR / "tasks.json"

def _task_to_dict(task: Task) -> dict:#实现将Task转化为json
    return {
        "title": task.title,
        "priority": task.priority.value,
        "due_date": task.due_date.strftime("%Y-%m-%d") if task.has_due_date else None,
        "is_completed": task.is_completed,
    }

def _dict_to_task(item: dict) -> Task:#实现将json变回Task
    task = Task(item["title"])
    task.priority = Priority(item["priority"])
    if item.get("due_date"):
        task.due_date = datetime.strptime(item["due_date"], "%Y-%m-%d")
    task.is_completed = bool(item.get("is_completed", False))
    return task

# 失败的时候返回false
def taskSave(data : list[Task])->bool:#实现自动保存文件
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)#目录不存在自动建目录
        payload = [_task_to_dict(t) for t in data]
        with open(_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[错误] 任务数据保存失败: {e}")
        return False

# 失败的时候返回None
def taskLoad()->list[Task]:#实现自动读取文件
    if not _DATA_FILE.exists():#首次运行时没有文件处理
        return []
    try:
        # 用 utf-8-sig 读取：兼容有无 BOM 的文件（记事本等编辑器保存会加 BOM）
        with open(_DATA_FILE, "r", encoding="utf-8-sig") as f:
            payload = json.load(f)
    except Exception as e:
        print(f"[错误] 任务数据文件读取失败: {e}")
        return None

    tasks = []
    for item in payload:
        try:
            tasks.append(_dict_to_task(item))
        except Exception:
            continue
    return tasks