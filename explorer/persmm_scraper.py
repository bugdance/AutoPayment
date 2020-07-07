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
"""The scraper is use for website process interaction."""
from accessor.request_worker import RequestWorker
from accessor.request_crawler import RequestCrawler
from booster.aes_formatter import AESFormatter
from booster.basic_formatter import BasicFormatter
from booster.basic_parser import BasicParser
from booster.callback_formatter import CallBackFormatter
from booster.callin_parser import CallInParser
from booster.date_formatter import DateFormatter
from booster.dom_parser import DomParser
from collector.persmm_mirror import PersMMMirror


class PersMMScraper(RequestWorker):
    """MM采集器，MM网站流程交互，5分钟刷abck，10分钟封禁解禁。"""
    
    def __init__(self) -> None:
        RequestWorker.__init__(self)
        self.RCR = RequestCrawler()  # 请求爬行器。
        self.AFR = AESFormatter()  # AES格式器。
        self.BFR = BasicFormatter()  # 基础格式器。
        self.BPR = BasicParser()  # 基础解析器。
        self.CFR = CallBackFormatter()  # 回调格式器。
        self.CPR = CallInParser(False)  # 接入解析器。
        self.DFR = DateFormatter()  # 日期格式器。
        self.DPR = DomParser()  # 文档解析器。
        self.PMR = PersMMMirror()  # MM镜像器。
        # # # 过程中重要的参数。
        self.redirect_url: str = ""  # 支付链接。
        # # # 返回中用到的变量。
        self.total_price: float = 0.0  # 总价。
        self.return_price: float = 0.0  # 返回价格。
        self.baggage_price: float = 0.0  # 行李总价。
        self.record: str = ""  # 票号。
    
    def init_to_assignment(self) -> bool:
        """Assignment to logger. 赋值日志。

        Returns:
        	bool
        """
        self.RCR.logger = self.logger
        self.AFR.logger = self.logger
        self.BFR.logger = self.logger
        self.BPR.logger = self.logger
        self.CFR.logger = self.logger
        self.CPR.logger = self.logger
        self.DFR.logger = self.logger
        self.DPR.logger = self.logger
        self.PMR.logger = self.logger
        return True
    
    def process_to_main(self, process_dict: dict = None) -> dict:
        """Main process. 主程序入口。

        Args:
            process_dict (dict): Parameters. 传参。

        Returns:
            dict
        """
        task_id = process_dict.get("task_id")
        log_path = process_dict.get("log_path")
        source_dict = process_dict.get("source_dict")
        enable_proxy = process_dict.get("enable_proxy")
        address = process_dict.get("address")
        self.retry_count = process_dict.get("retry_count")
        if not self.retry_count:
            self.retry_count = 1
        # # # 初始化日志。
        self.init_to_logger(task_id, log_path)
        self.init_to_assignment()
        # # # 同步返回参数。
        self.callback_data = self.CFR.format_to_sync()
        # # # 解析接口参数。
        if not self.CPR.parse_to_interface(source_dict):
            self.callback_data['msg'] = "请通知技术检查接口数据参数。"
            return self.callback_data
        self.logger.info(source_dict)
        # # # 启动爬虫，建立header。
        self.RCR.set_to_session()
        self.RCR.set_to_proxy(enable_proxy, address)
        self.user_agent, self.init_header = self.RCR.build_to_header("none")
        # # # 主体流程。
        if self.process_to_query(max_count=self.retry_count):
            if self.process_to_passenger(max_count=self.retry_count):
                if self.process_to_service(max_count=self.retry_count):
                    if self.process_to_payment(max_count=self.retry_count):
                        if self.process_to_record(max_count=self.retry_count):
                            self.process_to_return()
                            self.logger.removeHandler(self.handler)
                            return self.callback_data
        # # # 错误返回。
        self.callback_data['msg'] = self.callback_msg
        # self.callback_data['msg'] = "解决问题中，请手工支付。"
        self.logger.info(self.callback_data)
        self.logger.removeHandler(self.handler)
        return self.callback_data
    
    def process_to_query(self, count: int = 0, max_count: int = 1) -> bool:
        """Query process. 查询过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 更新超时时间。
            self.RCR.timeout = 10
            # # # 请求接口服务。
            self.RCR.url = "http://45.81.129.1:33334/produce/mm/"
            self.RCR.param_data = None
            self.RCR.header = None
            self.RCR.post_data = {"mm": "abck"}
            if not self.RCR.request_to_post("json", "json"):
                self.logger.info(f"请求刷值地址失败(*>﹏<*)【45.81.129.1:33334】")
                self.callback_msg = "请求刷值地址失败，请通知技术检查程序。"
                return self.process_to_query(count + 1, max_count)
            # # # 获取abck。
            cookie = self.RCR.page_source.get("value")
            if not cookie:
                self.logger.info(f"刷值数量不够用(*>﹏<*)【45.81.129.1:33334】")
                self.callback_msg = "刷值数量不够用，请通知技术检查程序。"
                return self.process_to_query(count + 1, max_count)
            # # # 设置cookie。
            history = f'{{"0":{{"departureAirportCode":"{self.CPR.departure_code}",' \
                f'"arrivalAirportCode":"{self.CPR.arrival_code}","adultCount":{self.CPR.adult_num},' \
                f'"childCount":{self.CPR.child_num},"infantCount":{self.CPR.infant_num},"isReturn":false}}}}'
            history = self.BPR.parse_to_quote(history)
            cookies = [
                {"domain": "booking.flypeach.com", "name": "flight_history", "path": "/", "value": history},
                {"domain": "flypeach.com", "name": "_abck", "path": "/", "value": cookie},
                {"domain": "booking.flypeach.com", "name": "displayed_appeal_modal", "path": "/", "value": "true"}
            ]
            self.RCR.set_to_cookies(True, cookies)
            # # # 更新超时时间。
            self.RCR.timeout = 40
            # # # 生成header, 获取首页。
            self.RCR.url = "https://booking.flypeach.com/cn"
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Host": "booking.flypeach.com",
                "Upgrade-Insecure-Requests": "1"
            })
            if self.RCR.request_to_get():
                # # # 转换接口日期。
                flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
                flight_date = flight_date.strftime("%Y/%m/%d")
                # # # 继承header, 点击查询航班数据。
                self.RCR.url = 'https://booking.flypeach.com/cn/search'
                self.RCR.header.update({
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://booking.flypeach.com",
                    "Referer": "https://booking.flypeach.com/cn",
                })
                # # # 基础参数。
                self.RCR.post_data = [
                    ("flight_search_parameter[0][departure_date]", flight_date),
                    ("flight_search_parameter[0][departure_airport_code]", self.CPR.departure_code),
                    ("flight_search_parameter[0][arrival_airport_code]", self.CPR.arrival_code),
                    ("flight_search_parameter[0][is_return]", "false"),
                    ("flight_search_parameter[0][return_date]", ""),
                    ("adult_count", self.CPR.adult_num), ("child_count", self.CPR.child_num),
                    ("infant_count", self.CPR.infant_num), ("special_code", ""), ("promotion_code", ""),
                ]
                if self.RCR.request_to_post(is_redirect=True):
                    print(self.RCR.page_source)
                    # # # 查询封禁信息。
                    error, temp_list = self.DPR.parse_to_attributes("text", "css", "title", self.RCR.page_source)
                    if error and "Access Denied" in error:
                        self.logger.info("abck遭到封禁，需要查看刷值服务(*>﹏<*)【query】")
                        self.callback_msg = "遭到封禁，请通知技术检查程序。"
                        return self.process_to_query(count + 1, max_count)
                    # # # 解析航班数据。
                    get_data, temp_list = self.BPR.parse_to_regex("flightResults = .*}}}]];", self.RCR.page_source)
                    get_list, temp_list = self.BPR.parse_to_regex("(\[\[{.*?);", get_data)
                    get_json = self.BPR.parse_to_list(get_list)
                    if not get_json:
                        self.logger.info(
                            f"获取不到航线数据(*>﹏<*)【{self.CPR.departure_code}】【{self.CPR.arrival_code}】")
                        self.callback_msg = "该航线航班已售完。"
                        return False
                    # # # 获取所有航班列表。
                    flight_number, flight_list = self.BPR.parse_to_path("$..flightNumber", get_json)
                    if not flight_list:
                        self.logger.info(f"匹配不到航班数据(*>﹏<*)【{self.CPR.flight_num}】")
                        self.callback_msg = "该航线航班已售完。"
                        return False
                    # # # 解析接口航班号。
                    interface_carrier = self.CPR.flight_num[:2]
                    interface_no = self.CPR.flight_num[2:]
                    interface_no = self.BFR.format_to_int(interface_no)
                    # # # 匹配接口航班。
                    is_flight = False  # 是否匹配到航班。
                    flight_id = ""  # 航班号ID。
                    fare_id = ""  # 价格ID。
                    for n, v in enumerate(flight_list):
                        # # # 解析网页航班号。
                        source_num = self.BPR.parse_to_clear(v)
                        if len(source_num) < 3:
                            continue
                        source_carrier = source_num[:2]
                        source_no = source_num[2:]
                        source_no = self.BFR.format_to_int(source_no)
                        # # # 匹配航班号。
                        if interface_carrier == source_carrier and interface_no == source_no:
                            is_flight = True
                            flight_id, temp_list = self.BPR.parse_to_path(f"$.[{n}].flightId", get_json)
                            
                            fare_list = []
                            fare_id, temp_list = self.BPR.parse_to_path(f"$.[{n}].fares.happy.fareId", get_json)
                            if fare_id:
                                fare_list.append(fare_id)
                            fare_id, temp_list = self.BPR.parse_to_path(f"$.[{n}].fares.happlus.fareId", get_json)
                            if fare_id:
                                fare_list.append(fare_id)
                            fare_id, temp_list = self.BPR.parse_to_path(f"$.[{n}].fares.prime.fareId", get_json)
                            if fare_id:
                                fare_list.append(fare_id)
                            if not fare_list:
                                self.logger.info(f"获取不到价格数据(*>﹏<*)【{self.CPR.flight_num}】")
                                self.callback_msg = f"该航班座位已售完。【{self.CPR.flight_num}】"
                                return False
                            
                            fare_id = fare_list[0]
                            break
                    # # # 没有找到航班号码。
                    if not is_flight:
                        self.logger.info(f"查找对应航班号失败(*>﹏<*)【{self.CPR.flight_num}】")
                        self.callback_msg = f"查找对应航班号失败【{self.CPR.flight_num}】，请核实。"
                        return False
                    # # # 继承header, 选完航班点击跳过查询。
                    self.RCR.url = "https://booking.flypeach.com/cn/flight_search"
                    self.RCR.header.update({
                        "Referer": "https://booking.flypeach.com/cn/flight_search",
                    })
                    # # # 基础参数。
                    self.RCR.post_data = [("flights[0][flightId]", flight_id), ("flights[0][fareId]", fare_id)]
                    if self.RCR.request_to_post(is_redirect=True):
                        # # # 查询封禁信息。
                        error, temp_list = self.DPR.parse_to_attributes("text", "css", "title", self.RCR.page_source)
                        if error and "Access Denied" in error:
                            self.logger.info("abck遭到封禁，需要查看刷值服务(*>﹏<*)【query】")
                            self.callback_msg = "遭到封禁，请通知技术检查程序。"
                            return self.process_to_query(count + 1, max_count)
                        # # # 安全通过。
                        self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                        return True
            # # # 错误重试。
            self.logger.info(f"提交查询第{count + 1}次超时(*>﹏<*)【query】")
            self.callback_msg = f"提交查询第{count + 1}次超时，请重试。"
            return self.process_to_query(count + 1, max_count)
    
    def process_to_passenger(self, count: int = 0, max_count: int = 1) -> bool:
        """Passenger process. 乘客过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 生成header, 添加乘客信息。
            self.RCR.url = "https://booking.flypeach.com/cn/profile"
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "booking.flypeach.com",
                "Origin": "https://booking.flypeach.com",
                "Referer": "https://booking.flypeach.com/cn/profile",
                "Upgrade-Insecure-Requests": "1"
            })
            # # # 联系方式中的国家随第一成人国籍走，没有就按中国。
            country = "CN"
            if self.CPR.adult_list:
                country = self.CPR.adult_list[0].get("nationality")
                if not country:
                    country = "CN"
            # # # 基础参数。
            self.RCR.post_data = [
                ("applicant[email]", self.CPR.contact_email),
                ("applicant[phone]", self.CPR.contact_mobile),
                ("applicant[purpose]", "6"), ("applicant[password]", ""),
                ("applicant[password_confirmation]", ""), ("applicant[country]", country),
                ("applicant[zip_code]", "100000"), ("applicant[state]", "Beijing"),
                ("applicant[city]", "Beijing"), ("applicant[street]", ""),
                ("applicant[is_check_include_passenger]", "true"),
                ("applicant[is_check_privacy_policy]", "false"),
                ("applicant[is_check_registration]", "false"),
            ]
            # # # 追加每个成人具体的参数。
            for n, v in enumerate(self.CPR.adult_list):
                birthday = self.DFR.format_to_transform(v.get("birthday"), "%Y%m%d")
                birthday = birthday.strftime("%Y/%m/%d")
                card_num = v.get("card_num")
                card_place = v.get('card_place')
                card_expired = v.get('card_expired')
                # # # 日本境内航线没有护照，携程默认G000000000。
                if not card_num or card_num == "G000000000":
                    card_num = ""
                    card_place = ""
                    card_expired = ""
                # # # 名字不要空格。
                last_name = v.get("last_name")
                last_name = self.BPR.parse_to_clear(last_name)
                first_name = v.get("first_name")
                first_name = self.BPR.parse_to_clear(first_name)
                adult_batch = [
                    (f"passengers[{n}][lastname]", last_name),
                    (f"passengers[{n}][firstname]", first_name),
                    (f"passengers[{n}][nationality]", v.get("nationality")),
                    (f"passengers[{n}][gender_type]", v.get("gender")),
                    (f"passengers[{n}][date_of_birth]", birthday),
                    (f"passengers[{n}][passport_number]", card_num),
                    (f"passengers[{n}][passport_issue_place]", card_place),
                    (f"passengers[{n}][passport_expiry_date]", card_expired),
                    (f"passengers[{n}][passenger_type]", "ADULT"),
                ]
                # # # 追加每个成人具体的参数。
                self.RCR.post_data.extend(adult_batch)
            # # # 追加每个儿童具体的参数。
            if self.CPR.child_num:
                for n, v in enumerate(self.CPR.child_list):
                    n += self.CPR.adult_num
                    birthday = self.DFR.format_to_transform(v.get("birthday"), "%Y%m%d")
                    birthday = birthday.strftime("%Y/%m/%d")
                    card_num = v.get("card_num")
                    card_place = v.get('card_place')
                    card_expired = v.get('card_expired')
                    # # # 日本境内航线没有护照，携程默认G000000000。
                    if not card_num or card_num == "G000000000":
                        card_num = ""
                        card_place = ""
                        card_expired = ""
                    # # # 名字不要空格。
                    last_name = v.get("last_name")
                    last_name = self.BPR.parse_to_clear(last_name)
                    first_name = v.get("first_name")
                    first_name = self.BPR.parse_to_clear(first_name)
                    child_batch = [
                        (f"passengers[{n}][lastname]", last_name),
                        (f"passengers[{n}][firstname]", first_name),
                        (f"passengers[{n}][nationality]", v.get("nationality")),
                        (f"passengers[{n}][gender_type]", v.get("gender")),
                        (f"passengers[{n}][date_of_birth]", birthday),
                        (f"passengers[{n}][passport_number]", card_num),
                        (f"passengers[{n}][passport_issue_place]", card_place),
                        (f"passengers[{n}][passport_expiry_date]", card_expired),
                        (f"passengers[{n}][passenger_type]", "CHD"),
                    ]
                    # # # 追加每个儿童具体的参数。
                    self.RCR.post_data.extend(child_batch)
            if self.RCR.request_to_post(is_redirect=True):
                # # # 安全通过。
                self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                return True
            # # # 错误重试。
            self.logger.info(f"添加乘客第{count + 1}次超时(*>﹏<*)【passenger】")
            self.callback_msg = f"添加乘客第{count + 1}次超时，请重试。"
            return self.process_to_passenger(count + 1, max_count)
    
    def process_to_service(self, count: int = 0, max_count: int = 1) -> bool:
        """Service process. 辅营过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 生成header, 添加附加页面。
            self.RCR.url = "https://booking.flypeach.com/cn/seats"
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "booking.flypeach.com",
                "Origin": "https://booking.flypeach.com",
                "Referer": "https://booking.flypeach.com/cn/seats",
                "Upgrade-Insecure-Requests": "1"
            })
            seats = []  # 座位信息。
            baggages = []   # 行李信息。
            # # # 追加每个成人具体的参数。
            for n, v in enumerate(self.CPR.adult_list):
                # # # 判断行李并累计公斤数。
                weight = v.get('baggage')
                kilogram = 0
                if weight:
                    for w in weight:
                        kilogram += self.BFR.format_to_int(w.get('weight'))
                # # # 解析行李参数，只有件数，没有公斤数，1件按20算。
                if kilogram:
                    if not kilogram % 20:
                        weight = self.BFR.format_to_int(kilogram / 20)
                        if weight > 5:
                            self.logger.info(f"行李超过5件(*>﹏<*)【{n}】【{v}】")
                            self.callback_msg = "行李超过5件"
                            return False
                    else:
                        self.logger.info(f"公斤数不是20的倍数(*>﹏<*)【{n}】【{v}】")
                        self.callback_msg = "匹配行李失败"
                        return False
                else:
                    weight = ""
                # # # 追加每个成人具体的参数。
                seats.append((f"seats[0][{n}]", ""))
                baggages.append((f"baggages[0][{n}]", weight))
            # # # 追加每个儿童具体的参数。
            if self.CPR.child_num:
                for n, v in enumerate(self.CPR.child_list):
                    n += self.CPR.adult_num
                    # # # 判断行李并累计公斤数。
                    weight = v.get('baggage')
                    kilogram = 0
                    if weight:
                        for w in weight:
                            kilogram += self.BFR.format_to_int(w.get('weight'))
                    # # # 解析行李参数，只有件数，没有公斤数，1件按20算。
                    if kilogram:
                        if not kilogram % 20:
                            weight = self.BFR.format_to_int(kilogram / 20)
                            if weight > 5:
                                self.logger.info(f"行李超过5件(*>﹏<*)【{n}】【{v}】")
                                self.callback_msg = "行李超过5件"
                                return False
                        else:
                            self.logger.info(f"公斤数不是20的倍数(*>﹏<*)【{n}】【{v}】")
                            self.callback_msg = "匹配行李失败"
                            return False
                    else:
                        weight = ""
                    # # # 追加每个儿童具体的参数。
                    seats.append((f"seats[0][{n}]", ""))
                    baggages.append((f"baggages[0][{n}]", weight))
            # # # 生成请求参数。
            seats.extend(baggages)
            self.RCR.post_data = seats
            if self.RCR.request_to_post(is_redirect=True):
                # # # 继承header, 添加支付卡信息页面。
                self.RCR.url = "https://booking.flypeach.com/cn/services"
                self.RCR.header.update({
                    "Referer": "https://booking.flypeach.com/cn/services",
                })
                # # # 基础参数。
                self.RCR.post_data = [
                    ("ticket_guard", ""), ("insurance_sonpo_domestic", ""), ("insurance_sonpo_international", ""),
                    ("insurance_ace", ""), ("insurance_agreement", ""), ("applicant[street]", ""),
                    ("mail_template", "1"), ("issue_honto_coupon", ""),
                ]
                if self.RCR.request_to_post(is_redirect=True):
                    # # # 获取最终总价格。
                    get_data, temp_list = self.BPR.parse_to_regex(
                        "\('initFinalPayment'.*?\);", self.RCR.page_source)
                    get_dict, temp_list = self.BPR.parse_to_regex("{.*}", get_data)
                    get_dict = self.BPR.parse_to_dict(get_dict)
                    if not get_dict:
                        self.logger.info(f"支付页面获取价格失败(*>﹏<*)【service】")
                        self.callback_msg = "支付页面获取价格失败"
                        return False
                    self.CPR.currency, temp_list = self.BPR.parse_to_path(
                        "$.basicInfos.mainCurrencyCode", get_dict)
                    self.total_price, temp_list = self.BPR.parse_to_path(
                        "$.paymentDetails.totalWithCreditCard", get_dict)
                    self.total_price = self.BFR.format_to_float(2, self.total_price)
                    # # # 解析行李价格，按人头和件数分价格。
                    single_baggage, temp_list = self.BPR.parse_to_path(
                        "$.feeDetails[0].baggages[0].basePrice", get_dict)
                    if single_baggage:
                        single_baggage = self.BFR.format_to_float(2, single_baggage)
                        one_baggage = single_baggage / 20
                        one_baggage = self.BFR.format_to_float(2, one_baggage)
                        # # # 追加每个成人具体的参数。
                        for n, v in enumerate(self.CPR.adult_list):
                            weight = v.get('baggage')
                            if weight:
                                for w in weight:
                                    kilogram = self.BFR.format_to_int(w.get('weight'))
                                    price = one_baggage * kilogram
                                    price = self.BFR.format_to_float(2, price)
                                    w['price'] = price
                                    self.CPR.return_baggage.append(w)
                                    self.baggage_price += price
                        # # # 追加每个儿童具体的参数。
                        if self.CPR.child_num:
                            for n, v in enumerate(self.CPR.child_list):
                                weight = v.get('baggage')
                                if weight:
                                    for w in weight:
                                        kilogram = self.BFR.format_to_int(w.get('weight'))
                                        price = one_baggage * kilogram
                                        price = self.BFR.format_to_float(2, price)
                                        w['price'] = price
                                        self.CPR.return_baggage.append(w)
                                        self.baggage_price += price
                    # # # 计算最终返回价格，不含行李价格。
                    if self.baggage_price:
                        self.baggage_price = self.BFR.format_to_float(2, self.baggage_price)
                        self.return_price = self.total_price - self.baggage_price
                        self.return_price = self.BFR.format_to_float(2, self.return_price)
                    else:
                        self.return_price = self.total_price
                    # # # 安全通过。
                    self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                    # # # 比价格是否要继续支付。
                    if self.process_to_compare():
                        return True
                    else:
                        return False
            # # # 错误重试。
            self.logger.info(f"服务第{count + 1}次超时或者错误(*>﹏<*)【service】")
            self.callback_msg = f"请求服务第{count + 1}次超时"
            return self.process_to_service(count + 1, max_count)
    
    def process_to_compare(self, count: int = 0, max_count: int = 1) -> bool:
        """Compare process. 对比过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        # # # 生成header, 查询货币汇率。
        self.RCR.url = f"http://flight.yeebooking.com/yfa/tool/interface/convert_conversion_result?" \
                       f"foreignCurrency={self.CPR.currency}&carrier=MM"
        self.RCR.param_data = None
        self.RCR.header = self.BFR.format_to_same(self.init_header)
        self.RCR.post_data = None
        if self.RCR.request_to_get("json"):
            # # # 解析汇率转换人民币价格。
            exchange = self.RCR.page_source.get(self.CPR.currency)
            if not exchange:
                self.logger.info(f"转换汇率价格失败(*>﹏<*)【{self.RCR.page_source}】")
                self.callback_msg = "转换汇率价格失败，请通知技术检查程序。"
                return False
            exchange_price = self.BFR.format_to_float(2, self.total_price * exchange)
            # # # 进行接口比价。
            target_price = self.BFR.format_to_float(2, self.CPR.target_price)
            diff_price = self.BFR.format_to_float(2, self.CPR.diff_price)
            target_total = self.BFR.format_to_float(2, target_price + diff_price)
            if exchange_price > target_total:
                self.logger.info(f"出票价格过高(*>﹏<*)【{target_total}】【{exchange_price}】")
                self.callback_msg = f"出票价格上限为{target_total}元。出票失败，出票价格过高，{exchange_price}元。"
                return False
            
            return True
        # # # 错误重试。
        self.logger.info(f"查询汇率接口第{count + 1}次超时(*>﹏<*)【compare】")
        self.callback_msg = f"查询汇率接口第{count + 1}次超时，请重试。"
        return self.process_to_compare(count + 1, max_count)
    
    def process_to_payment(self, count: int = 0, max_count: int = 1) -> bool:
        """Payment process. 支付过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 获取支付需要的参数。
            merchant_id, temp_list = self.BPR.parse_to_regex('{"merchantId":"(.*?)"', self.RCR.copy_source)
            init_token, temp_list = self.BPR.parse_to_regex("""'initToken', "(.*?)\"""", self.RCR.copy_source)
            content_session, temp_list = self.DPR.parse_to_attributes(
                "text", "css", "small.content-session", self.RCR.copy_source)
            if not merchant_id or not init_token or not content_session:
                self.logger.info("初始化支付参数失败(*>﹏<*)【payment】")
                self.callback_msg = "初始化支付参数失败，请通知技术检查程序。"
                return False
            # # # 生成卡信息并判断，卡号不能小于7位。
            if not self.CPR.card_num or len(self.CPR.card_num) < 7:
                self.logger.info("支付卡号小于七位(*>﹏<*)【payment】")
                self.callback_msg = "初始化支付卡号失败，请检查支付卡信息是否准确。"
                return False
            card_four = self.CPR.card_num[-4:]
            card_six = self.CPR.card_num[:6]
            card_name = f"{self.CPR.card_last} {self.CPR.card_first}"
            card_year = self.CPR.card_date[:2]
            card_month = self.CPR.card_date[2:]
            card_code = self.AFR.decrypt_into_aes(
                self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.card_code)
            if not card_code:
                self.logger.info(f"解密支付卡失败(*>﹏<*)【{self.CPR.card_code}】")
                self.callback_msg = "解密支付卡失败，请通知技术检查程序。"
                return False
            # # # 生成header，开始预支付。
            self.RCR.url = f"https://api.openpay.mx/v1/{merchant_id}/tokens"
            self.RCR.param_data = None
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Host": "api.openpay.mx",
                "Origin": "https://booking.flypeach.com",
                "Referer": "https://booking.flypeach.com/cn/pay",
                "Authorization": "Basic cGtfOGFhYWYxNWE2ODMxNDM4Y2ExZTNjYTE2MjIzYjQ2YmI6"
            })
            # # # 基础参数。
            self.RCR.post_data = {
                "card_number": self.CPR.card_num, "holder_name": card_name,
                "expiration_year": card_year, "expiration_month": card_month, "cvv2": card_code
            }
            if self.RCR.request_to_post("json", "json", 201):
                # # # 查询错误信息。
                error = self.RCR.page_source.get('description')
                if error:
                    self.logger.info(f"请求支付失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"请求支付失败【{error}】。"
                    return False
                # # # 获取支付需要的参数。
                token_id = self.RCR.page_source.get('id')
                card_type = self.RCR.page_source.get("card", {}).get("brand")
                if not token_id and not card_type:
                    self.logger.info("初始化支付参数失败(*>﹏<*)【payment】")
                    self.callback_msg = "初始化支付参数失败，请通知技术检查程序。"
                    return False
                # # # 生成header，开始预支付。
                self.RCR.url = "https://booking.flypeach.com/cn/pay/preapply"
                self.RCR.param_data = None
                self.RCR.header = self.BFR.format_to_same(self.init_header)
                self.RCR.header.update({
                    "Accept": "*/*",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Host": "booking.flypeach.com",
                    "Origin": "https://booking.flypeach.com",
                    "Referer": "https://booking.flypeach.com/cn/pay",
                    "X-Requested-With": "XMLHttpRequest"
                })
                # # # 基础参数。
                self.RCR.post_data = [
                    ("payment_method", "creditCard"), ("credit_card_type", card_type), ("4dg", card_four),
                    ("credit_card_number_4dg", card_four), ("credit_card_number_6dg", card_six),
                    ("credit_card_name", card_name), ("credit_card_expiry_date", f"{card_month}{card_year}"),
                    ("openpay_token_id", token_id), ("token", init_token),
                    ("is_agree", "true"), ("is_confirm", "true"), ("is_subscribe", "true"),
                ]
                if self.RCR.request_to_post("data", "json"):
                    # # # 生成header，开始预支付。
                    self.RCR.url = "https://booking.flypeach.com/cn/pay"
                    self.RCR.param_data = (("session", content_session),)
                    self.RCR.header = self.BFR.format_to_same(self.init_header)
                    self.RCR.header.update({
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Host": "booking.flypeach.com",
                        "Origin": "https://booking.flypeach.com",
                        "Referer": "https://booking.flypeach.com/cn/pay",
                        "Upgrade-Insecure-Requests": "1"
                    })
                    self.RCR.post_data = None
                    if self.RCR.request_to_post(status_code=302):
                        # # # 查询支付链接地址。
                        self.redirect_url, temp_list = self.DPR.parse_to_attributes(
                            "href", "css", "a[href]", self.RCR.page_source)
                        if not self.redirect_url:
                            self.logger.info("支付链接第一次获取失败(*>﹏<*)【payment】")
                            self.callback_msg = "支付链接第一次获取失败，请通知技术检查程序。"
                            return False
                        # # # 安全通过。
                        self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                        return True
            # # # 错误重试。
            self.logger.info(f"请求支付第{count + 1}次超时(*>﹏<*)【payment】")
            self.callback_msg = f"请求支付第{count + 1}次超时，请重试。"
            return self.process_to_payment(count + 1, max_count)
    
    def process_to_record(self, count: int = 0, max_count: int = 1) -> bool:
        """Record process. 订单过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 生成header，开始支付。
            # # # https://api.openpay.mx/v1/mzfg6ake9jzqdn9arzxh/charges/trq5yporoko8ziowkic2/redirect/
            self.RCR.url = self.redirect_url
            self.RCR.param_data = None
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Host": "api.openpay.mx",
                "Referer": "https://booking.flypeach.com/cn/pay",
                "Upgrade-Insecure-Requests": "1"
            })
            self.RCR.post_data = None
            if self.RCR.request_to_get():
                # # # 匹配下一次请求地址和参数。
                request_url, temp_list = self.DPR.parse_to_attributes(
                    "action", "css", "form#RedirectForm", self.RCR.page_source)
                referer_url = request_url
                option_post = []
                option, option_list = self.DPR.parse_to_attributes(
                    "name", "css", "form#RedirectForm input[type=hidden]", self.RCR.page_source)
                for i in option_list:
                    option, temp_list = self.DPR.parse_to_attributes(
                        "value", "css", f"form#RedirectForm input[name={i}]", self.RCR.page_source)
                    option_post.append((f"{i}", option))
                # # # 生成header，开始支付。
                # # # https://service3.smartcapsule.jp/disp/ONECLICKCOMM.do
                self.RCR.url = request_url
                self.RCR.param_data = None
                self.RCR.header = self.BFR.format_to_same(self.init_header)
                self.RCR.header.update({
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Host": "service3.smartcapsule.jp",
                    "Origin": "https://api.openpay.mx",
                    "Referer": self.redirect_url,
                    "Upgrade-Insecure-Requests": "1"
                })
                # # # 基础参数。
                self.RCR.post_data = option_post
                if self.RCR.request_to_post():
                    # # # 匹配下一次请求地址和参数。
                    request_url, temp_list = self.DPR.parse_to_attributes(
                        "action", "css", "form", self.RCR.page_source)
                    option_post = []
                    option, option_list = self.DPR.parse_to_attributes(
                        "name", "css", "form input[type=hidden]", self.RCR.page_source)
                    for i in option_list:
                        option, temp_list = self.DPR.parse_to_attributes(
                            "value", "css", f"input[name={i}]", self.RCR.page_source)
                        option_post.append((f"{i}", option))
                    # # # 生成header，开始支付。
                    # # # https://payment2.bluegate.jp/credit-authenticate
                    self.RCR.url = request_url
                    self.RCR.param_data = None
                    self.RCR.header = self.BFR.format_to_same(self.init_header)
                    self.RCR.header.update({
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Host": "payment2.bluegate.jp",
                        "Origin": "https://service3.smartcapsule.jp",
                        "Referer": referer_url,
                        "Upgrade-Insecure-Requests": "1"
                    })
                    # # # 基础参数。
                    self.RCR.post_data = option_post
                    if self.RCR.request_to_post():
                        # # # 匹配下一次请求地址和参数。
                        referer_url = request_url
                        request_url, temp_list = self.DPR.parse_to_attributes(
                            "action", "css", "form[name=ACSforward]", self.RCR.page_source)
                        option_post = []
                        option, option_list = self.DPR.parse_to_attributes(
                            "name", "css", "form[name=ACSforward] input[type=hidden]", self.RCR.page_source)
                        for i in option_list:
                            option, temp_list = self.DPR.parse_to_attributes(
                                "value", "css", f"form[name=ACSforward] input[name={i}]", self.RCR.page_source)
                            option_post.append((f"{i}", option))
                        # # # 生成header，开始支付。
                        # # # https://secure5.arcot.com/acspage/cap?RID=78528&VAA=A
                        self.RCR.url = request_url
                        self.RCR.param_data = None
                        self.RCR.header = self.BFR.format_to_same(self.init_header)
                        self.RCR.header.update({
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Host": "secure5.arcot.com",
                            "Origin": "https://payment2.bluegate.jp",
                            "Referer": referer_url,
                            "Upgrade-Insecure-Requests": "1"
                        })
                        # # # 基础参数。
                        self.RCR.post_data = option_post
                        if self.RCR.request_to_post():
                            # # # 匹配下一次请求地址和参数。
                            referer_url = request_url
                            request_url, temp_list = self.DPR.parse_to_attributes(
                                "action", "css", "form[name=downloadForm]", self.RCR.page_source)
                            option_post = []
                            option, option_list = self.DPR.parse_to_attributes(
                                "name", "css", "form[name=downloadForm] input[type=hidden]", self.RCR.page_source)
                            for i in option_list:
                                option, temp_list = self.DPR.parse_to_attributes(
                                    "value", "css", f"form[name=downloadForm] input[name={i}]", self.RCR.page_source)
                                option_post.append((f"{i}", option))
                            # # # 生成header，开始支付。
                            # # # https://payment2.bluegate.jp/credit-3Dauth2/SVID0101/
                            self.RCR.url = request_url
                            self.RCR.param_data = None
                            self.RCR.header = self.BFR.format_to_same(self.init_header)
                            self.RCR.header.update({
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Host": "payment2.bluegate.jp",
                                "Origin": "https://secure5.arcot.com",
                                "Referer": referer_url,
                                "Upgrade-Insecure-Requests": "1"
                            })
                            # # # 基础参数。
                            self.RCR.post_data = option_post
                            if self.RCR.request_to_post():
                                # # # 匹配下一次请求地址和参数。
                                referer_url = request_url
                                request_url, temp_list = self.DPR.parse_to_attributes(
                                    "action", "css", "form[name=returnForm]", self.RCR.page_source)
                                option_post = []
                                option, option_list = self.DPR.parse_to_attributes(
                                    "name", "css", "form[name=returnForm] input[type=hidden]", self.RCR.page_source)
                                for i in option_list:
                                    option, temp_list = self.DPR.parse_to_attributes(
                                        "value", "css", f"form[name=returnForm] input[name={i}]", self.RCR.page_source)
                                    option_post.append((f"{i}", option))
                                # # # 生成header，开始支付。
                                # # # https://service3.smartcapsule.jp/disp/ETCom3DSecureAftSTAction.do;svid09
                                self.RCR.url = request_url
                                self.RCR.param_data = None
                                self.RCR.header = self.BFR.format_to_same(self.init_header)
                                self.RCR.header.update({
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Host": "service3.smartcapsule.jp",
                                    "Origin": "https://payment2.bluegate.jp",
                                    "Referer": referer_url,
                                    "Upgrade-Insecure-Requests": "1"
                                })
                                # # # 基础参数。
                                self.RCR.post_data = option_post
                                if self.RCR.request_to_post():
                                    # # # 匹配下一次请求地址和参数。
                                    referer_url = request_url
                                    request_url, temp_list = self.DPR.parse_to_attributes(
                                        "action", "css", "form", self.RCR.page_source)
                                    option_post = []
                                    option, option_list = self.DPR.parse_to_attributes(
                                        "name", "css", "form input[type=hidden]", self.RCR.page_source)
                                    for i in option_list:
                                        option, temp_list = self.DPR.parse_to_attributes(
                                            "value", "css", f"form input[name={i}]", self.RCR.page_source)
                                        option_post.append((f"{i}", option))
                                    # # # 生成header，开始获取订单号。
                                    # # # https://api.openpay.mx/v1/mzfg6ake9jzqdn9arzxh/
                                    # # #     charges/trq5yporoko8ziowkic2/redirect/ok
                                    self.RCR.url = request_url
                                    self.RCR.param_data = None
                                    self.RCR.header = self.BFR.format_to_same(self.init_header)
                                    self.RCR.header.update({
                                        "Content-Type": "application/x-www-form-urlencoded",
                                        "Host": "api.openpay.mx",
                                        "Origin": "https://service3.smartcapsule.jp",
                                        "Referer": referer_url,
                                        "Upgrade-Insecure-Requests": "1"
                                    })
                                    # # # 基础参数。
                                    self.RCR.post_data = option_post
                                    if self.RCR.request_to_post(status_code=302):
                                        # # # 查询错误信息。
                                        invalid, temp_list = self.DPR.parse_to_attributes(
                                            "text", "css", "h1", self.RCR.page_source)
                                        if "Invalid URL" in invalid:
                                            self.logger.info(f"支付失败，可能重复支付(*>﹏<*)【{invalid}】")
                                            self.callback_msg = f"支付失败，可能重复支付，请致电航司核查。【{invalid}】"
                                            self.callback_data["orderIdentification"] = 2
                                            return False
                                        # # # 匹配下一次请求地址和参数。
                                        url, temp_list = self.BPR.parse_to_regex("charges/(.*)/redirect", request_url)
                                        if not url:
                                            self.logger.info(f"支付链接第二次获取失败(*>﹏<*)【record】")
                                            self.callback_msg = f"支付链接第二次获取失败，请通知技术检查程序。"
                                            self.callback_data["orderIdentification"] = 2
                                            return False
                                        # # # 生成header，开始获取订单号。
                                        # # # https://booking.flypeach.com/cn/pay/postapply?id=trq5yporoko8ziowkic2
                                        self.RCR.url = f"https://booking.flypeach.com/cn/pay/postapply?id={url}"
                                        self.RCR.param_data = None
                                        self.RCR.header = self.BFR.format_to_same(self.init_header)
                                        self.RCR.header.update({
                                            "Host": "booking.flypeach.com",
                                            "Referer": referer_url,
                                            "Upgrade-Insecure-Requests": "1"
                                        })
                                        self.RCR.post_data = None
                                        if self.RCR.request_to_get(status_code=302):
                                            # # # 查询错误信息。
                                            error, temp_list = self.DPR.parse_to_attributes(
                                                "text", "css", ".txt-message", self.RCR.page_source)
                                            if error:
                                                self.logger.info(f"请求支付失败(*>﹏<*)【{error}】")
                                                self.callback_msg = f"请求支付失败【{error}】。"
                                                self.callback_data["orderIdentification"] = 2
                                                return False
                                            # # # 生成header，开始获取订单号。
                                            # # # https://booking.flypeach.com/cn/done
                                            self.RCR.url = "https://booking.flypeach.com/cn/done"
                                            self.RCR.param_data = None
                                            self.RCR.header = self.BFR.format_to_same(self.init_header)
                                            self.RCR.header.update({
                                                "Host": "booking.flypeach.com",
                                                "Referer": referer_url,
                                                "Upgrade-Insecure-Requests": "1"
                                            })
                                            self.RCR.post_data = None
                                            if self.RCR.request_to_get():
                                                # # # 获取PNR。
                                                self.record, temp_list = self.DPR.parse_to_attributes(
                                                    "text", "css", ".txt-number .font-big", self.RCR.page_source)
                                                self.record = self.BPR.parse_to_clear(self.record)
                                                if not self.record:
                                                    self.logger.info("获取支付编码失败(*>﹏<*)【record】")
                                                    self.callback_msg = "获取PNR失败，可能已出票，请核对。"
                                                    self.callback_data["orderIdentification"] = 2
                                                    return False
                                                
                                                return True
            # # # 错误重试。
            self.logger.info(f"获取支付编码第{count + 1}次超时(*>﹏<*)【record】")
            self.callback_msg = f"获取支付编码第{count + 1}次超时，请重试。"
            self.callback_data["orderIdentification"] = 2
            return self.process_to_record(count + 1, max_count)
    
    def process_to_return(self) -> bool:
        """Return process. 返回过程。

        Returns:
            bool
        """
        self.callback_data["success"] = "true"
        self.callback_data['msg'] = "出票成功"
        self.callback_data['totalPrice'] = self.return_price
        self.callback_data["currency"] = self.CPR.currency
        self.callback_data['pnrCode'] = self.record
        self.callback_data["orderIdentification"] = 3
        self.callback_data["baggages"] = self.CPR.return_baggage
        self.logger.info(self.callback_data)
        return True

