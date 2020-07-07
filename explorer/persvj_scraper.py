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
from detector.persvj_simulator import PersVJSimulator


class PersVJScraper(RequestWorker):
    """VJ采集器，VJ网站流程交互。"""
    
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
        self.PSR = PersVJSimulator()  # VJ模拟器。
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
        self.PSR.logger = self.logger
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
        # # # 启动爬虫，建立header，更新联系电话。
        self.RCR.set_to_session()
        self.RCR.set_to_proxy(enable_proxy, address)
        self.user_agent, self.init_header = self.RCR.build_to_header("none")
        self.CPR.contact_mobile = "16639167479"
        self.CPR.currency = "VND"
        # # # 主体流程。
        if self.process_to_index(max_count=self.retry_count):
            if self.process_to_verify(max_count=self.retry_count):
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

    def process_to_proxy(self, count: int = 0, max_count: int = 3) -> bool:
        """Proxy process. 代理过程。

		Args:
			count (int): 累计计数。
			max_count (int): 最大计数。

		Returns:
			bool
		"""
        if count >= max_count:
            return False
        else:
            # # # 获取代理，并配置代理。
            self.RCR.url = 'http://cloudmonitorproxy.51kongtie.com/Proxy/getProxyByServiceType?proxyNum=1&serviceType=4'
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.param_data = None
            if self.RCR.request_to_get('json'):
                ip, temp_list = self.BPR.parse_to_path("$.[0].proxyIP", self.RCR.page_source)
                port, temp_list = self.BPR.parse_to_path("$.[0].prot", self.RCR.page_source)
                if ip and port:
                    proxy = f"http://yunku:123@{ip}:{port}"
                    self.RCR.set_to_proxy(True, proxy)
                    return True
            # # # 错误重试。
            self.logger.info(f"请求代理第{count + 1}次超时(*>﹏<*)【proxy】")
            self.callback_msg = f"请求代理第{count + 1}次超时，请重试。"
            return self.process_to_proxy(count + 1, max_count)

    def process_to_index(self, count: int = 0, max_count: int = 1) -> bool:
        """Verify process. 验证过程。
        
        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 生成header, 获取首页。
            self.RCR.url = "https://www.vietjetair.com/Sites/Web/zh-CN/Home"
            self.RCR.param_data = None
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Host": "www.vietjetair.com",
                "Upgrade-Insecure-Requests": "1",
            })
            if self.RCR.request_to_get():
                # # # 转换接口参数日期。
                flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
                # # # 获取view参数个数，参数100多个。
                view_count, temp_list = self.DPR.parse_to_attributes(
                    "value", "css", "#__VIEWSTATEFIELDCOUNT", self.RCR.page_source)
                view_count = self.BFR.format_to_int(view_count)
                hidden_field, temp_list = self.BPR.parse_to_regex(
                    '_TSM_CombinedScripts_=(.*?)"', self.RCR.page_source)
                # # # 继承header, 从这一步开始点击查询。
                self.RCR.url = "https://www.vietjetair.com/Sites/Web/zh-CN/Home"
                self.RCR.header.update({
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://www.vietjetair.com",
                    "Referer": "https://www.vietjetair.com/Sites/Web/zh-CN/Home",
                })
                # # # 基础参数。
                param_batch = [
                    ("ctl00_ScriptManager1_HiddenField", False, hidden_field),
                    ("__EVENTTARGET", True, "#__EVENTTARGET"), ("__EVENTARGUMENT", True, "#__EVENTARGUMENT"),
                    ("__LASTFOCUS", True, "#__LASTFOCUS"), ("__VIEWSTATEFIELDCOUNT", True, "#__VIEWSTATEFIELDCOUNT"),
                    ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
                    ("ctl00$UcHeaderV31$DrLang", False, "zh-CN"), ("ctl00$UcHeaderV31$TxtKeyWord", False, ""),
                    ("ctl00$UcHeaderV31$tbwKeyword_ClientState", False, ""),
                    ("ctl00$UcRightV31$RoundTrip", False, "RbOneWay"), ("selectOrigin", False, self.CPR.departure_code),
                    ("selectDestination", False, self.CPR.arrival_code),
                    ("ctl00$UcRightV31$selectedValOrigin", False, self.CPR.departure_code),
                    ("ctl00$UcRightV31$selectedValDestination", False, self.CPR.arrival_code),
                    ("ctl00$UcRightV31$TxtDepartDate", False, flight_date.strftime("%d/%m/%Y")),
                    ("ctl00$UcRightV31$TxtReturnDate", False, flight_date.strftime("%d/%m/%Y")),
                    ("ctl00$UcRightV31$CbbCurrency$TextBox", False, self.CPR.currency),
                    ("ctl00$UcRightV31$CbbCurrency$HiddenField", False, "0"),
                    ("ctl00$UcRightV31$TxtPromoCode", False, ""),
                    ("ctl00$UcRightV31$tbwpPromoCode_ClientState", False, ""),
                    ("ctl00$UcRightV31$BtSearch", False, "查找航班"),
                    ("ctl00$UcRightV31$CbbAdults$TextBox", False, self.CPR.adult_num),
                    ("ctl00$UcRightV31$CbbAdults$HiddenField", False, "0"),
                    ("ctl00$UcRightV31$CbbChildren$TextBox", False, self.CPR.child_num),
                    ("ctl00$UcRightV31$CbbChildren$HiddenField", False, "0"),
                    ("ctl00$UcRightV31$CbbInfants$TextBox", False, self.CPR.infant_num),
                    ("ctl00$UcRightV31$CbbInfants$HiddenField", False, "0"),
                    ("ctl00$UcRightV31$GnRegister", False, "RbENewsRegister"),
                    ("ctl00$UcRightV31$TxtEmail", False, ""), ("ctl00$UcRightV31$TxtWeEmail_ClientState", False, ""),
                    ("ctl00$UcRightV31$TxtRegEmail", False, ""), ("ctl00$UcRightV31$TxtCaptCha", False, ""),
                ]
                # # # 追加view参数，如果是0没有数字。
                for i in range(view_count):
                    if i == 0:
                        i = ""
                    param_batch.extend([(f"__VIEWSTATE{i}", True, f"#__VIEWSTATE{i}")])
                # # # 生成请求参数。
                self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.page_source)
                if self.RCR.request_to_post():
                    # # # 继承header, 获取生成cookie需要的参数的地址。
                    self.RCR.url = "https://booking.vietjetair.com/ameliapost.aspx"
                    self.RCR.param_data = (("lang", "zh"), )
                    self.RCR.header.update({"Host": "booking.vietjetair.com"})
                    # # # 基础参数。
                    self.RCR.post_data = [
                        ("chkRoundTrip", ""), ("lstOrigAP", self.CPR.departure_code),
                        ("lstDestAP", self.CPR.arrival_code), ("dlstDepDate_Day", flight_date.strftime("%d")),
                        ("dlstDepDate_Month", flight_date.strftime("%Y/%m")),
                        ("dlstRetDate_Day", flight_date.strftime("%d")),
                        ("dlstRetDate_Month", flight_date.strftime("%Y/%m")),
                        ("lstCurrency", self.CPR.currency), ("lstResCurrency", self.CPR.currency),
                        ("lstDepDateRange", "0"), ("lstRetDateRange", "0"), ("txtNumAdults", self.CPR.adult_num),
                        ("txtNumChildren", self.CPR.child_num), ("txtNumInfants", "0"),
                        ("lstLvlService", "1"), ("blnFares", "False"), ("txtPromoCode", ""), ("txtRefererId", ""),
                    ]
                    if self.RCR.request_to_post():
                        # # # 安全通过。
                        self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                        return True
            # # # 错误重试。
            self.logger.info(f"请求首页第{count + 1}次超时(*>﹏<*)【index】")
            self.callback_msg = f"请求首页第{count + 1}次超时，请重试。"
            return self.process_to_index(count + 1, max_count)
    
    def process_to_verify(self, count: int = 0, max_count: int = 1) -> bool:
        """Verify process. 验证过程。
        
        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 获取type11地址, bobcmn, slData, blobfp。
            type11, temp_list = self.DPR.parse_to_attributes("src", "css", "script[src]", self.RCR.copy_source)
            for i in temp_list:
                if "type=11" in i:
                    type11 = i
            bob_data, temp_list = self.BPR.parse_to_regex('\["bobcmn"\] = "(.*?)"', self.RCR.copy_source)
            sl_data, sl_list = self.BPR.parse_to_regex('={(.*?)}', self.RCR.copy_source)
            if sl_list:
                sl_data, temp_list = self.BPR.parse_to_regex('"(.*)"', sl_list[-1])
            blob_fp, temp_list = self.BPR.parse_to_regex('\["blobfp"\] = "(.*?)"', self.RCR.copy_source)
            if not type11 or not bob_data or not sl_data or not blob_fp:
                self.logger.info(f"获取cookie参数失败(*>﹏<*)【type11】")
                self.callback_msg = "请通知技术检查程序。"
                return self.process_to_verify(count + 1, max_count)
            # # # 生成header, 请求type11地址获取key参数。
            self.RCR.url = "https://booking.vietjetair.com" + type11
            self.RCR.param_data = None
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Accept": "*/*",
                "Host": "booking.vietjetair.com",
                "Referer": "https://booking.vietjetair.com/ameliapost.aspx?lang=zh",
            })
            if self.RCR.request_to_get():
                key, key_list = self.BPR.parse_to_regex('\["(.*?)"', self.RCR.page_source)
                if key_list:
                    key = key_list[2]
                if not key:
                    self.logger.info(f"获取cookie参数失败(*>﹏<*)【key】")
                    self.callback_msg = "请通知技术检查程序。"
                    return self.process_to_verify(count + 1, max_count)
                # # # 转换key，slData为字符串，并获取type13地址。
                key = key.replace(r"\x", "")
                self.PSR.key = self.PSR.hex_to_string(key)
                sl_data = self.PSR.hex_to_string(sl_data)
                unseal_data = self.PSR.unblock_to_message(sl_data, True)
                type13 = self.PSR.string_to_hex(unseal_data[:48])
                # # # 生成cookie74。
                cookie74 = self.PSR.hex_to_string(self.PSR.cookie74_base)
                cookie74 = self.PSR.block_to_message(cookie74, 7)
                cookie74 = self.PSR.string_to_hex(cookie74)
                cookie74 = type13 + cookie74
                # # # 生成cookie76。
                cookie76_data = self.PSR.hex_to_string(blob_fp)
                cookie76_data = self.PSR.break_into_list(cookie76_data)
                cookie76_data = self.PSR.compose_onto_string(cookie76_data)
                cookie76_data = cookie76_data[15:89]
                cookie76 = self.PSR.block_to_message(cookie76_data * 3, 9)
                cookie76 = self.PSR.string_to_hex(cookie76)
                cookie76 = type13 + cookie76
                # # # 生成cookie75。
                cookie75_data = self.PSR.hex_to_string(self.PSR.cookie75_base)
                cookie75_data = self.PSR.block_to_message(cookie75_data, 4)
                cookie75_data = self.PSR.string_to_hex(cookie75_data)
                cookie75_ef = "6666" + cookie76_data * 2
                cookie75_ef.encode("ISO-8859-1")
                cookie75_ef = self.PSR.block_to_message(cookie75_ef, 16)
                cookie75_ef = self.PSR.string_to_hex(cookie75_ef)
                cookie_bob = bob_data[226:402]
                cookie75 = f"TSdc75a61a_rc=1&TSdc75a61a_id=5&TSdc75a61a_cr={type13}:{cookie75_data}&" \
                           f"TSdc75a61a_ef={type13}{cookie75_ef}&TSdc75a61a_pg=0" \
                           f"&TSdc75a61a_ct=application/x-www-form-urlencoded" \
                           f"&TSdc75a61a_bg={cookie_bob}" \
                           f"&TSdc75a61a_rf=https%3a%2f%2fwww.vietjetair.com%2fSites%2fWeb%2fzh-CN%2fHome"
                if not cookie74 or not cookie75 or not cookie76:
                    self.logger.info(f"获取cookie7x参数失败(*>﹏<*)【cookie7x】")
                    self.callback_msg = "请通知技术检查程序。"
                    return self.process_to_verify(count + 1, max_count)
                # # # 继承header，请求type13地址获取cookie101。
                self.RCR.set_to_cookies(True, [
                    {"name": "TSdc75a61a_74", "value": cookie74, "domain": "booking.vietjetair.com", "path": "/"},
                ])
                self.RCR.url = f"https://booking.vietjetair.com/TSPD/{type13}?type=13"
                if self.RCR.request_to_get():
                    type13rep = self.RCR.page_source[:66]
                    cookie101 = f"1f{type13rep}20fe0000057a682d434e"
                    cookie101 = self.PSR.hex_to_string(cookie101)
                    cookie101 = self.PSR.block_to_message(cookie101, 6)
                    cookie101 = self.PSR.string_to_hex(cookie101)
                    cookie101 = f"{type13}:{type13}{cookie101}"
                    # # # 生成header, 请求地址更新cookie101。
                    self.RCR.set_to_cookies(True, [
                        {"name": "TSdc75a61a_76", "value": cookie76, "domain": "booking.vietjetair.com", "path": "/"},
                        {"name": "TSdc75a61a_75", "value": cookie75, "domain": "booking.vietjetair.com", "path": "/"},
                        {"name": "TSPD_101", "value": cookie101, "domain": "booking.vietjetair.com", "path": "/"},
                    ])
                    self.RCR.url = "https://booking.vietjetair.com/ameliapost.aspx"
                    self.RCR.param_data = None
                    self.RCR.header = self.BFR.format_to_same(self.init_header)
                    self.RCR.header.update({
                        "Host": "booking.vietjetair.com",
                        "Referer": "https://booking.vietjetair.com/ameliapost.aspx?lang=zh",
                        "Upgrade-Insecure-Requests": "1",
                    })
                    self.RCR.post_data = None
                    if self.RCR.request_to_get():
                        success, temp_list = self.DPR.parse_to_attributes(
                            "id", "css", "#clntcap_success", self.RCR.page_source)
                        if not success:
                            self.logger.info(f"获取cookie参数失败(*>﹏<*)【cookie101】")
                            self.callback_msg = "请通知技术检查程序。"
                            return self.process_to_verify(count + 1, max_count)
                        # # # 生成新的cookie101。
                        new101 = self.RCR.get_from_cookies().get('TSPD_101')
                        new101 = f"{new101}:{cookie101[97:]}"
                        # # # 继承header，通过验证。
                        self.RCR.set_to_cookies(True, [
                            {"name": "TSdc75a61a_76", "value": cookie76,
                             "domain": "booking.vietjetair.com", "path": "/"},
                            {"name": "TSdc75a61a_75", "value": cookie75,
                             "domain": "booking.vietjetair.com", "path": "/"},
                            {"name": "TSPD_101", "value": new101, "domain": "booking.vietjetair.com", "path": "/"},
                        ])
                        # # # 转换接口参数日期。
                        flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
                        self.RCR.url = "https://booking.vietjetair.com/ameliapost.aspx"
                        self.RCR.param_data = (("lang", "zh"),)
                        self.RCR.header = self.BFR.format_to_same(self.init_header)
                        post_string = f"chkRoundTrip=&lstOrigAP={self.CPR.departure_code}" \
                                      f"&lstDestAP={self.CPR.arrival_code}" \
                                      f"&dlstDepDate_Day={flight_date.strftime('%d')}" \
                                      f"&dlstDepDate_Month={flight_date.strftime('%Y/%m')}" \
                                      f"&dlstRetDate_Day={flight_date.strftime('%d')}" \
                                      f"&dlstRetDate_Month={flight_date.strftime('%Y/%m')}" \
                                      f"&lstCurrency={self.CPR.currency}&lstResCurrency={self.CPR.currency}" \
                                      f"&lstDepDateRange=0&lstRetDateRange=0" \
                                      f"&txtNumAdults={self.CPR.adult_num}&txtNumChildren={self.CPR.child_num}" \
                                      f"&txtNumInfants=0&lstLvlService=1&blnFares=False&txtPromoCode=&txtRefererId="
                        multipart = self.RCR.set_to_multi({'_pd': post_string})
                        if multipart:
                            self.RCR.header.update({
                                "Content-Type": multipart.content_type,
                                "Origin": "https://booking.vietjetair.com",
                            })
                            self.RCR.post_data = multipart
                            if self.RCR.request_to_post():
                                # # # 安全通过。
                                self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                                return True
            # # # 错误重试。
            self.logger.info(f"请求验证第{count + 1}次超时(*>﹏<*)【verify】")
            self.callback_msg = f"请求验证第{count + 1}次超时，请重试。"
            return self.process_to_verify(count + 1, max_count)
        
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
            # # # 获取上一步灵活的参数。
            origin, temp_list = self.DPR.parse_to_attributes(
                "value", "css", "#lstOrigAP option[selected]", self.RCR.copy_source)
            temp_all, origin_list = self.DPR.parse_to_attributes(
                "value", "css", "#lstOrigAP option", self.RCR.copy_source)
            destination, temp_list = self.DPR.parse_to_attributes(
                "value", "css", "#lstDestAP option[selected]", self.RCR.copy_source)
            temp_all, destination_list = self.DPR.parse_to_attributes(
                "value", "css", "#lstDestAP option", self.RCR.copy_source)
            departure_range, temp_list = self.DPR.parse_to_attributes(
                "value", "css", "#lstDepDateRange option[selected]", self.RCR.copy_source)
            temp_all, departure_list = self.DPR.parse_to_attributes(
                "value", "css", "#lstDepDateRange option", self.RCR.copy_source)
            return_range, temp_list = self.DPR.parse_to_attributes(
                "value", "css", "#lstRetDateRange option[selected]", self.RCR.copy_source)
            temp_all, return_list = self.DPR.parse_to_attributes(
                "value", "css", "#lstRetDateRange option", self.RCR.copy_source)
            if not origin and origin_list:
                origin = origin_list[0]
            if not destination and destination_list:
                destination = destination_list[0]
            if not departure_range and departure_list:
                departure_range = departure_list[0]
            if not return_range and return_list:
                return_range = return_list[0]
            # # # 生成header, 请求航班具体数据页面。
            self.RCR.url = "https://booking.vietjetair.com/ameliapost.aspx"
            self.RCR.param_data = (("lang", "zh"),)
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "booking.vietjetair.com",
                "Origin": "https://booking.vietjetair.com",
                "Referer": "https://booking.vietjetair.com/ameliapost.aspx?lang=zh",
                "Upgrade-Insecure-Requests": "1",
            })
            # # # 基础参数。
            param_batch = [
                ("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
                ("SesID", True, "input[name=SesID]"), ("DebugID", True, "input[name=DebugID]"),
                ("lstOrigAP", False, origin), ("lstDestAP", False, destination),
                ("dlstDepDate_Day", True, "#dlstDepDate_Day option[selected]"),
                ("dlstDepDate_Month", True, "#dlstDepDate_Month option[selected]"),
                ("lstDepDateRange", False, departure_range),
                ("dlstRetDate_Day", True, "#dlstRetDate_Day option[selected]"),
                ("dlstRetDate_Month", True, "#dlstRetDate_Month option[selected]"),
                ("lstRetDateRange", False, return_range), ("txtNumAdults", True, "#txtNumAdults"),
                ("txtNumChildren", True, "#txtNumChildren"), ("txtNumInfants", True, "#txtNumInfants"),
                ("lstLvlService", True, "#lstLvlService"), ("lstResCurrency", False, self.CPR.currency),
                ("lstCurrency", False, self.CPR.currency), ("txtPromoCode", False, ""),
            ]
            # # # 生成请求参数。
            self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
            if self.RCR.request_to_post(is_redirect=True):
                # # # 查询错误信息。
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorMessage", self.RCR.page_source)
                if error:
                    self.logger.info(f"获取航班数据失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"获取航班数据失败【{error}】。"
                    return False
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorCaption", self.RCR.page_source)
                if error:
                    self.logger.info(f"获取航班数据失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"获取航班数据失败【{error}】。"
                    return False
                # # # 解析数据匹配航班座位。
                details, temp_list = self.DPR.parse_to_attributes("id", "css", "#travOpsMain", self.RCR.page_source)
                tables, table_list = self.DPR.parse_to_attributes(
                    "id", "css", "table.FlightsGrid tr[id*=gridTravelOptDep]", self.RCR.page_source)
                if not details or not tables:
                    self.logger.info(f"获取不到航线数据(*>﹏<*)【{self.CPR.departure_code}】【{self.CPR.arrival_code}】")
                    self.callback_msg = "该航线航班已售完。"
                    return False
                # # # 解析接口航班号。
                interface_carrier = self.CPR.flight_num[:2]
                interface_no = self.CPR.flight_num[2:]
                interface_no = self.BFR.format_to_int(interface_no)
                # # # 设置匹配航班标识和坐席标识。
                is_flight = 0
                seats = ""
                for i in range(len(table_list)):
                    # # # 解析网页航班号。
                    source_num, temp_list = self.DPR.parse_to_attributes(
                        "text", "css", f"tr[id=gridTravelOptDep{i+1}] span.airline{interface_carrier}",
                        self.RCR.page_source)
                    source_num = self.BPR.parse_to_clear(source_num)
                    source_carrier = source_num[:2]
                    source_no = source_num[2:]
                    source_no = self.BFR.format_to_int(source_no)
                    # # # 匹配航班号。
                    if interface_carrier == source_carrier and interface_no == source_no:
                        is_flight = 1
                        # # # 获取坐席列表。
                        temp_all, seats_list = self.DPR.parse_to_attributes(
                            "value", "css", f"tr[id=gridTravelOptDep{i+1}] #gridTravelOptDep", self.RCR.page_source)
                        if not seats_list:
                            self.logger.info(f"该航班座位已售完(*>﹏<*)【{self.CPR.flight_num}】")
                            self.callback_msg = "该航班座位已售完。"
                            return False
                        seats = seats_list[0]
                        break
                # # # 没有找到航班号码。
                if not is_flight:
                    self.logger.info(f"查找对应航班号失败(*>﹏<*)【{self.CPR.flight_num}】")
                    self.callback_msg = f"查找对应航班号失败【{self.CPR.flight_num}】，请核实。"
                    return False
                # # # 继承header, 提交座位信息页面。
                self.RCR.url = "https://booking.vietjetair.com//TravelOptions.aspx"
                self.RCR.param_data = (("lang", "zh"), ("st", "pb"), ("sesid", ""), )
                self.RCR.header.update({
                    "Referer": "https://booking.vietjetair.com//TravelOptions.aspx?lang=zh&st=pb&sesid=",
                })
                # # # 基础参数。
                param_batch = [
                    ("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
                    ("button", False, "continue"), ("SesID", True, "input[name=SesID]"),
                    ("DebugID", True, "input[name=DebugID]"), ("SesID", True, "input[name=SesID]"),
                    ("DebugID", True, "input[name=DebugID]"), ("PN", True, "#PN"),
                    ("RPN", True, "#RPN"), ("gridTravelOptDep", False, seats),
                ]
                # # # 生成请求参数
                self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.page_source)
                if self.RCR.request_to_post(is_redirect=True):
                    # # # 查询错误信息
                    error, temp_list = self.DPR.parse_to_attributes(
                        "text", "css", "p.ErrorMessage", self.RCR.page_source)
                    if error:
                        self.logger.info(f"提交查询失败(*>﹏<*)【{error}】")
                        self.callback_msg = f"提交查询失败【{error}】。"
                        return False
                    error, temp_list = self.DPR.parse_to_attributes(
                        "text", "css", "p.ErrorCaption", self.RCR.page_source)
                    if error:
                        self.logger.info(f"提交查询失败(*>﹏<*)【{error}】")
                        self.callback_msg = f"提交查询失败【{error}】。"
                        return False
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
            self.RCR.url = "https://booking.vietjetair.com/Details.aspx"
            self.RCR.param_data = (("lang", "zh"), ("st", "pb"), ("sesid", ""),)
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "booking.vietjetair.com",
                "Origin": "https://booking.vietjetair.com",
                "Referer": "https://booking.vietjetair.com/Details.aspx?lang=zh&st=pb&sesid=",
                "Upgrade-Insecure-Requests": "1",
            })
            # # # 基础参数。
            param_batch = [
                ("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
                ("SesID", True, "input[name=SesID]"), ("DebugID", True, "input[name=DebugID]"),
                ("button", False, "continue"),
            ]
            # # # 追加每个成人具体的参数。
            for n, v in enumerate(self.CPR.adult_list):
                last_name = v.get("last_name")
                last_name = self.BPR.parse_to_clear(last_name)
                first_name = v.get("first_name")
                first_name = self.BPR.parse_to_separate(first_name)
                adult_batch = [
                    (f"txtPax{n+1}_Gender", False, v.get("gender")),
                    (f"txtPax{n+1}_LName", False, last_name),
                    (f"txtPax{n+1}_FName", False, first_name),
                    (f"txtPax{n+1}_DOB_Day", False, ""),
                    (f"txtPax{n+1}_DOB_Month", False, ""),
                    (f"txtPax{n+1}_DOB_Year", False, ""),
                    (f"txtPax{n+1}_Phone1", False, ""),
                    (f"txtPax{n+1}_Passport", False, ""),
                    (f"dlstPax{n+1}_PassportExpiry_Day", False, ""),
                    (f"dlstPax{n+1}_PassportExpiry_Month", False, ""),
                    (f"txtPax{n+1}_Nationality", False, ""),
                    (f"txtPax{n+1}_PrefLanguage", False, "1"),
                ]
                # # # 如果是第一个成人，需要添加联系信息。
                if n == 0:
                    adult_batch.extend([
                        (f"txtPax{n+1}_Phone2", False, "+86" + self.CPR.contact_mobile),
                        (f"txtPax{n+1}_Addr1", False, "Beijing"),
                        (f"txtPax{n+1}_City", False, "Beijing"),
                        (f"txtPax{n+1}_Ctry", False, "49"),
                        (f"txtPax{n+1}_Prov", False, "-1"),
                        (f"txtPax{n + 1}_EMail", False, self.CPR.contact_email),
                    ])
                else:
                    adult_batch.append((f"txtPax{n + 1}_EMail", False, ""))
                # # # 追加每个成人具体的参数。
                param_batch.extend(adult_batch)
            # # # 追加每个儿童具体的参数。
            if self.CPR.child_num:
                for n, v in enumerate(self.CPR.child_list):
                    n += self.CPR.adult_num
                    last_name = v.get("last_name")
                    last_name = self.BPR.parse_to_clear(last_name)
                    first_name = v.get("first_name")
                    first_name = self.BPR.parse_to_separate(first_name)
                    child_batch = [
                        (f"txtPax{n+1}_Gender", False, "C"),
                        (f"txtPax{n+1}_LName", False, last_name),
                        (f"txtPax{n+1}_FName", False, first_name),
                        (f"txtPax{n+1}_DOB_Day", False, ""),
                        (f"txtPax{n+1}_DOB_Month", False, ""),
                        (f"txtPax{n+1}_DOB_Year", False, ""),
                        (f"txtPax{n+1}_Phone1", False, ""),
                        (f"txtPax{n+1}_Passport", False, ""),
                        (f"dlstPax{n+1}_PassportExpiry_Day", False, ""),
                        (f"dlstPax{n+1}_PassportExpiry_Month", False, ""),
                        (f"txtPax{n+1}_Nationality", False, ""),
                        (f"txtPax{n+1}_PrefLanguage", False, "1"),
                        (f"txtPax{n+1}_EMail", False, ""),
                    ]
                    # # # 追加每个儿童具体的参数。
                    param_batch.extend(child_batch)
            # # # 生成请求参数。
            self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
            if self.RCR.request_to_post(is_redirect=True):
                # # # 查询错误信息。
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorMessage", self.RCR.page_source)
                if error:
                    self.logger.info(f"添加乘客失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"添加乘客失败【{error}】。"
                    return False
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorCaption", self.RCR.page_source)
                if error:
                    self.logger.info(f"添加乘客失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"添加乘客失败【{error}】。"
                    return False
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
            # # # 添加附加页面，要判断有什么附加, 目前有餐饮, 优先权，巴士。
            meal, temp_list = self.DPR.parse_to_attributes(
                "class", "css", "#shopPaxOmega .shopPaxMstr .Meal.Itemimage", self.RCR.copy_source)
            priority, temp_list = self.DPR.parse_to_attributes(
                "class", "css", "#shopPaxOmega .shopPaxMstr .Priority.Itemimage", self.RCR.copy_source)
            bus, temp_list = self.DPR.parse_to_attributes(
                "class", "css", "#shopPaxOmega .shopPaxMstr .Bus.Itemimage", self.RCR.copy_source)
            # # # 生成header, 添加附加页面，要判断有什么附加再追加。
            self.RCR.url = "https://booking.vietjetair.com/AddOns.aspx"
            self.RCR.param_data = (("lang", "zh"), ("st", "pb"), ("sesid", ""),)
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "booking.vietjetair.com",
                "Origin": "https://booking.vietjetair.com",
                "Referer": "https://booking.vietjetair.com/AddOns.aspx?lang=zh&st=pb&sesid=",
                "Upgrade-Insecure-Requests": "1",
            })
            # # # 基础参数。
            param_batch = [
                ("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
                ("SesID", True, "input[name=SesID]"), ("DebugID", True, "input[name=DebugID]"),
                ("button", False, "continue"), ("m1th", True, "#m1th"), ("m1p", True, "#m1p"),
                ("ctrSeatAssM", True, "#ctrSeatAssM"), ("ctrSeatAssP", True, "#ctrSeatAssP"),
                ("chkInsuranceNo", False, "N")
            ]
            # # # 追加每个成人具体的参数。
            for n, v in enumerate(self.CPR.adult_list):
                # # # 判断行李并累计公斤数。
                weight = v.get('baggage')
                kilogram = 0
                if weight:
                    for w in weight:
                        kilogram += self.BFR.format_to_int(w.get('weight'))
                # # # 带不带行李都要填行李参数，如果有需要取值。
                baggage, temp_list = self.DPR.parse_to_attributes(
                    "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                    f"[{n + 1}]//select[@class='lstShopSelect']/@id", self.RCR.copy_source)
                # # # 解析行李参数。
                if kilogram:
                    baggage_value, temp_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n+1}]//select[@class='lstShopSelect']"
                        f"//option[contains(., '{kilogram}')]/@value", self.RCR.copy_source)
                    pax_item, temp_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n+1}]//select[@class='lstShopSelect']"
                        f"//option[contains(., '{kilogram}')]/@hidpaxitem", self.RCR.copy_source)
                    pax_item = f"hidpaxitem:{pax_item}"
                    pax_value, temp_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n+1}]//select[@class='lstShopSelect']"
                        f"//option[contains(., '{kilogram}')]/@hidpaxvalue", self.RCR.copy_source)
                    # # # 解析行李价格，按公斤比数取价格。
                    price, temp_list = self.BPR.parse_to_regex("VND\|(.*?)\|", pax_value)
                    price = self.BFR.format_to_float(2, price)
                    if not price:
                        self.logger.info(f"匹配行李价格失败(*>﹏<*)【{n}】【{v}】")
                        self.callback_msg = "匹配行李失败"
                        return False
                    for w in weight:
                        w_weight = self.BFR.format_to_int(w.get('weight'))
                        w_price = price * (w_weight / kilogram)
                        w_price = self.BFR.format_to_float(2, w_price)
                        w['price'] = w_price
                        self.CPR.return_baggage.append(w)
                    self.baggage_price += price
                else:
                    baggage_value = "-1"
                    pax_item = "-1"
                    pax_value = "-1"
                # # # 基础参数。
                adult_batch = [
                    (f"m1p{n+1}", True, f"#m1p{n+1}"), (f"m1p{n+1}rpg", True, f"#m1p{n+1}rs"),
                    (baggage, False, baggage_value), (pax_item, False, pax_value), ("shpsel", False, "")
                ]
                # # # 判断有没有餐饮附加，如果有需要追加参数。
                if meal:
                    meal_name, name_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n + 1}]//tr[contains(@class, 'Meal')]"
                        f"//input[contains(@name, 'hidPaxItem')]/@name", self.RCR.copy_source)
                    meal_value, value_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n + 1}]//tr[contains(@class, 'Meal')]"
                        f"//input[contains(@name, 'hidPaxItem')]/@value", self.RCR.copy_source)
                    # # # 参数需要追加列表。
                    for i in range(len(name_list)):
                        adult_batch.extend([(name_list[i], False, value_list[i]), ("shpsel", False, "")])
                # # # 判断有没有优先权，如果有需要追加参数。
                if priority:
                    priority_name, temp_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n + 1}]//tr[contains(@class, 'Priority')]"
                        f"//input[contains(@name, 'hidPaxItem')]/@name", self.RCR.copy_source)
                    priority_value, temp_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n + 1}]//tr[contains(@class, 'Priority')]"
                        f"//input[contains(@name, 'hidPaxItem')]/@value", self.RCR.copy_source)
                    adult_batch.extend([
                        (priority_name, False, priority_value), (f"priorityCheckinChoice1{n+1}", False, "on"),
                        ("shpsel", False, "")
                    ])
                # # # 判断有没有巴士，如果有需要追加参数。
                if bus:
                    bus_name, temp_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n + 1}]//tr[contains(@class, 'Bus')]"
                        f"//input[contains(@name, 'hidPaxItem')]/@name", self.RCR.copy_source)
                    bus_value, temp_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n + 1}]//tr[contains(@class, 'Bus')]"
                        f"//input[contains(@name, 'hidPaxItem')]/@value", self.RCR.copy_source)
                    adult_batch.extend([(bus_name, False, bus_value), (f"busItemChoice1{n+1}", False, "on")])
                # # # 追加每个成人具体的参数。
                param_batch.extend(adult_batch)
            # # # 追加每个儿童具体的参数。
            if self.CPR.child_num:
                for n, v in enumerate(self.CPR.child_list):
                    # # # 判断行李并累计公斤数。
                    n += self.CPR.adult_num
                    weight = v.get('baggage')
                    kilogram = 0
                    if weight:
                        for w in weight:
                            kilogram += self.BFR.format_to_int(w.get('weight'))
                    # # # 带不带行李都要填行李参数，如果有需要取值。
                    baggage, temp_list = self.DPR.parse_to_attributes(
                        "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                        f"[{n + 1}]//select[@class='lstShopSelect']/@id", self.RCR.copy_source)
                    # # # 解析行李参数。
                    if kilogram:
                        baggage_value, temp_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//select[@class='lstShopSelect']"
                            f"//option[contains(., '{kilogram}')]/@value", self.RCR.copy_source)
                        pax_item, temp_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//select[@class='lstShopSelect']"
                            f"//option[contains(., '{kilogram}')]/@hidpaxitem", self.RCR.copy_source)
                        pax_item = f"hidpaxitem:{pax_item}"
                        pax_value, temp_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//select[@class='lstShopSelect']"
                            f"//option[contains(., '{kilogram}')]/@hidpaxvalue", self.RCR.copy_source)
                        # # # 解析行李价格，按公斤比数取价格。
                        price, temp_list = self.BPR.parse_to_regex("VND\|(.*?)\|", pax_value)
                        price = self.BFR.format_to_float(2, price)
                        if not price:
                            self.logger.info(f"匹配行李价格失败(*>﹏<*)【{n}】【{v}】")
                            self.callback_msg = "匹配行李失败"
                            return False
                        for w in weight:
                            w_weight = self.BFR.format_to_int(w.get('weight'))
                            w_price = price * (w_weight / kilogram)
                            w_price = self.BFR.format_to_float(2, w_price)
                            w['price'] = w_price
                            self.CPR.return_baggage.append(w)
                        self.baggage_price += price
                    else:
                        baggage_value = "-1"
                        pax_item = "-1"
                        pax_value = "-1"
                    # # # 基础参数。
                    child_batch = [
                        (f"m1p{n + 1}", True, f"#m1p{n + 1}"), (f"m1p{n + 1}rpg", True, f"#m1p{n + 1}rs"),
                        (baggage, False, baggage_value), (pax_item, False, pax_value), ("shpsel", False, "")
                    ]
                    # # # 判断有没有餐饮附加，如果有需要追加参数。
                    if meal:
                        meal_name, name_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//tr[contains(@class, 'Meal')]"
                            f"//input[contains(@name, 'hidPaxItem')]/@name", self.RCR.copy_source)
                        meal_value, value_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//tr[contains(@class, 'Meal')]"
                            f"//input[contains(@name, 'hidPaxItem')]/@value", self.RCR.copy_source)
                        # # # 参数需要追加列表。
                        for i in range(len(name_list)):
                            child_batch.extend([(name_list[i], False, value_list[i]), ("shpsel", False, "")])
                    # # # 判断有没有优先权，如果有需要追加参数。
                    if priority:
                        priority_name, temp_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//tr[contains(@class, 'Priority')]"
                            f"//input[contains(@name, 'hidPaxItem')]/@name", self.RCR.copy_source)
                        priority_value, temp_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//tr[contains(@class, 'Priority')]"
                            f"//input[contains(@name, 'hidPaxItem')]/@value", self.RCR.copy_source)
                        child_batch.extend([
                            (priority_name, False, priority_value), (f"priorityCheckinChoice1{n + 1}", False, "on"),
                            ("shpsel", False, "")
                        ])
                    # # # 判断有没有巴士，如果有需要追加参数。
                    if bus:
                        bus_name, temp_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//tr[contains(@class, 'Bus')]"
                            f"//input[contains(@name, 'hidPaxItem')]/@name", self.RCR.copy_source)
                        bus_value, temp_list = self.DPR.parse_to_attributes(
                            "value", "xpath", f"(//table[@id='shopPaxOmega']//table[@class='shopPaxMstr'])"
                            f"[{n + 1}]//tr[contains(@class, 'Bus')]"
                            f"//input[contains(@name, 'hidPaxItem')]/@value", self.RCR.copy_source)
                        child_batch.extend([(bus_name, False, bus_value), (f"busItemChoice1{n + 1}", False, "on")])
                    # # # 追加每个儿童具体的参数。
                    param_batch.extend(child_batch)
            # # # 生成请求参数。
            self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
            if self.RCR.request_to_post(is_redirect=True):
                # # # 查询错误信息。
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorMessage", self.RCR.page_source)
                if error:
                    self.logger.info(f"添加附加服务失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"添加附加服务失败【{error}】。"
                    return False
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorCaption", self.RCR.page_source)
                if error:
                    self.logger.info(f"添加附加服务失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"添加附加服务失败【{error}】。"
                    return False
                # # # 安全通过。
                self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                return True
            # # # 错误重试。
            self.logger.info(f"添加附加服务第{count + 1}次超时(*>﹏<*)【service】")
            self.callback_msg = f"添加附加服务第{count + 1}次超时, 请重试。"
            return self.process_to_service(count + 1, max_count)

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
            # # # 生成卡信息并判断，日期需要月底最后一天。
            card_name = f"{self.CPR.card_last} {self.CPR.card_first}"
            card_date = self.DFR.format_to_transform("20" + self.CPR.card_date, "%Y%m")
            card_day = self.DFR.format_to_last(card_date.year, card_date.month)
            card_date = card_date.strftime("%Y/%m") + f"/{card_day}"
            card_code = self.AFR.decrypt_into_aes(
                self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.card_code)
            if not card_code:
                self.logger.info(f"解密支付卡失败(*>﹏<*)【{self.CPR.card_code}】")
                self.callback_msg = "解密支付卡失败，请通知技术检查程序。"
                return False
            # # # 生成header, 添加支付卡信息页面。
            self.RCR.url = "https://booking.vietjetair.com/Payments.aspx"
            self.RCR.param_data = (("lang", "zh"), ("st", "pb"), ("sesid", ""),)
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "booking.vietjetair.com",
                "Origin": "https://booking.vietjetair.com",
                "Referer": "https://booking.vietjetair.com/Payments.aspx?lang=zh&st=pb&sesid=",
                "Upgrade-Insecure-Requests": "1",
            })
            # # # 基础参数。
            param_batch = [
                ("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
                ("button", False, ""), ("SesID", True, "input[name=SesID]"), ("DebugID", True, "input[name=DebugID]"),
                ("SesID", True, "input[name=SesID]"), ("DebugID", True, "input[name=DebugID]"),
                ("SesID", True, "input[name=SesID]"), ("DebugID", True, "input[name=DebugID]"),
                ("lstPmtType", True, "#lstPmtType"), ("txtCardNo", False, self.CPR.card_num),
                ("dlstExpiry", False, card_date), ("txtCVC", False, card_code),
                ("txtCardholder", False, card_name), ("txtAddr1", False, "Beijing"),
                ("txtAddr1", False, "Beijing"), ("txtCity", False, "Beijing"),
                ("txtPCode", False, "100000"), ("lstCtry", False, "49"), ("lstProv", False, "-1"),
                ("txtPhone", False, self.CPR.contact_mobile), ("dangerous_goods_check", False, "1")
            ]
            # # # 生成请求参数。
            self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
            if self.RCR.request_to_post(is_redirect=True):
                # # # 查询错误信息。
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorMessage", self.RCR.page_source)
                if error:
                    self.logger.info(f"请求支付失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"请求支付失败【{error}】。"
                    return False
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorCaption", self.RCR.page_source)
                if error:
                    self.logger.info(f"请求支付失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"请求支付失败【{error}】。"
                    return False
                # # # 获取最终总价格。
                total_price, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "#rescharges tr:last-child td:last-child strong", self.RCR.page_source)
                total_price = self.BPR.parse_to_clear(total_price)
                total_price = total_price.strip(self.CPR.currency)
                self.total_price = self.BFR.format_to_float(2, total_price)
                if not total_price:
                    self.logger.info(f"支付页面获取总价失败(*>﹏<*)【payment】")
                    self.callback_msg = f"支付页面获取总价失败，请通知技术检查程序。"
                    return self.process_to_payment(count + 1, max_count)
                # # # 安全通过。
                self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                # # # 比价格是否要继续支付。
                if self.process_to_compare():
                    return True
                else:
                    return False
            # # # 错误重试。
            self.logger.info(f"请求支付第{count + 1}次超时(*>﹏<*)【payment】")
            self.callback_msg = f"请求支付第{count + 1}次超时，请重试。"
            return self.process_to_payment(count + 1, max_count)

    def process_to_compare(self, count: int = 0, max_count: int = 1) -> bool:
        """Compare process. 对比过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 生成header, 查询货币汇率。
            self.RCR.url = f"http://flight.yeebooking.com/yfa/tool/interface/convert_conversion_result?" \
                           f"foreignCurrency={self.CPR.currency}&carrier=VJ"
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
            # # # 计算最终返回价格，不含行李价格。
            if self.baggage_price:
                self.baggage_price = self.BFR.format_to_float(2, self.baggage_price)
                self.return_price = self.total_price - self.baggage_price
                self.return_price = self.BFR.format_to_float(2, self.return_price)
            else:
                self.return_price = self.total_price
            # # # 生成header, 确认订单信息和信用卡页面。
            self.RCR.url = "https://booking.vietjetair.com/Confirm.aspx"
            self.RCR.param_data = (("lang", "zh"), ("st", "pb"), ("sesid", ""),)
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "booking.vietjetair.com",
                "Origin": "https://booking.vietjetair.com",
                "Referer": "https://booking.vietjetair.com/Confirm.aspx?lang=zh&st=pb&sesid=",
                "Upgrade-Insecure-Requests": "1",
            })
            # # # 基础参数。
            param_batch = [
                ("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
                ("SesID", True, "input[name=SesID]"), ("DebugID", True, "input[name=DebugID]"),
                ("button", False, "continue"), ("lstPmtType", True, "#lstPmtType"),
                ("txtCardholder", True, "#txtCardholder"), ("chkIAgree", False, "on"),
            ]
            # # # 追加每个成人具体的参数。
            for n, v in enumerate(self.CPR.adult_list):
                last_name = v.get("last_name")
                last_name = self.BPR.parse_to_clear(last_name)
                first_name = v.get("first_name")
                first_name = self.BPR.parse_to_separate(first_name)
                adult_batch = [
                    (f"txtPax{n+1}_Gender", False, v.get("gender")),
                    (f"txtPax{n+1}_LName", False, last_name),
                    (f"txtPax{n+1}_FName", False, first_name),
                    (f"txtPax{n+1}_PrefLanguage", False, "1"),
                ]
                param_batch.extend(adult_batch)
            # # # 追加每个儿童具体的参数。
            if self.CPR.child_num:
                for n, v in enumerate(self.CPR.child_list):
                    n += self.CPR.adult_num
                    last_name = v.get("last_name")
                    last_name = self.BPR.parse_to_clear(last_name)
                    first_name = v.get("first_name")
                    first_name = self.BPR.parse_to_separate(first_name)
                    child_batch = [
                        (f"txtPax{n+1}_Gender", False, "C"),
                        (f"txtPax{n+1}_LName", False, last_name),
                        (f"txtPax{n+1}_FName", False, first_name),
                        (f"txtPax{n+1}_PrefLanguage", False, "1"),
                    ]
                    param_batch.extend(child_batch)
            # # # 生成请求参数。
            self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
            if self.RCR.request_to_post(is_redirect=True):
                # # # 查询错误信息。
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorMessage", self.RCR.page_source)
                if error:
                    self.logger.info(f"获取支付编码失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"获取PNR失败【{error}】。"
                    self.callback_data["orderIdentification"] = 2
                    return False
                error, temp_list = self.DPR.parse_to_attributes(
                    "text", "css", "p.ErrorCaption", self.RCR.page_source)
                if error:
                    self.logger.info(f"获取支付编码失败(*>﹏<*)【{error}】")
                    self.callback_msg = f"获取PNR失败【{error}】。"
                    self.callback_data["orderIdentification"] = 2
                    return False
                # # # 继承header, 具体等待和支付页面。
                self.RCR.url = "https://booking.vietjetair.com/Processing.aspx"
                self.RCR.header.update(
                    {"Referer": "https://booking.vietjetair.com/Processing.aspx?lang=zh&st=pb&sesid="})
                # # # 基础参数。
                param_batch = [
                    ("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
                    ("SesID", True, "input[name=SesID]"), ("DebugID", True, "input[name=DebugID]"),
                ]
                # # # 生成请求参数。
                self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.page_source)
                if self.RCR.request_to_post(is_redirect=True):
                    # # # 查询错误信息
                    error, temp_list = self.DPR.parse_to_attributes(
                        "text", "css", "p.ErrorMessage", self.RCR.page_source)
                    if error:
                        self.logger.info(f"获取支付编码失败(*>﹏<*)【{error}】")
                        self.callback_msg = f"获取PNR失败【{error}】。"
                        self.callback_data["orderIdentification"] = 2
                        return False
                    error, temp_list = self.DPR.parse_to_attributes(
                        "text", "css", "p.ErrorCaption", self.RCR.page_source)
                    if error:
                        self.logger.info(f"获取支付编码失败(*>﹏<*)【{error}】")
                        self.callback_msg = f"获取PNR失败【{error}】。"
                        self.callback_data["orderIdentification"] = 2
                        return False
                    # # # 获取PNR，8位。
                    # self.record, temp_list = self.DPR.parse_to_attributes(
                    #     "text", "css", ".AuthNumber", self.RCR.page_source)
                    # self.record = self.BPR.parse_to_clear(self.record)
                    # if not self.record or len(self.record) < 8:
                    #     self.logger.info("获取支付编码失败(*>﹏<*)【record】")
                    #     self.callback_msg = "获取PNR失败，可能已出票，请核对。"
                    #     self.callback_data["orderIdentification"] = 2
                    #     return False
                    # # # # VJ和VZ需要截取前8位数字。
                    # self.record = self.record[:8]
                    
                    # # # 获取PNR，6位。
                    self.record, temp_list = self.DPR.parse_to_attributes(
                        "text", "css", ".ResNumber", self.RCR.page_source)
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

