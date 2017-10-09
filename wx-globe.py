#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tornado
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

# Flask
from flask import Flask
app = Flask(__name__)

# WX-Globe
from cgi import parse_qs, escape
from encrypt.WXBizMsgCrypt import WXBizMsgCrypt
from pypinyin import pinyin, lazy_pinyin
from tools.getCommit import getCommit
from tools.getWeather import getWeather

import xml.etree.cElementTree as ET

import os, re, time
import urllib, urllib2
import threading
import datetime
import json
import requests

import sendMsg

# disable warnings
import warnings
warnings.filterwarnings("ignore")

sToken          = "c8tcRUW1j"
sEncodingAESKey = "e6msYFTXeev0zxFNQpNCzq91SfzcAKBBn3CGXAJgd90"
sAppId          = "wx1c77202393c1c41d"

# {0}: ToUserName
# {1}: FromUserName
# {2}: CreateTime
# {3}: Content
text_T = "\
<xml>\
<ToUserName><![CDATA[zhanglintc]]></ToUserName>\
<FromUserName><![CDATA[wx1c77202393c1c41d]]></FromUserName>\
<CreateTime>1348831860</CreateTime>\
<MsgType><![CDATA[text]]></MsgType>\
<Content><![CDATA[{0}]]></Content>\
</xml>\
"

class AsyncSend(threading.Thread):
    def __init__(self, fromuser_name):
        threading.Thread.__init__(self)
        self.fromuser_name = fromuser_name

    def run(self):
        today = str(datetime.date.today()) # something like: 2014-11-10
        sendContent = getCommit("https://github.com/zhanglintc?tab=contributions&from={0}".format(today))
        sendMsg.sendMsg(
            content = sendContent,
            touser = self.fromuser_name,
        )

class updateSend(threading.Thread):
    def __init__(self, fromuser_name):
        threading.Thread.__init__(self)
        self.fromuser_name = fromuser_name

    def run(self):
        time_s = time.time()
        os.system("cd /home/lane/Mmrz-Sync/server && git pull")
        commit, author, dttime, lginfo = getGitInfo()
        time_e = time.time()

        elapse = round(time_e - time_s, 3)
        sendContent = "Mmrz has updated at:\n{0}\nusing {1}s\nLog: {2}".format(time.ctime(), elapse, lginfo)
        sendMsg.sendMsg(
            content = sendContent,
            touser = self.fromuser_name,
        )

def getGitInfo():
    os.system("cd /home/lane/Mmrz-Sync/server && git log -n 1 > mmrz-log.tmp")
    fr = open("/home/lane/Mmrz-Sync/server/mmrz-log.tmp", "rb")
    content = fr.read()
    fr.close()
    os.system("cd /home/lane/Mmrz-Sync/server && rm mmrz-log.tmp")

    commit = re.search("commit (\w{10})", content)
    author = re.search("Author: (\w*) \<", content)
    dttime = re.search("Date: +(.*) +", content)
    lginfo = re.search("    (.*)", content)

    commit = commit.group(1) if commit else "none"
    author = author.group(1) if author else "none"
    dttime = dttime.group(1) if dttime else "none"
    lginfo = lginfo.group(1) if lginfo else "none"

    return commit, author, dttime, lginfo

def restart_Mmrz():
    os.system("cd /home/lane/Mmrz-Sync/server && python restart.py &")

def tuling(text):
    url = "http://www.tuling123.com/openapi/api?key=77aa5b955fcab122b096f2c2dd8434c8&info={0}".format(text)
    content = urllib2.urlopen(url)
    content = json.loads(content.read())

    return content["text"]

def simsimi(text):
    text = urllib.quote(text.encode("utf-8"))
    url = "http://simsimi.com/getRealtimeReq?uuid=lsUq8qBErrxTthxXH5rqbcnMLEyvkPu9uI3dDsC9lW9&lc=ch&ft=1&reqText={0}".format(text)
    content = urllib2.urlopen(url)
    content = json.loads(content.read())

    return content.get("respSentence", "尚不支持...").encode("utf-8")

host = '0.0.0.0'
port = '8000'
debug = 1

def run_tornado():
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port, address=host)
    IOLoop.instance().start()

def run_flask():
    app.run(host=host, port=port)

@app.route('/')
def index():
    return 'Hello World!'

if __name__ == '__main__':
    run_flask() if debug else run_tornado()
