import socket
import time
from tkinter.scrolledtext import ScrolledText
from mttkinter import mtTkinter as tkinter
from config import *
from tkinter import *
from threading import Thread
import tkinter.messagebox
import sys

class Client2:
    def __init__(self):
        # 创建并初始化客户端套接字
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接到指定服务器
        self.client.connect((SERVER_IP, SERVER_PORT))
        # 客户端网名
        self.nickname=''
        # 客户端账号
        self.username=''

        # 创建并初始化登录界面
        self.draw_login_win()
        # 创建并初始化聊天界面
        self.draw_chat_win()
        # 隐藏聊天界面
        self.chat.withdraw()
        # 显示登录界面
        self.root.mainloop()

    def login(self):
        # 获取账号和密码
        account = self.input_account.get()
        passwd = self.input_password.get()
        if (account == ""):
            tkinter.messagebox.showinfo('错误', '账号不能为空!')
            return
        if (passwd == ""):
            tkinter.messagebox.showinfo('错误', '密码不能为空!')
            return
        # 发送登录信息给服务器  0|username|passwd 登录请求格式
        login_msg = '0|' + account + '|' + passwd
        self.client.send(login_msg.encode('utf-8'))
        # 接收登录响应信息
        # 2|username|nickname|登录成功!  3|fail|登录失败!
        response_msg = self.client.recv(1024).decode('utf-8').split('|')
        # 登录成功
        if response_msg[0] == '2':
            tkinter.messagebox.showinfo('正确', '登录成功')
            self.nickname = response_msg[2]
            self.username = response_msg[1]
            # 隐藏登录窗口
            self.root.withdraw()
            # 显示聊天窗口
            self.chat.title("qq-聊天室   qq:%s  网名:%s" %(self.username,self.nickname))
            self.chat.deiconify()
            # 开启子线程去不断接收服务器的消息
            t = Thread(target=self.recv_msg, args=())
            t.daemon = True
            t.start()
        elif response_msg[0] == '3':
            tkinter.messagebox.showinfo('错误', '账号不存在或密码错误!')

    # 发送聊天消息到服务器
    def send_msg(self):
        # 清空输入框
        message = self.chat_area.get(0.0, END)
        self.clear_chat()
        # 发送聊天请求给服务器
        # 1|username|nickname|message 聊天请求格式
        chat_msg = '1|' + self.username + '|' + self.nickname + '|' + message
        self.client.send(chat_msg.encode('utf-8'))


    # 从服务器接收消息
    def recv_msg(self):
        while True:
            # 将从服务器收到的信息打印在聊天界面
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 当前时间
            response_msg = self.client.recv(1024).decode('utf-8')
            self.scroll.insert(tkinter.END, now + "\n", 'green')
            self.scroll.insert(tkinter.END, response_msg+"\n")

    # 创建登录窗口
    def draw_login_win(self):
        # 创建窗口对象 root，并设置标题和大小
        self.root = Tk()
        self.root.title("登录界面")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", )

        # 创建画布
        self.canvas = Canvas(self.root, height=200, width=500)
        self.root.image_file = PhotoImage(file="2.png")
        self.root.image = self.canvas.create_image(0, 0, anchor='nw', image=self.root.image_file)
        self.canvas.pack(side="top")

        # 账号密码文本框
        self.label_account = Label(self.root, text='账号: ')
        self.label_password = Label(self.root, text='密码: ')
        self.input_account = Entry(self.root, width=30)
        self.input_password = Entry(self.root, show="*", width=30)

        # 登录和注册按钮
        self.login_button = Button(self.root, text="登录", bg="lightblue", command=self.login)
        self.siginUp_button = Button(self.root, text="重置", bg="lightblue", command=self.clear_login)
        self.logined = Checkbutton(self.root, text="记住密码")

        # 位置调整
        self.label_account.place(x=60, y=170)
        self.label_password.place(x=60, y=205)
        self.input_account.place(x=100, y=170)
        self.input_password.place(x=100, y=205)
        self.logined.place(x=320, y=205)
        self.login_button.place(x=100, y=250)
        self.siginUp_button.place(x=240, y=250)

        # 设置窗口不能拉伸
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

    # 创建聊天窗口
    def draw_chat_win(self):
        self.chat = Tk()
        self.chat.title("QQ-聊天室")
        self.chat.geometry("580x430")

        # self.root.resizable(False)
        # 创建滚动文本框（聊天界面）
        self.scroll = ScrolledText(self.chat)
        self.scroll['height'] = 23
        self.scroll['width'] = 80
        self.scroll.grid(row=0, column=0, columnspan=2)
        # 设置聊天界面文本的颜色
        self.scroll.tag_config('green', foreground='#09F738')
        self.scroll.tag_config('red', foreground='red')

        # 格式化成 2016-03-20 11:45:39 形式
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.scroll.insert(tkinter.END, "欢迎进入聊天室，请畅所欲言!\n", 'red')

        # 创建文本域（输入）
        self.chat_area = Text(self.chat)
        self.chat_area['width'] = 80
        self.chat_area['height'] = 6
        self.chat_area.grid(row=1, column=0, pady=10)

        self.login_button = Button(self.chat, text="发送", command=self.send_msg)
        self.login_button.place(x=270, y=390)
        self.chat.protocol("WM_DELETE_WINDOW", self.callback)

    # 窗口关闭事件（释放资源）
    def callback(self):
        self.client.close()
        sys.exit(0)

    # 清空聊天输入框
    def clear_chat(self):
        self.chat_area.delete(0.0, END)
    # 情况登录框
    def clear_login(self):
        self.input_account.delete(0, END)
        self.input_password.delete(0, END)
        self.logined.deselect()

Client2()