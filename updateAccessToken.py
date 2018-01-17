#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Update AccessToken.
"""

import urllib
import json

tokenFile = "AccessToken"

sAppId = "wx1c77202393c1c41d"
secret = "3AhT8A1akqYHKVuLCtrcx3OvZPFHbMO03vvBaGu4xyciG8Lj6z1OGs8Zp-81ZtnE"

def updateAccessToken():
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(sAppId, secret)

    web = urllib.urlopen(url)
    ret = json.loads(web.read())
    access_token = ret["access_token"]

    # write token to local file
    import os
    log.d("current execute path: " + str(os.getcwd()))
    fw = open(tokenFile, "wb")
    fw.write(access_token)
    fw.close()

    return access_token

if __name__ == '__main__':
    updateAccessToken();

    try:
        raw_input()
    except:
        pass


