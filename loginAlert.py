#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sendMsg
import os

stdout = os.popen('whoami')
whoami = stdout.read().strip()

stdout = os.popen('date "+%H:%M:%S"')
date = stdout.read().strip()

msg = ""
msg += "Login Alert\n"
msg += "User: {0}\n".format(whoami)
msg += "Time: {0}\n".format(date)

sendMsg.sendMsg(content=mgs, touser="zhanglintc")

