#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
import sys, os

Report_T = """\
城市: {city}
日期: {date}

早上 {morning_tempC} 度, {morning_Desc}.
中午 {noon_tempC} 度, {noon_Desc}.
晚上 {afternoon_tempC} 度, {afternoon_Desc}.\
"""

def getWeather(city):
    # city = "dalian"
    # city_CN = "大连"
    base_url = "http://api.worldweatheronline.com/free/v2/weather.ashx"
    params = "?key=55f1fdd05fba23be0a18043d0a017&num_of_days=3&format=json&lang=zh&q={0}".format(city)

    resp = urllib.urlopen(base_url + params)
    dikt = json.loads(resp.read())

    date = dikt['data']['weather'][0]['date']
    morning =  dikt['data']['weather'][0]['hourly'][2]
    noon = dikt['data']['weather'][0]['hourly'][4]
    afternoon = dikt['data']['weather'][0]['hourly'][6]

    morning_tempC, morning_Desc = morning['tempC'], morning['lang_zh'][0]['value'].encode("utf-8")
    noon_tempC, noon_Desc = noon['tempC'], noon['lang_zh'][0]['value'].encode("utf-8")
    afternoon_tempC, afternoon_Desc = afternoon['tempC'], afternoon['lang_zh'][0]['value'].encode("utf-8")

    today = Report_T.format(
        city = city,
        date = date,
        morning_tempC = morning_tempC,
        morning_Desc = morning_Desc,
        noon_tempC = noon_tempC,
        noon_Desc = noon_Desc,
        afternoon_tempC = afternoon_tempC,
        afternoon_Desc = afternoon_Desc,
    )

    return today


