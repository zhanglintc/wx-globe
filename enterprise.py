#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        time_e = time.time()

        elapse = round(time_e - time_s, 3)
        sendContent = "Mmrz has updated at:\n{0}\nusing {1}s".format(time.ctime(), elapse)
        sendMsg.sendMsg(
            content = sendContent,
            touser = self.fromuser_name,
        )

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

def restart_Mmrz():
    os.system("cd /home/lane/Mmrz-Sync/server && python restart.py &")

def setMenu():
    secret = "3AhT8A1akqYHKVuLCtrcx3OvZPFHbMO03vvBaGu4xyciG8Lj6z1OGs8Zp-81ZtnE"
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(sAppId, secret)
    access_token = ""
    if not access_token:
        web = urllib.urlopen(url)
        ret = json.loads(web.read())
        access_token = ret["access_token"]
        print access_token

    params = {
        "button":[
            {    
                "name":"小工具",
                "key":"V1001_TOOL_LITE",
                "sub_button":[
                    {
                        "type":"click",
                        "name":"GitHub报告",
                        "key":"V1001_GITHUB"
                    },
                ]
            },
            {
                "name":"关于",
                "sub_button":[
                    {
                        "type":"view",
                        "name":"打开主页",
                        "url":"http://zhanglintc.co/"
                    },
                    {
                        "type":"view",
                        "name":"打开博客",
                        "url":"http://imlane.farbox.com"
                    },
                ]
            }
        ]
    }
    params = json.dumps(params, ensure_ascii = False)
    print params

    print requests.post("https://qyapi.weixin.qq.com/cgi-bin/menu/create?access_token={0}&agentid=0".format(access_token), data = params).text

    Mmrz_Menu = {
        "button":[
            {    
                "name":"版本管理",
                "key":"V1001_VERSIOM",
                "sub_button":[
                    {
                        "type":"click",
                        "name":"当前版本",
                        "key":"V1001_CURRENT"
                    },
                    {
                        "type":"click",
                        "name":"拉取新版",
                        "key":"V1001_PULL_LATEST"
                    },
                ]
            },
            {    
                "name":"服务管理",
                "key":"V1002_SERVER",
                "sub_button":[
                    {
                        "type":"click",
                        "name":"重启服务",
                        "key":"V1002_RESTART"
                    },
                ]
            }
        ]
    }
    Mmrz_Menu = json.dumps(Mmrz_Menu, ensure_ascii = False)
    print requests.post("https://qyapi.weixin.qq.com/cgi-bin/menu/create?access_token={0}&agentid=5".format(access_token), data = Mmrz_Menu).text

def getRequestBody(environ):
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))

    except (ValueError):
        request_body_size = 0

    # When the method is POST the query string will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)

    return request_body

def verifyCallbackMode(environ):
    d = parse_qs(environ['QUERY_STRING'])

    wx = WXBizMsgCrypt(sToken, sEncodingAESKey, sAppId)
    ret, sReplyEchoStr = wx.VerifyURL(d["msg_signature"][0], d["timestamp"][0], d["nonce"][0], d["echostr"][0])

    return sReplyEchoStr

def application(environ, start_response):
    # response content
    start_response('200 OK', [('Content-Type', 'text/html')])

    wx = WXBizMsgCrypt(sToken, sEncodingAESKey, sAppId)
    d = parse_qs(environ['QUERY_STRING'])

    # always restart Mmrz at start
    restart_Mmrz()

    # set up weixin callback mode
    if "echostr" in environ['QUERY_STRING']:
        return verifyCallbackMode(environ)

    request_body = getRequestBody(environ)
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

    if environ["PATH_INFO"] == "/send":
        d = parse_qs(environ['QUERY_STRING'])
        text = d.get('text', "default message")

        sendMsg.sendMsg(content=text, touser="zhanglintc")

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
        if msg_type == "text":
            content_text  = xml_tree.find("Content").text
            pinyinList = lazy_pinyin(unicode(content_text))
            pinyin = ""
            for item in pinyinList:
                pinyin += item

            weather = getWeather(pinyin)

            ret, message = wx.EncryptMsg(text_T.format(weather), d["nonce"][0])
            return message

        ret, message = wx.EncryptMsg(text_T.format("尚不支持..."), d["nonce"][0])
        return message

    if agent_ID == "5":
        if msg_type == "event":
            event_key = xml_tree.find("EventKey").text

            if event_key == "V1001_CURRENT":
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

def main():
    # setMenu()
    pass

if __name__ == '__main__':
    main()
