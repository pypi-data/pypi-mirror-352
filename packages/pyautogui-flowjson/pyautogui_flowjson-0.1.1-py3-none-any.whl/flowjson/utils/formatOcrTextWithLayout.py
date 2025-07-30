from typing import Tuple

# TODO: 需要优化
def formatOcrTextWithLayout(results, y_threshold=30, x_threshold=30) -> str:
    # y_threshold: 判断是否换行的y轴距离阈值 标准行高，用于计算换行数
    # x_threshold: 判断是否加空格的x轴距离阈值 标准字符宽度，用于计算空格数
    lines: Tuple[float, float, str] = []
    for res in results:
        for line in res:
            # [左上角坐标, 右上角坐标, 右下角坐标, 左下角坐标], (文本, 置信度)
            coordinates, (text, confidence) = line
            x_min = min([coord[0] for coord in coordinates])  # coordinates[0][0]
            y_min = min([coord[1] for coord in coordinates])  # coordinates[0][1]
            lines.append((y_min, x_min, text))

    # 对文本行进行排序
    lines.sort(key=lambda x: (x[0], x[1]))  # 先按Y轴再按X轴排序

    # 用于存储最终文本
    final_text = ""
    pre_lt_x = 0
    pre_lt_y = 0

    for y, x, text in lines:
        if y > pre_lt_y + y_threshold:
            # 计算换行数
            newlines = int((y - pre_lt_y) // y_threshold)
            final_text += "\n" * newlines
        elif x > pre_lt_x + x_threshold:
            # 计算空格数
            spaces = int((x - pre_lt_x) // x_threshold)
            final_text += " " * spaces

        final_text += text
        pre_lt_y, pre_lt_x = y, x

    return final_text
