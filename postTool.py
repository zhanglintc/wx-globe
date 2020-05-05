#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import json
import requests

import xml.etree.cElementTree as ET

# disable warnings
import warnings
warnings.filterwarnings("ignore")

postBody = "\
<xml><ToUserName><![CDATA[wx1c77202393c1c41d]]></ToUserName>\
<Encrypt><![CDATA[z7OQxxAfmymuaKQ6WW1cemERCXbwtrFH4lMGFVCYafg9w7886ycCYusV+mW32pXHCUHGTRsDTyWY1cfiN15h/Vj1LGu4TtDTHju/74rBbYrQQpGyTNXe8azyqaUZWr2OlszQUG9lwRHQPyy1o0YUOtteLRs10F6r/e4oqERKiYSW3kxHmeZygpFTYLTbJ2POLR/R5noD7LdkEAiLAwYdb34O/wANHHu2aCYC/PgNXIdIihvlXAT06idfxuK6d3opgYaaNbxpEd+SLR68NU+kA57/04J1f3o5PnmnnkKpsErO8imxjrOaooq2wVKgGkSLvGLa8BKr4FSzU7k/3YEM60Vip1Xl4y+pmnyCgxLHmtlCA5bKLWCAVj1GF0D2ZP5HrMpOzHD85zZ62Sqez+EbONn/tATcG2oEMs59T9VX84GOP63eZ7M+Wv2WC9ycSXQ7locQ0piE+f1vsXfSLWhUYg==]]></Encrypt>\
<AgentID><![CDATA[0]]></AgentID>\
</xml>\
"

xmlContent = "\
<xml><ToUserName><![CDATA[wx1c77202393c1c41d]]></ToUserName>\
<FromUserName><![CDATA[zhanglintc]]></FromUserName>\
<CreateTime>1448614862</CreateTime>\
<MsgType><![CDATA[event]]></MsgType>\
<AgentID>0</AgentID>\
<Event><![CDATA[click]]></Event>\
<EventKey><![CDATA[V1001_GITHUB]]></EventKey>\
</xml>\
"

addOn = "/?msg_signature=244460c2cced1a58556b18eb7af4b98d3e1bee4d&timestamp=1448544108&nonce=1336927500"
Theodolite_URL = "http://127.0.0.1:8000{0}".format(addOn)

def post():
    requests.post(Theodolite_URL, data = postBody)

def XMLParse():
    xml_tree = ET.fromstring(xmlContent)

    touser_name = xml_tree.find("ToUserName")
    fromuser_name = xml_tree.find("FromUserName")
    create_time = xml_tree.find("CreateTime")
    msg_type = xml_tree.find("MsgType")
    agent_ID = xml_tree.find("AgentID")
    event = xml_tree.find("Event")
    event_key = xml_tree.find("EventKey")

    print(touser_name.text)
    print(fromuser_name.text)
    print(create_time.text)
    print(msg_type.text)
    print(agent_ID.text)
    print(event.text)
    print(event_key.text)

if __name__ == '__main__':
    # post()
    XMLParse()
