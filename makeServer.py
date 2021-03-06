#!/usr/bin/env python
# -*- coding: utf-8 -*-

# server.py

import threading
import time, os

# 从wsgiref模块导入:
from wsgiref.simple_server import make_server
# 导入我们自己编写的application函数:
from enterprise import application, restart_Mmrz

from updateAccessToken import updateAccessToken

class AutoUpdateAccessToken(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            updateAccessToken()
            time.sleep(7000)

def main():
    # auto update AccessToken every 7000s
    auat = AutoUpdateAccessToken()
    auat.setDaemon(True)
    auat.start()

    # always restart Mmrz at start
    restart_Mmrz()

    # 创建一个服务器，IP地址为空，端口是8000，处理函数是application:
    port  = 8000
    httpd = make_server('', port, application)
    print("Serving HTTP on port {0}...".format(port))
    # 开始监听HTTP请求:
    httpd.serve_forever()

if __name__ == '__main__':
    main()



