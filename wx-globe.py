#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tornado
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

# Flask
from flask import Flask
from flask import request
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

"""
App AgentId list:
AgentId 0: Meta-Controller
AgentId 3: 天气预报
AgentId 4: 车位信息共享平台
AgentId 5: Mmrz-Dock
"""

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

def verifyCallbackMode(query_string):
    d = parse_qs(query_string)

    wx = WXBizMsgCrypt(sToken, sEncodingAESKey, sAppId)
    ret, sReplyEchoStr = wx.VerifyURL(d["msg_signature"][0], d["timestamp"][0], d["nonce"][0], d["echostr"][0])

    return sReplyEchoStr

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
    app.run(host=host, port=port, threaded=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        query_string = request.environ.get('QUERY_STRING')
        if query_string:
            return verifyCallbackMode(query_string)
        else:
            return 'the dafault page'

    else: # request.method == 'POST'
        wx = WXBizMsgCrypt(sToken, sEncodingAESKey, sAppId)
        d = parse_qs(request.environ.get('QUERY_STRING'))
        request_body = request.input_stream.read(request.content_length)
        ret, xml_content = wx.DecryptMsg(request_body, d["msg_signature"][0], d["timestamp"][0], d["nonce"][0])
        xml_tree = ET.fromstring(xml_content)

        touser_name   = xml_tree.find("ToUserName").text
        fromuser_name = xml_tree.find("FromUserName").text
        create_time   = xml_tree.find("CreateTime").text
        msg_type      = xml_tree.find("MsgType").text
        agent_ID      = xml_tree.find("AgentID").text
        # content_text  = xml_tree.find("Content").text
        # event         = xml_tree.find("Event").text
        # event_key     = xml_tree.find("EventKey").text

        if agent_ID == "0":
            if msg_type == "event":
                event_key = xml_tree.find("EventKey").text

                if event_key == "V1001_GITHUB":
                    # ret, message = wx.EncryptMsg(text_T.format(getCommit("https://github.com/zhanglintc?period=daily")), d["nonce"][0])
                    aycs = AsyncSend(fromuser_name)
                    aycs.start()

                    # return null string
                    return ""

            else:
                content_text  = xml_tree.find("Content").text
                ret, message = wx.EncryptMsg(text_T.format(tuling(content_text)), d["nonce"][0])
                return message

        if agent_ID == "3":
            log.d("agent_ID 3 entered")
            if msg_type == "text":
                content_text  = xml_tree.find("Content").text
                pinyinList = lazy_pinyin(unicode(content_text))
                pinyin = ""
                for item in pinyinList:
                    pinyin += item

                log.d("pinyin: " + str(pinyin))
                try:
                    weather = getWeather(pinyin)
                except Exception as e:
                    log.d(e)
                    weather = "getWeather() exception occured"
                log.d("weather: " + str(weather))

                ret, message = wx.EncryptMsg(text_T.format(weather), d["nonce"][0])
                return message

            ret, message = wx.EncryptMsg(text_T.format("尚不支持..."), d["nonce"][0])
            return message

        if agent_ID == "5":
            if msg_type == "event":
                event_key = xml_tree.find("EventKey").text

                if event_key == "V1001_CURRENT":
                    commit, author, dttime, lginfo = getGitInfo()

                    ret_info = "Remote Version Info\nModified at:\n{2}\nAuthor:  {1}\nHash:  {0}\nLog:  {3}".format(commit, author, dttime, lginfo)

                    ret, message = wx.EncryptMsg(text_T.format(ret_info), d["nonce"][0])

                    return message

                if event_key == "V1001_PULL_LATEST":
                    if fromuser_name != "zhanglintc":
                        ret, message = wx.EncryptMsg(text_T.format("You are not allowed to do this"), d["nonce"][0])
                        return message

                    ups = updateSend(fromuser_name)
                    ups.start()

                    ret, message = wx.EncryptMsg(text_T.format("Updating Mmrz, please wait..."), d["nonce"][0])
                    return message

                if event_key == "V1002_RESTART":
                    if fromuser_name != "zhanglintc":
                        ret, message = wx.EncryptMsg(text_T.format("You are not allowed to do this"), d["nonce"][0])
                        return message

                    restart_Mmrz()
                    ret, message = wx.EncryptMsg(text_T.format("Server has restart at:\n" + time.ctime()), d["nonce"][0])

                    return message

                if event_key == "V1002_COPY_DB":
                    os.system("cp /home/yanbin/wx-guike_server/DBDATA/zncx.db /home/lane/ftp")

                    ret, message = wx.EncryptMsg(text_T.format('zncx.db has copied to "ftp://zhanglintc.work"'), d["nonce"][0])

                    return message

            if msg_type == "text":
                content_text  = xml_tree.find("Content").text
                ret, message = wx.EncryptMsg(text_T.format(tuling(content_text)), d["nonce"][0])

                return message

            # ret, message = wx.EncryptMsg(text_T.format("尚不支持..."), d["nonce"][0])
            # return message
            return ""

        # return a null string
        return ""

@app.route('/send')
def send():
    text = request.args.get('text', "the default message")
    sendMsg.sendMsg(content=text, touser="zhanglintc")
    return "/send function entered"

if __name__ == '__main__':
    run_flask() if debug else run_tornado()
