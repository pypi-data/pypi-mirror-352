import tkinter
import tkinter as tk
from io import BytesIO
from tkinter import ttk

import requests
from PIL import Image, ImageTk


def showImageTip(root, title, imagePath, tips):
  # 创建一个Tk对象
  if root:
    window = root
  else:
    window = tk.Tk()
  # 设置窗口大小和位置
  win_width = 400
  win_height = 480
  screen_width = window.winfo_screenwidth()
  screen_height = window.winfo_screenheight()
  x = int((screen_width - win_width) / 2)
  y = int((screen_height - win_height) / 2)
  window.geometry("{}x{}+{}+{}".format(win_width, win_height, x, y))

  # 设置窗口大小和标题
  window.title(title)

  # 创建一个Label控件用于显示图片
  resp = requests.get(imagePath)
  image = Image.open(BytesIO(resp.content))  # 替换你自己的图片路径
  image = image.resize((400, 400))
  photo = ImageTk.PhotoImage(image)
  label1 = ttk.Label(window, image=photo)
  label1.pack(side=tkinter.TOP)

  # 创建一个Label控件用于显示提示文字
  label2 = ttk.Label(window, text=tips, font=("Arial Bold", 16))
  label2.config(anchor='center', justify='center')
  label2.pack(side=tkinter.BOTTOM)
  # 显示窗口
  window.mainloop()


if __name__ == '__main__':
  showImageTip(root=None, title='在线授权', imagePath='https://blog.gomyck.com/img/pay-img/wechatPay2Me.jpg', tips='{}\n授权已失效,请联系微信:\n{}'.format(123, 123))
