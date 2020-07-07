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
# # # Base package.
from flask import Flask, request, jsonify
import logging
import time
import configparser
import requests
import json
# # # Packages.
from booster.callback_formatter import CallBackFormatter
from explorer.persfr_scraper import PersFRScraper
from explorer.persfy_scraper import PersFYScraper
from explorer.persmm_scraper import PersMMScraper
from explorer.persvj_scraper import PersVJScraper
from explorer.persnk_scraper import PersNKScraper
from explorer.perswn_scraper import PersWNScraper
from explorer.persvy_scraper import PersVYScraper
from explorer.corpsl_scraper import CorpSLScraper
from explorer.corpuo_scraper import CorpUOScraper
# # # App instances. App实例。
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# # # 日志格式化。
app.logger = logging.getLogger('flask')
app.logger.setLevel(level=logging.INFO)
app.formatter = logging.Formatter('[%(asctime)s]%(message)s')
app.handler = logging.FileHandler("auto.log")
# app.handler = logging.StreamHandler()
app.handler.setFormatter(app.formatter)
app.logger.addHandler(app.handler)


# # # 接口请求地址，http://x.x.x.x:18081/auto/sl/。
@app.route('/auto/<airline_company>/', methods=['POST'])
def auto_payment(airline_company: str = "") -> dict:
    """支付接口。
    
    Args:
        airline_company (str): 航司二字码。

    Returns:
        dict
    """
    # # # 开始计时，回调声明。
    start_time = time.time()
    call_back = CallBackFormatter()
    call_back.logger = app.logger
    return_error = call_back.format_to_sync()
    # # # 解析数据并获取日志任务号。
    try:
        get_dict = json.loads(request.get_data())
        task_id = get_dict.get('automaticGetTicketId')
        log_path = f"log/{airline_company}-{task_id}.log"
    except Exception as ex:
        msg = f"航司【{airline_company}】支付数据格式有误"
        return_error['msg'] = msg
        app.logger.info(msg)
        app.logger.info(ex)
        return jsonify(return_error)
    else:
        # # # 读取配置文件信息并配置。
        config = configparser.ConfigParser()
        config.read("config.ini", encoding="utf-8")
        # # # 读取并检查声明账户类型。
        airline_account = "" # 账户类型。
        if 'account' in config:
            account = config.options('account')
            if airline_company.lower() in account:
                airline_account = config.get('account', airline_company.lower())
        # # # 判断账户类型是否正确。
        if airline_account == "corp" or airline_account == "pers":
            pass
        else:
            msg = f"航司【{airline_company}】支付功能还未上线"
            return_error['msg'] = msg
            app.logger.info(msg)
            return jsonify(return_error)
        # # # 读取并检查转发配置类型。
        forward_address = "" # 转发地址。
        if 'forward' in config:
            forward = config.options('forward')
            if airline_company.lower() in forward:
                forward_address = config.get('forward', airline_company.lower())
        # # # 判断地址是否需要转发。
        if forward_address:
            msg = f"航司【{airline_company}】支付转发声明完成"
            app.logger.info(msg)
            try:
                request_url =  f"{forward_address}/auto/{airline_company.lower()}/"
                response = requests.post(url=request_url, json=get_dict, timeout=180)
                result_data = response.json()
                result_msg = result_data.get('msg')
            except Exception as ex:
                msg = f"航司【{airline_company}】支付转发地址超时"
                return_error['msg'] = msg
                app.logger.info(msg)
                app.logger.info(ex)
                return jsonify(return_error)
            else:
                end_time = (time.time() - start_time).__round__(2)
                msg = f"航司【{airline_company}】支付转发请求成功【{end_time}】【{task_id}】【{result_msg}】"
                app.logger.info(msg)
                return jsonify(result_data)
        else:
            msg = f"航司【{airline_company}】支付本地声明完成"
            app.logger.info(msg)
            # # # 读取并检查基础配置类型。
            retry_count = ""
            if 'retry' in config:
                retry = config.options('retry')
                if airline_company.lower() in retry:
                    retry_count = config.get('retry', airline_company.lower())
            if not retry_count:
                retry_count = "1"
            # # # 读取并检查代理配置类型。
            ip_address = "" # 代理地址。
            enable_proxy = False # 是否需要代理。
            if 'proxy' in config:
                proxy = config.options('proxy')
                if airline_company.lower() in proxy:
                    ip_address = config.get('proxy', airline_company.lower())
            if ip_address:
                enable_proxy = True
            try:
                # # # 拼接请求参数。
                process_dict = {
                    "task_id": task_id, "log_path": log_path, "source_dict": get_dict,
                    "enable_proxy": enable_proxy, "address": ip_address, "retry_count": int(retry_count)
                }
                # # # 声明航司类。
                create_var = globals()
                scraper = create_var[airline_account.capitalize() + airline_company.upper() + "Scraper"]()
                result_data = scraper.process_to_main(process_dict)
                result_msg = result_data.get('msg')
            except Exception as ex:
                msg = f"航司【{airline_company}】支付本地未知错误"
                return_error['msg'] = msg
                app.logger.info(msg)
                app.logger.info(ex)
                return jsonify(return_error)
            else:
                end_time = (time.time() - start_time).__round__(2)
                msg = f"航司【{airline_company}】支付本地请求成功【{end_time}】【{task_id}】【{result_msg}】"
                app.logger.info(msg)
                return jsonify(result_data)


# # # 接收同步地址，http://x.x.x.x:18081/proxy/sl/。
@app.route('/proxy/<airline_company>/', methods=['POST'])
def auto_forward(airline_company: str = "") -> dict:
    """同步转发地址。
    
    Args:
        airline_company (str): 航司二字码。

    Returns:
        dict
    """
    # # # 定义返回格式并解析。
    return_error = {"success": "false"}
    try:
        get_dict = eval(request.get_data())
        ip_address = get_dict['ip']
    except Exception as ex:
        msg = f"航司【{airline_company}】同步转发数据有误"
        app.logger.info(msg)
        app.logger.info(ex)
        return jsonify(return_error)
    else:
        # # # 读取配置文件信息并配置。
        config = configparser.ConfigParser()
        config.read("config.ini", encoding="utf-8")
        # # # 读取并检查转发配置类型。
        if 'forward' in config:
            forward = config.options('forward')
            if airline_company.lower() in forward:
                config['forward'][airline_company.lower()] = ip_address
                config.write(open("config.ini", "w"))
                return_error['success'] = "true"
                return jsonify(return_error)
            
        msg = f"航司【{airline_company}】同步转发配置有误"
        app.logger.info(msg)
        return jsonify(return_error)
        

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=18082)
