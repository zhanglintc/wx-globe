#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
Check https://github.com/zhanglintc and get the day's contributions
and show it directly.
"""

import os, urllib
import datetime, time
import re

def getCommit(targetURL):
    today = str(datetime.date.today()) # something like: 2014-11-10
    cur_time = (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) # 2014-11-10 15:12:40
    log_file = (datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')) + '.log' # 20141110_151240.log

    web_cotent = urllib.urlopen(targetURL) # open website
    web_cotent = urllib.urlopen(targetURL) # do it twice

    line  = True
    error = True
    count = None
    pushed_detail = ""
    fw = open(log_file, 'w')
    while line:
        # read each line while not the end
        line = web_cotent.readline()

        # write web_content to log file
        fw.write(line)

        # if 'data-count' is found, means connect is OK, set error as False
        if error and 'data-count' in line:
            error = False

        # if get web_content error, exit with code 100, so caller.py will recall this script
        if 'wrong' in line:
            if error: # really error, this make script hasn't get data-count
                fw.close()
                os.remove(log_file)
                return 100
            else: # something occurred after get data-count, doesn't matter
                break

        if line and count == None: # readline isn't None means urlopen success, initialize count as 0
            count = 0

        if '"{0}"'.format(today) in line and "data-from" not in line: # find TODAY, TODAY must surrounded with quotation marks like "2014-11-10"
            count = line.split('\"')[11] # today's commit is in 11th position

        if 'Pushed' in line:
            line = re.sub('^ *', '', line) # strip spaces in the beginning of this line
            line = re.sub('</a>', '', line) # remove </a>
            pushed_detail += ("## " + line + "\n")

        if "/pull/" in line and '"title"' in line:
            line = re.sub('</a>', '', line) # remove </a>
            line = line.split('>')[-1] # pull request detail is in last position
            pushed_detail += ("## " + "Pull request: " + line + "\n")

        if "/issues/" in line and '"title"' in line:
            mc = re.search('\>(.*?)\<', line) # issues detail is the shortest string between ">" and "<"
            line = mc.group(1) + "\n" # add a line break
            pushed_detail += ("## " + "Issue: " + line + "\n")

    fw.close()

    send_content = "{0}\nMade {1} {2}\n\n\n{3}\n#GitHub reminder#\n".format(
        cur_time,
        count,
        "contribution" if int(count) < 2 else "contributions",
        pushed_detail,
    )

    # if don't want to see log file, use the code next line
    # if want to see log file, then comment the code below
    os.remove(log_file) # remove log file any way, zhanglin 2014.11.20

    return send_content

if __name__ == '__main__':
    print(getCommit("https://github.com/zhanglintc?tab=contributions&from={0}".format(str(datetime.date.today()))) + "\n")

    try:
        raw_input()
    except:
        pass


