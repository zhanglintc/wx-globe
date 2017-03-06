#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, urllib2
import json
import requests

from updateAccessToken import updateAccessToken

tokenFile = "AccessToken"

def sendMsg(content = "", touser = "@all"):
    try:
        fr = open(tokenFile, "rb")
        access_token = fr.read().strip()

    except:
        access_token = updateAccessToken()
   
    params = {
        "touser" : touser,
        "toparty": "@all",
        "totag"  : "@all",
        "agentid": "5",   # str or int is OK
        "msgtype": "text",
        "text": {
            "content": content or "test message"
            },
        }
    params = json.dumps(params, ensure_ascii = False)

    resp = requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(access_token), data = params).text
    print "from sendMsg: " + resp
    resp = json.loads(resp)
    if resp["errcode"] != 0:
        print "from sendMsg: " + "Error {0}: {1}".format(resp["errcode"], resp["errmsg"])

        if resp["errcode"] == 42001 or resp["errcode"] == 40014:
            access_token = updateAccessToken()
            print "from sendMsg: " + requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(access_token), data = params).text

if __name__ == '__main__':
    sendMsg()
