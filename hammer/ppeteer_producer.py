# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (c) 2018-, pyLeo Developer. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""The producer is use for produce the data."""
# # # Import current path.
import sys
sys.path.append('..')
# # # 基础包。
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import time
import logging
import requests
# # # 程序包。
from booster.basic_parser import BasicParser
from booster.date_formatter import DateFormatter
from accessor.ppeteer_crawler import PpeteerCrawler
# # # 日志格式化。
logger = logging.getLogger("flask")
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('[%(asctime)s]%(message)s')
handler = logging.FileHandler("produce.log")
# handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
# # # 声明赋值。
BP = BasicParser()
DF = DateFormatter()
PC_wn = PpeteerCrawler()
PC_mm = PpeteerCrawler()
PC_vy = PpeteerCrawler()
BP.logger = logger
DF.logger = logger
PC_wn.logger = logger
PC_mm.logger = logger
PC_vy.logger = logger
# # # 数据库。
engine = create_engine('mysql://root:@127.0.0.1:3306/produce')
DBSession = sessionmaker(bind=engine)
session = DBSession()
Model = declarative_base()
headers = None


class ProduceMM(Model):
    """MM造值表,abck
    """
    __tablename__ = "produce_mm"
    id = Column(Integer, primary_key=True)
    create_time = Column(Integer)
    update_time = Column(Integer)
    produce_value = Column(Text)
    
    def __init__(self, create_time, update_time, produce_value):
        self.create_time = create_time
        self.update_time = update_time
        self.produce_value = produce_value


class ProduceVY(Model):
    """VY造值表,abck
    """
    __tablename__ = "produce_vy"
    id = Column(Integer, primary_key=True)
    create_time = Column(Integer)
    update_time = Column(Integer)
    produce_value = Column(Text)
    
    def __init__(self, create_time, update_time, produce_value):
        self.create_time = create_time
        self.update_time = update_time
        self.produce_value = produce_value


class ProduceWN(Model):
    """WN造值表,header
    """
    __tablename__ = "produce_wn"
    id = Column(Integer, primary_key=True)
    create_time = Column(Integer)
    produce_value = Column(Text)
    
    def __init__(self, create_time, produce_value):
        self.create_time = create_time
        self.produce_value = produce_value


async def produce_mm():
    """mm刷abck

    Returns:
        None
    """
    await PC_mm.set_to_chrome(True)
    PC_mm.set_to_timeout(120)
    await PC_mm.set_to_delete()
    await PC_mm.set_to_intercept(True)
    PC_mm.page.on('request', intercept_img)
    await PC_mm.set_to_url('https://booking.flypeach.com/cn')
    await asyncio.sleep(10)
    cookies = await PC_mm.get_to_cookies()
    for i in cookies:
        name = i.get("name")
        value = i.get("value")
        if name == "_abck" and "~0~" in value and "~-1~-1~-1" in value:
        # if name == "_abck" and "~-1~-1~-1" in value:
            t = int(time.time())
            try:
                insert = ProduceMM(t, t, value)
                session.add(insert)
                session.commit()
            except Exception as ex:
                logger.info(f"mm刷值写入数据库错误{ex}")
            else:
                logger.info(f"mm刷值写入数据库成功")
            session.close()
            break
            
    await PC_mm.set_to_quit()

async def produce_vy():
    """vy刷abck
    
    Returns:
        None
    """
    await PC_vy.set_to_chrome(True)
    PC_vy.set_to_timeout(120)
    await PC_vy.set_to_delete()
    await PC_vy.set_to_intercept(True)
    PC_vy.page.on('request', intercept_img)
    await PC_vy.set_to_url("https://tickets.vueling.com/?culture=en-GB&AspxAutoDetectCookieSupport=1")
    await asyncio.sleep(10)
    cookies = await PC_vy.get_to_cookies()
    for i in cookies:
        name = i.get("name")
        value = i.get("value")
        if name == "_abck" and "~-1~-1~-1" in value:
            t = int(time.time())
            try:
                insert = ProduceVY(t, t, value)
                session.add(insert)
                session.commit()
            except Exception as ex:
                logger.info(f"vy刷值写入数据库错误{ex}")
            else:
                logger.info(f"vy刷值写入数据库成功")
            session.close()
            break

    await PC_mm.set_to_quit()

async def produce_wn():
    """wn刷header
    
    Returns:
        None
    """
    global headers
    headers = None
    await PC_wn.set_to_chrome(False)
    PC_wn.set_to_timeout(120)
    await PC_wn.set_to_delete()
    await PC_wn.set_to_intercept(True)
    PC_wn.page.on('request', intercept_request)
    future = DF.format_to_now(custom_days=7)
    future = future.strftime("%Y-%m-%d")
    
    # await PC_wn.set_to_url('https://www.southwest.com/')
    # await asyncio.sleep(20)
    # if await PC_wn.page.querySelector("#LandingAirBookingSearchForm_originationAirportCode"):
    #     await PC_wn.set_to_text("#LandingAirBookingSearchForm_originationAirportCode", "DEN")
    #     await PC_wn.set_to_enter()
    #     await asyncio.sleep(2)
    #     await PC_wn.set_to_text("#LandingAirBookingSearchForm_destinationAirportCode", "LAX")
    #     await PC_wn.set_to_enter()
    #     await asyncio.sleep(2)
    #     await PC_wn.set_to_click('input[name=tripType][value=oneway]')
    #     await asyncio.sleep(2)
    #     await PC_wn.set_to_click('#LandingAirBookingSearchForm_submit-button')
    #     await asyncio.sleep(20)
    #     if await PC_wn.page.querySelector(".search-results--container"):
    
    await PC_wn.set_to_url('https://www.southwest.com/air/booking/index.html')
    time.sleep(20)
    if await PC_wn.page.querySelector("#originationAirportCode"):
        await PC_wn.set_to_text("#originationAirportCode", "DEN")
        await PC_wn.set_to_enter()
        await asyncio.sleep(2)
        await PC_wn.set_to_text("#destinationAirportCode", "LAX")
        await PC_wn.set_to_enter()
        await asyncio.sleep(2)
        await PC_wn.set_to_click('input[name=tripType][value=oneway]')
        await asyncio.sleep(2)
        await PC_wn.set_to_click('#form-mixin--submit-button')
        await asyncio.sleep(20)
        if await PC_wn.page.querySelector(".search-results--container"):
            t = int(time.time())
            try:
                print(headers)
                insert = ProduceWN(t, headers)
                session.add(insert)
                session.commit()
            except Exception as ex:
                logger.info(f"wn刷值写入数据库错误{ex}")
            else:
                logger.info(f"wn刷值写入数据库成功")
            session.close()
        else:
            logger.info("wn刷值没找到确认元素，可能是假header")

    await PC_wn.set_to_quit()
    
async def intercept_img(request):
    """请求过滤"""
    if request.resourceType in ['image', 'media', 'eventsource', 'websocket']:
        await request.abort()
    else:
        await request.continue_()
        
async def intercept_request(request):
    """请求过滤"""
    if request.resourceType in ['image', 'media', 'eventsource', 'websocket']:
        await request.abort()
    else:
        if "/booking/shopping" in request.url:
            # resp = await request.text()
            # resp = request.respond
            global headers
            headers = request.headers
        await request.continue_()

async def intercept_response(response):
    """响应过滤"""
    resourceType = response.request.resourceType
    if resourceType in ['xhr', 'fetch']:
        # resp = await response.text()
        resp = response.url
        print(resp)

def service_check():
    """

    Returns:

    """
    try:
        response = requests.post("http://192.168.0.31:8191/ServiceResponse", data={"ServiceId": 44}, timeout=5)
        logger.info(response.text)
    except Exception as ex:
        logger.info(f"生产服务请求失败{ex}")


scheduler = AsyncIOScheduler()
# scheduler.add_job(
#     func=service_check, trigger='interval', minutes=55, next_run_time=datetime.now())
# scheduler.add_job(
#     func=produce_mm, trigger='interval', minutes=5, next_run_time=datetime.now())
scheduler.add_job(
    func=produce_wn, trigger='interval', hours=8, next_run_time=datetime.now())
# scheduler.add_job(func=produce_vy, trigger='interval', seconds=300, next_run_time=datetime.now())
scheduler.start()
asyncio.get_event_loop().run_forever()

