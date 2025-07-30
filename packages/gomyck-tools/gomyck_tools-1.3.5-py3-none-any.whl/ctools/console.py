import logging
import sys
import tkinter as tk


class Console:

  def __init__(self, master):
    self.master = master

    # 创建文本框和滚动条
    self.textbox = tk.Text(self.master, wrap=tk.NONE)

    self.vertical_scrollbar = tk.Scrollbar(self.textbox, command=self.textbox.yview)
    self.horizontal_scrollbar = tk.Scrollbar(self.textbox, command=self.textbox.xview, orient=tk.HORIZONTAL)

    self.textbox.configure(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)
    self.textbox.pack(side=tk.LEFT, pady=10, padx=10, ipadx=10, ipady=10, fill=tk.BOTH, expand=True)

    self.vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # 将标准输出和标准错误输出重定向到文本框中
    sys.stdout = self
    sys.stderr = self

    # # 创建输入框和按钮
    # self.entry = tk.Entry(self.master)
    # self.entry.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
    # self.button = tk.Button(self.master, text="Send", command=self.send)
    # self.button.pack(side=tk.BOTTOM)

    # 将日志输出到文本框中
    self.log_handler = logging.StreamHandler(self)
    self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logging.getLogger().addHandler(self.log_handler)
    # logging.getLogger().setLevel(logging.INFO)

  def write(self, message):
    # 在文本框中输出消息
    self.textbox.insert(tk.END, message + '\n')
    self.textbox.see(tk.END)

  def flush(self):
    pass

  def send(self):
    # 获取输入框中的文本并打印到控制台
    text = self.entry.get()
    print(text)
    self.entry.delete(0, tk.END)

  def __del__(self):
    # 关闭日志处理器
    logging.getLogger().removeHandler(self.log_handler)
