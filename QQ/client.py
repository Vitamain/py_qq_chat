import socket
import json
import time
from tkinter import ttk
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
        self.nickname = ''
        # 客户端账号
        self.username = ''
        # 目标对象
        self.target = 'all'

        # 创建并初始化登录界面
        self.draw_login_win()
        # 创建并初始化聊天界面
        self.draw_chat_win()
        # 隐藏聊天界面
        self.chat.withdraw()
        # 显示登录界面
        self.root.mainloop()
        self.get_user_list()


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
        if response_msg[0] == '00':
            tkinter.messagebox.showinfo('正确', '登录成功')
            self.nickname = response_msg[2]
            self.username = response_msg[1]
            # 隐藏登录窗口
            self.root.withdraw()
            # 显示聊天窗口
            self.chat.title("qq-聊天室         qq:%s             网名:%s" %(self.username,self.nickname))
            self.chat.deiconify()
            # 开启子线程去不断接收服务器的消息
            t = Thread(target=self.recv_msg, args=())
            t.daemon = True
            t.start()
            self.get_user_list()
        elif response_msg[0] == '01':
            tkinter.messagebox.showinfo('错误', '账号不存在或密码错误!')

    # 发送聊天消息到服务器
    def send_msg(self):
        # 清空输入框
        message = self.chat_area.get(0.0, END)
        self.clear_chat()
        # 发送聊天请求给服务器
        # 1|username|nickname|message|target 聊天请求格式
        chat_msg = '1|' + self.username + '|' + self.nickname + '|' + message + '|' + self.target
        self.client.send(chat_msg.encode('utf-8'))


    # 从服务器接收消息
    def recv_msg(self):
        while True:
            # 判断响应消息类型 (2,3,5)|message 2-普通消息 3-用户上下线消息 5-用户列表消息
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 当前时间
            response_msg = self.client.recv(1024).decode('utf-8').split('|')
            # 如果是用户上下线消息，需要重新获取在线用户列表，发送获取请求
            if (response_msg[0] == '3'):
                self.get_user_list()
            # 从客户端返回用户列表的 json 字符串
            elif (response_msg[0] == '5'):
                self.users = json.loads(response_msg[1].encode('utf-8'))
                print(self.users)
                # 刷新在线用户下拉框和在线用户列表
                list = ['all']
                self.user_alive.delete(0.0, END)
                for user, nickname in self.users.items():
                    if (user != self.username):
                        str = user + '|' + nickname
                        list.append(str)
                        self.user_alive.insert(tkinter.END, str + '\n')
                # 将列表转化为元组
                tup = tuple(list)
                self.user_list['value'] = tup
                self.user_list.current(0)
                continue

            # 将从服务器收到的信息打印在聊天界面
            self.scroll.insert(tkinter.END, now + "\n", 'green')
            self.scroll.insert(tkinter.END, response_msg[1]+"\n")

    # 发送获取用户列表请求
    def get_user_list(self):
        request_msg = '4|get_user_list'
        self.client.send(request_msg.encode('utf-8'))


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
        self.chat.geometry("750x450")

        # self.root.resizable(False)
        # 创建滚动文本框（聊天界面）
        self.scroll = ScrolledText(self.chat)
        self.scroll['height'] = 23
        self.scroll['width'] = 80
        self.scroll.grid(row=0, column=0, columnspan=2)
        # 设置聊天界面文本的颜色
        self.scroll.tag_config('green', foreground='#09F738')
        self.scroll.tag_config('red', foreground='red')

        # 格式化成 2021-05-27 11:45:39 形式
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.scroll.insert(tkinter.END, "欢迎进入聊天室，请畅所欲言!\n", 'red')

        # 创建文本域（输入）
        self.chat_area = Text(self.chat)
        self.chat_area['width'] = 80
        self.chat_area['height'] = 6
        self.chat_area.grid(row=1, column=0, pady=27)
        # 发送按钮
        self.login_button = Button(self.chat, text="发送", command=self.send_msg)
        self.login_button.place(x=260, y=415)
        # 在线用户下拉框
        self.label = Label(self.chat, text='聊天对象')
        self.label.place(x=10, y=305)
        # 创建变量，便于取值
        self.comvalue = StringVar()
        # 创建下拉框
        self.user_list = ttk.Combobox(self.chat, textvariable=self.comvalue)
        # 设置选项值
        self.user_list['value'] = ('all',)
        # 设置为活跃状态（下拉框的选项可变）
        self.user_list.config(state=ACTIVE)
        # 初始选中值
        self.user_list.current(0)

        # 在线用户列表
        self.user_label = Label(self.chat, text='在线用户')
        self.user_label.place(x=585, y=5)
        self.user_alive = ScrolledText(self.chat)
        self.user_alive['height'] = 30
        self.user_alive['width'] = 20
        self.user_alive.grid(row=0, column=0, columnspan=2)
        self.user_alive.place(x=585 ,y=25)

        # 刷新按钮
        #self.flush_button = Button(self.chat, text="刷新", commmand=self.get_user_list())
        # 绑定选中事件
        self.user_list.bind("<<ComboboxSelected>>", self.select_target)
        self.user_list.place(x=70, y=305)
        # 指定窗口关闭事件
        self.chat.protocol("WM_DELETE_WINDOW", self.callback)

    def select_target(self, *args):
        # 将目标对象 target 置为选中的值
        self.target = self.user_list.get()
        print(self.target)


    # 窗口关闭事件（释放资源）
    def callback(self):
        self.client.close()
        sys.exit(0)

    # 清空聊天输入框
    def clear_chat(self):
        self.chat_area.delete(0.0, END)
    # 清空登录框
    def clear_login(self):
        self.input_account.delete(0, END)
        self.input_password.delete(0, END)
        self.logined.deselect()

Client2()