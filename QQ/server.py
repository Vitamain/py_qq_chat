import socket
from config import *
from threading import Thread
from db import *

class Server:
    def __init__(self):
        # 创建套接字并指定套接字的类型 AF_INET(套接字家族)--ipV4 ,SOCK_STREAM(套接字类型)--TCP
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 创建在线用户列表
        self.alive_user = {}

        # 初始化套接字，绑定 ip 地址和 端口号
        self.server.bind((SERVER_IP, SERVER_PORT))
        # 设置监听状态，指定 TCP 连接数量
        self.server.listen(10)
        print('服务器已启动...... ')
        print('本机 ip: ', SERVER_IP)
        print('本机 port:', SERVER_PORT)
        # 等待客户端连接 accept() 返回元组（客户端套接字，客户端 ip 地址）
        while True:
            client, addr = self.server.accept();
            print(addr, '已连接!')

            # 创建一个子线程去处理与当前客户端的交互
            # target: 指定线程执行的函数  args: 函数形参
            t = Thread(target=self.request_handler, args=(client, addr))
            t.start()

    # 处理客户端请求的目标函数
    def request_handler(self, client, addr):
        while True:
            try:
                # 接收客户端的消息
                # 0|username|passwd 登录请求格式
                # 1|username|nickname|message 聊天请求格式
                request_msg = client.recv(1024).decode('utf-8').split('|');
                if (request_msg[0] == '0'):
                    login_msg = {}
                    login_msg['username'] = request_msg[1]
                    login_msg['passwd'] = request_msg[2]
                    # 处理登录请求 0|username|passwd
                    self.login_handler(client, login_msg)
                elif (request_msg[0] == '1'):
                    chat_msg = {}
                    chat_msg['username'] = request_msg[1]
                    chat_msg['nickname'] = request_msg[2]
                    chat_msg['message'] = request_msg[3]
                    # 处理聊天请求 1|username|nickname|message
                    self.chat_handler(client, chat_msg)
            except ConnectionResetError:
                print(addr, '断开连接!')
                # 客户端下线，将客户端从在线用户列表删除
                self.remove_user(client)
                # 关闭套接字
                client.close()
                break

    # 处理用户的登录请求
    def login_handler(self, client, login_msg):
        # 根据用户的登录信息（username, passwd）查询用户信息
        # res: (id, username, passwd, nickname)
        res = DB.find_user(login_msg['username'], login_msg['passwd'])
        # 向客户端返回登录响应信息
        # 2|username|nickname|登录成功!  3|fail|登录失败!
        if res == None:
            response_msg = '3|fail|登录失败!'
        else:
            print('(' + login_msg['username'] + ')' + res[3], '已上线!')
            response_msg = '2|'  + res[1] + '|'+ res[3] + '|登录成功!'
            # 将用户添加到在线用户列表
            self.alive_user[login_msg['username']] = {'socket' : client, 'nickname' : res[3]}
            # 将用户登录成功信息群发
            self.mass_distribution_login(res, login_msg['username'])
        client.send(response_msg.encode('utf-8'))

    # 处理用户的聊天请求
    def chat_handler(self, client, chat_msg):
        # 将用户聊天消息群发即可
        response_msg = '(' + chat_msg['username'] + ')' + chat_msg['nickname'] + ': ' + chat_msg['message']
        for user, temp in self.alive_user.items():
            temp['socket'].send(response_msg.encode('utf-8'))

    # 登录信息群发功能
    def mass_distribution_login(self, res, username):
        for user, temp in self.alive_user.items():
            # 登录用户不用接收该信息
            if user == username:
                continue
            response_msg = '(' + res[1] + ')' + res[3] + " 已上线!\n"
            temp['socket'].send(response_msg.encode('utf-8'))

    # 客户端下线（从在线用户列表删除）
    def remove_user(self, client):
        response_msg = ''
        for user, temp in self.alive_user.items():
            if temp['socket'] == client:
                username = user
                nickname = temp['nickname']
                del self.alive_user[user]
                response_msg = '(' + username + ')' + nickname + ' 已下线!\n'
                break
        print('(' + username + ')' + nickname + ' 已下线!')
        for user, temp in self.alive_user.items():
            temp['socket'].send(response_msg.encode('utf-8'))





server = Server()
