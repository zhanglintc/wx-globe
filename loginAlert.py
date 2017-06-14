#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sendMsg
import threading
import os

def login_message():
    stdout = os.popen('whoami')
    whoami = stdout.read().strip()

    stdout = os.popen('date "+%H:%M:%S %m-%d"')
    date = stdout.read().strip()

    msg = ""
    msg += "Login Alert\n"
    msg += "User: {0}\n".format(whoami)
    msg += "Time: {0}\n".format(date)

    sendMsg.sendMsg(content=msg, touser="zhanglintc|smile")

if __name__ == '__main__':
    threading.Thread(target=login_message).start()


