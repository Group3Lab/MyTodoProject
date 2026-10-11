"""
任务统计图表菜单
用 OpenCV 生成任务优先级统计图，保存为 chart.png
"""

import cv2
import numpy as np
from datetime import date

from core.menuModule.menu import Menu
from core.taskModule.taskSystem import TaskSystem


class ChartMenu(Menu):
    def __init__(self, task_system: TaskSystem):
        super().__init__(
            "任务统计图表",
            "生成高/中/低优先级任务数量统计图，保存为 chart.png"
        )
        self.__task_system = task_system

    def execute(self) -> int:
        """生成统计图表"""
        try:
            high, mid, low = self.__count_by_priority()
            path = self.__draw_chart(high, mid, low)
            print(f"[完成] 统计图已保存 -> {path}")
            return 0
        except Exception as e:
            print(f"[错误] 生成图表失败: {e}")
            return -1

    def __count_by_priority(self):
        """统计高/中/低优先级各有多少条任务"""
        high = 0
        mid = 0
        low = 0

        count = self.__task_system.get_task_count()
        for i in range(count):
            task = self.__task_system.get_by_index(i)
            name = task.priority.name      # High / Medium / Low
            if name == "High":
                high += 1
            elif name == "Medium":
                mid += 1
            else:
                low += 1

        return high, mid, low

    def __draw_chart(self, high, mid, low):
        """用 OpenCV 画条形图并保存为 chart.png"""
        # 画布：640 宽 x 480 高，白色背景
        img = np.ones((480, 640, 3), dtype=np.uint8) * 255

        # 标题（cv2.putText 只支持英文，所以标题用英文）
        cv2.putText(img, "Task Priority Chart", (140, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

        # 日期标注
        today = date.today().strftime("%Y-%m-%d")
        cv2.putText(img, "Date: " + today, (20, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)

        # 三个条形的数据：名称、数量、颜色（BGR 顺序）
        data = [
            ("High",   high, (255, 100, 0)),
            ("Medium", mid,  (0, 180, 0)),
            ("Low",    low,  (0, 0, 220)),
        ]

        x = 80            # 第一根条形的左边位置
        bar_width = 100   # 条形宽度
        max_height = 300  # 数量最多的那根条形的高度
        base_y = 420      # 底部基线的 y 坐标

        # 找最大数量，至少为 1，防止除以 0
        max_count = max(high, mid, low, 1)

        for name, value, color in data:
            # 条形高度按数量比例缩放
            bar_height = int(value / max_count * max_height)
            top_y = base_y - bar_height

            # 画实心矩形（-1 表示填充）
            cv2.rectangle(img, (x, top_y), (x + bar_width, base_y), color, -1)

            # 条形上方标数字
            cv2.putText(img, str(value), (x + 40, top_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

            # 底部标名称
            cv2.putText(img, name, (x + 20, base_y + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

            x += 160   # 移到下一根条形的位置

        # 保存到项目根目录下的 chart.png
        path = "chart.png"
        cv2.imwrite(path, img)
        return path
