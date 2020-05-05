#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Update AccessToken.
"""

import urllib.request, urllib.parse, urllib.error
import json
import sys, os
from MmrzLog import log

curPath = os.path.abspath(os.path.dirname(sys.argv[0]))
tokenFile = "{0}/AccessToken".format(curPath)

sAppId = "wx1c77202393c1c41d"
secret = "3AhT8A1akqYHKVuLCtrcx3OvZPFHbMO03vvBaGu4xyciG8Lj6z1OGs8Zp-81ZtnE"

def updateAccessToken():
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(sAppId, secret)

    web = urllib.request.urlopen(url)
    ret = json.loads(web.read())
    access_token = ret["access_token"]

    # write token to local file
    log.d("current execute path: " + str(os.getcwd()))
    fw = open(tokenFile, "w")
    fw.write(access_token)
    fw.close()

    return access_token

if __name__ == '__main__':
    updateAccessToken();



