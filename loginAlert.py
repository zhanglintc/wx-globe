#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sendMsg
import threading
import os, json, time

time_log_file = "login-time.json"

def login_message():
    stdout = os.popen('whoami')
    whoami = stdout.read().strip()

    stdout = os.popen('date "+%H:%M:%S %m-%d"')
    date = stdout.read().strip()

    msg = ""
    msg += "Login Notification\n"
    msg += "User: {0}\n".format(whoami)
    msg += "Time: {0}\n".format(date)

    try:
        fr = open(time_log_file, "rb")
        content = fr.read()
        jsn = json.loads(content)
        fr.close()
    except:
        jsn = {}

    log_time = jsn.get(whoami, 0)
    cur_time = time.time()

    if cur_time > log_time + 3600:
        sendMsg.sendMsg(content=msg, touser="zhanglintc|smile")

        fw = open(time_log_file, "wb")
        jsn[whoami] = cur_time
        content = json.dumps(jsn, indent=4)
        fw.write(content)
        fw.close()
    else:
        print("last notification within 1 hour")

if __name__ == '__main__':
    threading.Thread(target=login_message).start()


