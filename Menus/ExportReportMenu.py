"""
导出任务清单
使用依赖注入获取 TaskSystem 实例
"""

from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem

import html#生成HTML文件，实现导出后双击即可使用
from datetime import datetime#获取时间
from pathlib import Path#实现导出文件存放位置

DEFAULT_DIR=Path(__file__).resolve().parent.parent/"reports"#将文件存放位置默认在项目根目录下的reports/文件夹之中

class ExportReportMenu(Menu):
    def __init__(self,task_system: TaskSystem):
        super().__init__(
            "任务清单导出",
            "把当前清单导出成一个文件"
        )
        self.__task_system=task_system


    def execute(self) ->int:
        """获取任务清单，将任务清单按要求格式导出成一个文件"""
        try:
            output_dir=self._ask_output_dir()#问用户路径
            tasks=self._collect_tasks()#拉数据
            stats=self._compute_stats(tasks)#算统计
            today=datetime.now().date()#取今天
            html_text=self._render_html(tasks,stats,today)#拼HTML
            path=self._save_html(html_text,output_dir)#传入用户路径
            print(f"[完成] 已导出报告->{path}")
            return 0

        except Exception as e:
            print(f"[错误] 导出失败：{e}")
            return -1

    def _ask_output_dir(self)->Path:#用来让用户选择路径
        """问用户输出点，按回车用默认，路径不可用退回默认"""
        print(f"导出目录(默认{DEFAULT_DIR},直接回车使用):")
        raw=input(">").strip()

        if not raw:
            return DEFAULT_DIR
        try:#尝试用户输入路径是否可用
            user_path=Path(raw)
            user_path.mkdir(parents=True,exist_ok=True)
            return user_Path
        except(OSError,PermissionError) as e:
            print(f"[警告]无法使用该目录({e}),使用默认目录")
            return DEFAULT_DIR

    def _collect_tasks(self)->list:#拉取数据
        tasks=[]
        for i in range(self.__task_system.get_task_count()):
            t=self.__task_system.get_by_index(i)
            if t is not None:
                tasks.append(t)
        return tasks

    def _compute_stats(self,tasks:list)->dict:#统计数据
        today = datetime.now().date()#获取时间
        total=len(tasks)
        done=sum(1 for t in tasks if t.is_completed)
        undone=total-done
        overdue=sum(1 for t in tasks if self._is_overdue(t,today))
        rate=round(done/total*100,1)if total>0 else 0.0
        return{
            "total":total,
            "done":done,
            "undone":undone,
            "overdue":overdue,
            "rate":rate,
        }

    @staticmethod#判断是否逾期
    def _is_overdue(task,today)->bool:
        if task.is_completed or not task.has_due_date:
            return False
        return task.due_date.date() < today

    def _render_html(self, tasks: list, stats: dict, today) -> str:#拼接HTML
        today_str = today.strftime("%Y-%m-%d")
        rows_html = self._render_rows(tasks, today)
        bar_width = f"{stats['rate']}%"
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>任务清单报告 - {today_str}</title>
  <style>
    body  {{ font-family: -apple-system, "Microsoft YaHei", sans-serif;
             margin: 32px; color: #222; }}
    h1    {{ margin-bottom: 4px; }}
    .meta {{ color: #666; font-size: 14px; margin-bottom: 16px; }}
    .stats{{ display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 6px; }}
    .stat b{{ color: #0066cc; font-size: 18px; }}
    .bar  {{ width: 100%; height: 18px; background: #eee;
             border-radius: 9px; overflow: hidden; margin: 4px 0 24px; }}
    .fill {{ height: 100%; background: linear-gradient(90deg, #4caf50, #2e7d32);
             transition: width 0.4s; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td{{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }}
    th    {{ background: #f5f5f5; }}
    tr.overdue {{ background: #ffd6d6; color: #b00020; }} /* 标红 */
    tr.overdue td {{ font-weight: 600; }}
    .empty{{ text-align: center; color: #999; padding: 24px; }}
  </style>
</head>
<body>
  <h1>任务清单报告</h1>
  <div class="meta">生成日期：{today_str}</div>
  <div class="stats">
    <div class="stat">任务总数：<b>{stats['total']}</b></div>
    <div class="stat">已完成：<b>{stats['done']}</b></div>
    <div class="stat">未完成：<b>{stats['undone']}</b></div>
    <div class="stat">已逾期：<b>{stats['overdue']}</b></div>
    <div class="stat">完成率：<b>{stats['rate']}%</b></div>
  </div>
  <div class="bar"><div class="fill" style="width: {bar_width}"></div></div>
  <table>
    <thead>
      <tr><th>编号</th><th>优先级</th><th>截止日期</th><th>状态</th><th>标题</th></tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</body>
</html>"""

    def _render_rows(self, tasks: list, today) -> str:#拼表格
        if not tasks:
            return '<tr><td colspan="5" class="empty">暂无任务</td></tr>'
        parts = []
        for i, t in enumerate(tasks, 1):
            cls = "overdue" if self._is_overdue(t, today) else ""
            due_str = t.due_date.strftime("%Y-%m-%d") if t.has_due_date else "—"
            status = "已完成" if t.is_completed else "未完成"
            title = html.escape(t.title)
            prio = t.priority.value
            parts.append(
                f'<tr class="{cls}">'
                f'<td>{i}</td><td>{prio}</td><td>{due_str}</td>'
                f'<td>{status}</td><td>{title}</td>'
                f'</tr>'
            )
        return "\n      ".join(parts)

    def _save_html(self, html_text: str, output_dir: Path) -> Path:#写文件
        output_dir.mkdir(parents=True, exist_ok=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        path = output_dir / f"report_{today_str}.html"
        path.write_text(html_text, encoding="utf-8")
        return path