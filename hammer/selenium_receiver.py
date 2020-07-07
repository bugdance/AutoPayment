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
"""The receiver is use for receive the data."""
# # # Import current path.
import sys
sys.path.append('..')
# # # 基础包。
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import logging
import requests
from datetime import datetime
import time
# # # 程序包。
from booster.basic_parser import BasicParser
from booster.date_formatter import DateFormatter
from accessor.selenium_crawler import SeleniumCrawler
# # # app实例。
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# # # 数据库。
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1:3306/produce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# # # 日志格式化。
app.logger = logging.getLogger("flask")
app.logger.setLevel(level=logging.INFO)
app.formatter = logging.Formatter('[%(asctime)s]%(message)s')
app.handler = logging.FileHandler("produce.log")
# app.handler = logging.StreamHandler()
app.handler.setFormatter(app.formatter)
app.logger.addHandler(app.handler)
# # # 声明赋值。
SC_wn = SeleniumCrawler()
SC_mm = SeleniumCrawler()
# SC_vy = SeleniumCrawler()
BP = BasicParser()
DF = DateFormatter()
SC_wn.logger = app.logger
SC_mm.logger = app.logger
# SC_vy.logger = app.logger
BP.logger = app.logger
DF.logger = app.logger
SC_wn.set_to_chrome(False)
SC_wn.driver.minimize_window()
SC_mm.set_to_chrome()
# SC_vy.set_to_chrome()


class ProduceMM(db.Model):
    """MM造值表,abck
    """
    __tablename__ = "produce_mm"
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Integer)
    update_time = db.Column(db.Integer)
    produce_value = db.Column(db.Text)
    
    def __init__(self, create_time, update_time, produce_value):
        self.create_time = create_time
        self.update_time = update_time
        self.produce_value = produce_value


class ProduceVY(db.Model):
    """VY造值表,abck
    """
    __tablename__ = "produce_vy"
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Integer)
    update_time = db.Column(db.Integer)
    produce_value = db.Column(db.Text)
    
    def __init__(self, create_time, update_time, produce_value):
        self.create_time = create_time
        self.update_time = update_time
        self.produce_value = produce_value


class ProduceWN(db.Model):
    """WN造值表,header
    """
    __tablename__ = "produce_wn"
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.Integer)
    produce_value = db.Column(db.Text)
    
    def __init__(self, create_time, produce_value):
        self.create_time = create_time
        self.produce_value = produce_value


def produce_mm():
    """mm刷abck
    :return: None
    """
    SC_mm.set_to_delete()
    SC_mm.set_to_url("https://booking.flypeach.com/cn")
    time.sleep(10)
    cookies = SC_mm.get_to_cookies()
    for i in cookies:
        name = i.get("name")
        value = i.get("value")
        if name == "_abck" and "~0~" in value and "~-1~-1~-1" in value:
            t = int(time.time())
            try:
                insert = ProduceMM(t, t, value)
                db.session.add(insert)
                db.session.commit()
            except Exception as ex:
                app.logger.info(f"mm刷值写入数据库错误{ex}")
            else:
                pass
            break


# def produce_vy():
#     """vy刷abck
#     :return: None
#     """
#     SC_vy.set_to_delete()
#     SC_vy.set_to_url("https://tickets.vueling.com/?culture=en-GB&AspxAutoDetectCookieSupport=1")
#     time.sleep(10)
#     cookies = SC_vy.get_to_cookies()
#     for i in cookies:
#         name = i.get("name")
#         value = i.get("value")
#         if name == "_abck" and "~-1~-1~-1" in value:
#             t = int(time.time())
#             try:
#                 insert = ProduceVY(t, t, value)
#                 db.session.add(insert)
#                 db.session.commit()
#             except Exception as ex:
#                 app.logger.info(f"vy刷值写入数据库错误{ex}")
#             else:
#                 pass
#             break


def produce_wn():
    """
    :return:
    """
    SC_wn.set_to_delete()
    SC_wn.set_to_url("https://www.southwest.com/air/booking/?redirectToVision=true&int=&leapfrogRequest=true")
    if SC_wn.set_to_wait("#form-mixin--submit-button", 10):
        SC_wn.set_to_text("#originationAirportCode", "LAX")
        time.sleep(2)
        SC_wn.set_to_enter("#originationAirportCode")
        time.sleep(2)
        SC_wn.set_to_text("#destinationAirportCode", "SLC")
        time.sleep(2)
        SC_wn.set_to_enter("#destinationAirportCode")
        time.sleep(2)
        SC_wn.set_to_click("#form-mixin--submit-button")
    # future = DF.format_to_now(custom_days=7)
    # future = future.strftime("%Y-%m-%d")
    # SC_wn.set_to_url(
    #     f"https://www.southwest.com/air/flight-schedules/results.html?"
    #     f"departureDate={future}&destinationAirportCode=SLC&originationAirportCode=LAX"
    #     f"&scheduleViewType=daily&timeOfDay=ALL_DAY")
    time.sleep(60)
    log = SC_wn.get_to_package()
    for i in log:
        message = BP.parse_to_dict(i.get('message'))
        method, temp_list = BP.parse_to_path("$.message.method", message)
        if "requestWillBeSent" in method:
            url, temp_list = BP.parse_to_path("$.message.params.request.url", message)
            if "/flights/schedules" in url:
                header, temp_list = BP.parse_to_path("$.message.params.request.headers", message)
                if header:
                    t = int(time.time())
                    try:
                        insert = ProduceWN(t, header)
                        db.session.add(insert)
                        db.session.commit()
                    except Exception as ex:
                        app.logger.info(f"wn刷值写入数据库错误{ex}")
                    else:
                        pass
                    break


def delete_mm():
    """mm删除abck
    :return: None
    """
    try:
        now = int(time.time())
        ProduceMM.query.filter(ProduceMM.create_time < now - 604800).delete()
        db.session.commit()
    except Exception as ex:
        app.logger.info(f"mm删除数据库错误{ex}")
    else:
        pass
    
    
# def delete_vy():
#     """vy删除abck
#     :return: None
#     """
#     try:
#         now = int(time.time())
#         ProduceVY.query.filter(ProduceVY.create_time < now - 604800).delete()
#         db.session.commit()
#     except Exception as ex:
#         app.logger.info(f"vy删除数据库错误{ex}")
#     else:
#         pass

    
def delete_wn():
    """wn删除header
    :return: None
    """
    try:
        now = int(time.time())
        ProduceWN.query.filter(ProduceWN.create_time < now - 86400).delete()
        db.session.commit()
    except Exception as ex:
        app.logger.info(f"wn删除数据库错误{ex}")
    else:
        pass
    

def service_check():
    """
    
    Returns:

    """
    try:
        response = requests.post("http://192.168.0.31:8191/ServiceResponse", data={"ServiceId": 44}, timeout=5)
        app.logger.info(response.text)
    except Exception as ex:
        app.logger.info(f"生产服务请求失败{ex}")
    

scheduler = APScheduler()
scheduler.init_app(app=app)
scheduler.add_job(func=produce_mm, id='produce_mm', trigger='interval', seconds=300, next_run_time=datetime.now())
scheduler.add_job(func=produce_wn, id='produce_wn', trigger='interval', seconds=14400, next_run_time=datetime.now())
# scheduler.add_job(func=produce_vy, id='produce_vy', trigger='interval', seconds=300, next_run_time=datetime.now())

scheduler.add_job(func=delete_mm, id='delete_mm', trigger='cron', hour=0, minute=0, next_run_time=datetime.now())
scheduler.add_job(func=delete_wn, id='delete_wn', trigger='interval', seconds=21600, next_run_time=datetime.now())
# scheduler.add_job(func=delete_vy, id='delete_vy', trigger='cron', hour=0, minute=0, next_run_time=datetime.now())

scheduler.add_job(func=service_check, id='service_check', trigger='interval', seconds=3300, next_run_time=datetime.now())
scheduler.start()


# # # 链接地址,例http://x.x.x.x:33334/produce/mm/
@app.route('/produce/mm/', methods=['POST'])
def server_mm():
    """
    Returns:

    """
    get_dict = BP.parse_to_eval(request.get_data())
    if not get_dict:
        return jsonify({"value": ""})

    try:
        status = get_dict.get("mm")
        if status != "abck":
            return jsonify({"value": ""})

        now = int(time.time())
        sql = f"select id, produce_value from produce_mm where update_time < {now - 600} order by rand() limit 1;"
        result = db.session.execute(sql)
        result = list(result)
        if result:
            number = result[0][0]
            value = result[0][1]
            ProduceMM.query.filter(ProduceMM.id == number).update({'update_time': now + 180})
            db.session.commit()
            return jsonify({"value": value})
        else:
            return jsonify({"value": ""})
    except Exception as ex:
        app.logger.info(f"从数据库取mm刷值失败{ex}")
        return jsonify({"value": ""})


# # # 链接地址,例http://x.x.x.x:33334/produce/wn/
@app.route('/produce/wn/', methods=['POST'])
def server_wn():
    """
    Returns:

    """
    get_dict = BP.parse_to_eval(request.get_data())
    if not get_dict:
        return jsonify({"value": ""})

    try:
        status = get_dict.get("wn")
        if status != "header":
            return jsonify({"value": ""})

        now = int(time.time())
        sql = f"select produce_value from produce_wn where {now - 86400} < create_time < {now} order by rand() limit 1;"
        result = db.session.execute(sql)
        result = list(result)
        if result:
            value = result[0][0]
            return jsonify({"value": value})
        else:
            return jsonify({"value": ""})
    except Exception as ex:
        app.logger.info(f"从数据库取wn刷值失败{ex}")
        return jsonify({"value": ""})


# # # # 链接地址,例http://x.x.x.x:33334/produce/vy/
# @app.route('/produce/vy/', methods=['POST'])
# def server_vy() -> dict:
#     """
#
#     Returns:
#         dict
#     """
#     get_dict = BP.parse_to_eval(request.get_data())
#     if not get_dict:
#         return jsonify({"value": ""})
#
#     try:
#         status = get_dict.get("vy")
#         if status != "abck":
#             return jsonify({"value": ""})
#
#         now = int(time.time())
#         sql = f"select id, produce_value from produce_vy where update_time < {now - 600} order by rand() limit 1;"
#         result = db.session.execute(sql)
#         result = list(result)
#         if result:
#             number = result[0][0]
#             value = result[0][1]
#             ProduceVY.query.filter(ProduceVY.id == number).update({'update_time': now + 180})
#             db.session.commit()
#             return jsonify({"value": value})
#         else:
#             return jsonify({"value": ""})
#     except Exception as ex:
#         app.logger.info(f"从数据库取vy刷值失败{ex}")
#         return jsonify({"value": ""})
    

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=33334, threaded=True)
