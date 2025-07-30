from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation


class excelUtil:
  wb = None
  sourcePath = None
  savePath = None

  def __init__(self, path, save_path):
    # 创建一个 Workbook 对象
    self.wb = load_workbook(path)
    # 在 Workbook 中创建一个 Worksheet 对象
    self.ws = self.wb.active
    self.sourcePath = path
    self.savePath = save_path

  def makeDropData(self, col, drop_data):
    # 定义下拉框的数据
    dropdown_items = drop_data
    # 将下拉框数据转换成字符串
    dropdown_items_str = ','.join(dropdown_items)
    # 在第一列中添加下拉框
    dropdown_col = col
    dropdown_start_row = 2
    dropdown_end_row = 200
    # 配置下拉框参数
    dropdown = DataValidation(type="list", formula1=f'"{dropdown_items_str}"', allow_blank=True)
    # 添加下拉框到指定的单元格区域
    dropdown_range = f"{dropdown_col}{dropdown_start_row}:{dropdown_col}{dropdown_end_row}"
    self.ws.add_data_validation(dropdown)
    dropdown.add(dropdown_range)

  def save(self):
    # 保存工作簿
    self.wb.save(self.savePath)
