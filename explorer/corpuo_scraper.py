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
from detector.corpuo_simulator import CorpUOSimulator
import time
import json
import random
import redis


class CorpUOScraper(RequestWorker):
	"""UO采集器，UO网站流程交互。"""
	
	def __init__(self) -> None:
		RequestWorker.__init__(self)
		self.RCR = RequestCrawler()  # 请求爬行器。
		self.AFR = AESFormatter()  # AES格式器。
		self.BFR = BasicFormatter()  # 基础格式器。
		self.BPR = BasicParser()  # 基础解析器。
		self.CFR = CallBackFormatter()  # 回调格式器。
		self.CPR = CallInParser()  # 接入解析器。
		self.DFR = DateFormatter()  # 日期格式器。
		self.DPR = DomParser()  # 文档解析器。
		
		self.CSR = CorpUOSimulator()  # UO模拟器
		# # # 请求中用到的变量
		self.verify_token: str = ""  # 认证token
		self.tab_id: str = ""  # 认证tab id
		self.ajax_header: str = ""  # 认证ajax header
		self.temp_source: str = ""  # 临时源数据
		self.hold_button: str = ""  # 占舱按钮
		self.return_price: float = 0.0  # 返回价格。
		
		# # # 返回中用到的变量。
		self.total_price: float = 0.0  # 总价。
		self.return_price: float = 0.0  # 返回价格。
		self.baggage_price: float = 0.0  # 行李总价。
		self.record: str = ""  # 票号
		self.pnr_timeout: str = ""  # 票号超时时间
		self.api_key: str = ""  # header 中的apiKey
		self.availability_apikey: str = ""  # Key
		self.ancillaries_apikey: str = ""  # Key
		
		self.segmentId = ""
	
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
		self.CSR.logger = self.logger
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
		self.callback_data = self.CFR.format_to_async()
		# # # 解析接口参数。
		if not self.CPR.parse_to_interface(source_dict):
			self.callback_data['msg'] = "请通知技术检查接口数据参数。"
			return self.callback_data
		self.logger.info(source_dict)
		# # # 启动爬虫，建立header。
		self.RCR.set_to_session()
		self.RCR.set_to_proxy(enable_proxy, address)
		self.user_agent, self.init_header = self.RCR.build_to_header("Chrome")
		# # # 更新联系方式
		self.CPR.contact_email = "168033518@qq.com"
		self.CPR.contact_mobile = "16639168284"
		self.RCR.timeout = 10  # 超时时间
		#
		if self.process_to_login():
			
			# 如果有 PNR 直接支付
			if self.CPR.pnr_code:
				self.logger.info(f"有PNR， 进行付款 | 票号： {self.CPR.pnr_code}   ")
				if self.process_to_record():
					self.process_to_return()
					self.logger.removeHandler(self.handler)
					return self.callback_data
			else:
				self.logger.info("没有有PNR， 进行占舱并付款")
				if self.process_to_search():
					if self.process_to_passenger():
						if self.process_to_service():
							if self.process_to_payment():
									if self.process_to_record():
										self.process_to_return()
										self.logger.removeHandler(self.handler)
										return self.callback_data
		
		# # # 错误返回。
		self.callback_data["occupyCabinId"] = self.CPR.task_id
		self.callback_data['msg'] = self.callback_msg
		# self.callback_data['msg'] = "解决问题中，请手工站位。"
		self.callback_data["carrierAccount"] = ""
		self.callback_data['carrierAccountAgent'] = self.CPR.username
		self.logger.info(self.callback_data)
		self.logger.removeHandler(self.handler)
		return self.callback_data
	
	def get_sun_proxy(self):
		'''
		获取redis池里的代理
		:return: '183.165.32.160:43031'
		'''
		self.RCR.set_to_proxy(False, "")
		try:
			pool = redis.ConnectionPool(host='118.31.118.146', port=6379, db=6, password='PkQDgGa51e76')
			res_prod = redis.Redis(connection_pool=pool)
			proxy: str = res_prod.rpop('uorealtime_proxy_pool').decode()
			res_prod.srem('uorealtime_proxy_pool_set', proxy)
			res_prod.close()
		except Exception as ex:
			self.callback_msg = "获取太阳代理失败"
			self.logger.info(ex)
			return False
		else:
			self.RCR.set_to_proxy(enable_proxy=True, address=f"http://{proxy}")
			return True
	
	def get_proxy(self, count: int = 0, max_count: int = 4):
		"""
		判断代理，在规定时间段内使用
		:return:
		"""
		if count >= max_count:
			return False
		else:
			
			self.RCR.set_to_proxy(False, "")
			# 获取代理， 并配置代理
			# 托马斯
			# log_account = account[random.randint(0, len(account) - 1)]
			service_type = ["3", "4", "112"]
			self.RCR.url = 'http://cloudmonitorproxy.51kongtie.com/Proxy/getProxyByServiceType?proxyNum=1&serviceType=' + \
			               service_type[random.randint(0, 2)]
			# 塔台
			# self.RCR.url = 'http://cloudmonitorproxy.51kongtie.com/Proxy/getProxyByServiceType?proxyNum=1&serviceType=112'
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.param_data = None
			if self.RCR.request_to_get('json'):
				for ip in self.RCR.page_source:
					if ip.get('proxyIP'):
						self.proxys = "http://yunku:123@" + str(ip.get('proxyIP')) + ":" + str(ip.get('prot'))
						# self.proxys = "http://yunku:123@" + "60.179.17.209" + ":" + "3138"
						# self.proxys = "http://94.249.236.165:8080"
						self.RCR.set_to_proxy(enable_proxy=True, address=self.proxys)
						return True
					else:
						self.callback_msg = f"代理地址获取失败"
						self.logger.info(self.callback_msg)
						return self.get_proxy(count + 1, max_count)
			else:
				# self.RCR.set_to_proxy(enable_proxy=True, address='http://yunku:123@120.5.51.17:3138')
				self.callback_msg = f"代理地址获取失败"
				self.logger.info(self.callback_msg)
				return self.get_proxy(count + 1, max_count)
	
	def process_to_login(self, count: int = 0, max_count: int = 4) -> bool:
		"""Login process. 登录过程。

		Args:
			count (int): 累计计数。
			max_count (int): 最大计数。

		Returns:
			bool
		"""
		if count >= max_count:
			return False
		else:
			# # # 解析登录首页
			self.RCR.url = "https://www.hkexpress.com/zh-CN/agencies/login"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "www.hkexpress.com",
				"Upgrade-Insecure-Requests": "1"
			})
			if self.RCR.request_to_get():
				main_js, temp_list = self.DPR.parse_to_attributes(
					"src", "css", "script[src*='main.bundle.js']", self.RCR.page_source)
				if not main_js:
					self.logger.info("main_js 提取失败 (*>﹏<*)【login】")
					self.callback_msg = "登录超时或者错误"
					return False
				
				# 获取 apikey
				self.RCR.url = main_js
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "*/*",
					"Host": "static.hkexpress.com",
					"Referer": "https://www.hkexpress.com/zh-CN/agencies/login"
				})
				if self.RCR.request_to_get():
					# 提取 apiKey， 设置到 header 中
					self.api_key, temp_list = self.BPR.parse_to_regex(',apiKey:"(.*?)"', self.RCR.page_source)
					self.availability_apikey, temp_list = self.BPR.parse_to_regex(',availabilityApiKey:"(.*?)"',
					                                                              self.RCR.page_source)
					self.ancillaries_apikey, temp_list = self.BPR.parse_to_regex(',ancillariesApiKey:"(.*?)"',
					                                                             self.RCR.page_source)
					
					self.js_code, temp_list = self.BPR.parse_to_regex(
						'var.t\=new.RegExp\((.*)\)\.exec\(e\)', self.RCR.page_source)
					
					if not self.api_key or not self.availability_apikey:
						self.logger.info("api_key 提取失败 (*>﹏<*)【login】")
						self.callback_msg = "登录超时或者错误"
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/agent"
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Accept": "application/json, text/plain, */*",
						"Content-Type": "application/json; charset=UTF-8",
						"Host": "booking-api.hkexpress.com",
						"Origin": "https://www.hkexpress.com",
						"Referer": "https://www.hkexpress.com/zh-CN/agencies/login",
						"ApiKey": self.api_key
					})
					# 解密，
					password = self.AFR.decrypt_into_aes(
						self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.password)
					self.RCR.post_data = {"username": self.CPR.username, "password": password,
					                      "loginType": "Agent"}
					if self.RCR.request_to_post("json", "json"):
						success = self.RCR.page_source.get("success")
						if success is False:
							error, temp_list = self.BPR.parse_to_path("$.errors[0].description",
							                                          self.RCR.page_source)
							if error:
								self.logger.info(f"登录失败|{error}")
								self.callback_msg = f"登录失败|{error}"
								return False
							else:
								self.logger.info(f"登录失败|{self.RCR.page_source}")
								self.callback_msg = f"登录失败|{self.RCR.page_source}"
								return False
						else:
							# # # 提取账户信息 account information
							account_first_name, account_name_list = self.BPR.parse_to_path(
								"$.firstName", self.RCR.page_source)
							account_last_name, account_name_list = self.BPR.parse_to_path(
								"$.lastName", self.RCR.page_source)
							
							self.logger.info(f"登录成功 | {account_last_name} | {account_first_name}")
							self.RCR.url = "https://booking.hkexpress.com/zh-CN/agencies/agencybookings"
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								"Host": "booking.hkexpress.com",
								"Referer": "https://www.hkexpress.com/zh-CN/agencies/login",
								"Upgrade-Insecure-Requests": "1"
							})
							if self.RCR.request_to_get():
								return True
			
			self.logger.info(f"登录第{count + 1}次超时或者错误(*>﹏<*)【login】")
			self.callback_msg = f"登录第{count + 1}次超时或者错误"
			# self.get_sun_proxy()
			return self.process_to_login(count + 1, max_count)
	
	def circle(self, count: int = 0, max_count: int = 10):
		if count >= max_count:
			return False
		else:
			token = self.CSR.token_md5(self.verify_token, self.js_code)
			
			self.RCR.url = "https://availability-api.hkexpress.com/api/v1.0/availability/lowfareavailability"
			self.RCR.param_data = None
			# self.RCR.header = self.BFR.format_to_same(self.init_header)
			# self.RCR.header.update({
			# 	"Accept": "*/*",
			# 	"Access-Control-Request-Method": "POST",
			# 	"Access-Control-Request-Headers": "apikey,content-type",
			# 	"Host": "availability-api.hkexpress.com",
			# 	"Origin": "https://booking.hkexpress.com",
			# 	"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
			# })
			# self.RCR.post_data = None
			# self.RCR.request_to_options()
			
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json; charset=UTF-8",
				"Host": "availability-api.hkexpress.com",
				"Origin": "https://booking.hkexpress.com",
				"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
				"ApiKey": self.availability_apikey
			})
			flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
			first_day = self.DFR.format_to_custom(flight_date, -3)
			last_day = self.DFR.format_to_custom(flight_date, 3)
			self.RCR.post_data = {"token": token,
			                      "outboundDepartureStation": self.CPR.departure_code,
			                      "outboundArrivalStation": self.CPR.arrival_code,
			                      "outboundStartDate": first_day.strftime("%Y-%m-%d"),
			                      "outboundEndDate": last_day.strftime("%Y-%m-%d"),
			                      "tripType": "Outbound", "cultureCode": "zh-CN",
			                      "adultsNumber": self.CPR.adult_num,
			                      "childrenNumber": self.CPR.child_num,
			                      "infantsNumber": self.CPR.infant_num, "currency": ""}
			
			if self.RCR.request_to_post("json", "json"):
				
				success = self.RCR.page_source.get("success")
				if not success:
					error, temp_list = self.BPR.parse_to_path("$..code",
					                                          self.RCR.page_source)
					if error:
						self.logger.info(f"获取航班价格失败| 异常原因： {error}")
						self.callback_msg = f"获取航班价格失败| 异常原因： {error}"
						return False
				
				if "message" in self.RCR.page_source:
					error, error_list = self.DPR.parse_to_attributes(
						"text", "css", 'div[class="message"]', self.RCR.page_source)
					error_id, error_list = self.DPR.parse_to_attributes(
						"text", "css", 'div[class="message"] strong', self.RCR.page_source)
					self.logger.info(f"请求被阻止【{error} - {error_id}】")
					self.callback_msg = f"请求被阻止【{error} - {error_id}】"
					return False
				# 判断航班状态，
				# 1， NoFlights  无航班
				# 2， SoldOut    售罄
				# 3， Available  可用
				html, temp_html = self.BPR.parse_to_path('$..journeys', self.RCR.page_source)
				flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
				first_day = flight_date.strftime('%Y-%m-%d')
				for i in html:
					if str(first_day) in i.get('date'):
						if i.get('status') == "Available":
							continue
						elif i.get('status') == "NoFlights":
							self.logger.info(f"当前日期无航班【{self.CPR.flight_date}】")
							self.callback_msg = f"当前日期无航班【{self.CPR.flight_date}】"
							return False
						elif i.get('status') == "SoldOut":
							self.logger.info(f"当前航班票已售罄【{self.CPR.flight_date}】【机票状态：{i.get('status')}】")
							self.callback_msg = f"当前航班票已售罄【{self.CPR.flight_date}】【机票状态：{i.get('status')}】"
							return False
						else:
							self.logger.info(f"当前航班参数有误【{i.get('status')}】")
							self.callback_msg = f"当前航班参数有误【{i.get('status')}】"
							return False
				
				self.verify_token2 = self.RCR.page_source.get("token")
				if self.verify_token2:
					if self.circle2():
						return True
					else:
						return False
			
			self.get_sun_proxy()
			return self.circle(count + 1, max_count)
	
	def circle2(self, count: int = 0, max_count: int = 10):
		if count >= max_count:
			return False
		else:
			# 对获取到的 token 进行 md5 加密
			token = self.CSR.token_md5(self.verify_token2, self.js_code)
			
			flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
			flight_date = flight_date.strftime('%Y-%m-%d')
			
			self.RCR.url = "https://availability-api.hkexpress.com/api/v1.0/availability/dayavailability"
			self.RCR.param_data = (
				("token", token), ("outboundDate", flight_date)
			)
			# self.RCR.header = self.BFR.format_to_same(self.init_header)
			# self.RCR.header.update({
			# 	"Accept": "*/*",
			# 	"Access-Control-Request-Method": "GET",
			# 	"Access-Control-Request-Headers": "apikey",
			# 	"Host": "availability-api.hkexpress.com",
			# 	"Origin": "https://booking.hkexpress.com",
			# 	"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
			# })
			# self.RCR.post_data = None
			# self.RCR.request_to_options()
			
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Host": "availability-api.hkexpress.com",
				"Origin": "https://booking.hkexpress.com",
				"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
				"ApiKey": self.availability_apikey
			})
			if self.RCR.request_to_get("json"):
				self.temp_source = self.RCR.page_source
				return True
			
			self.get_sun_proxy()
			return self.circle2(count + 1, max_count)
	
	def process_to_search(self, count: int = 0, max_count: int = 4) -> bool:
		"""Search process. 搜索过程。

		Args:
			count (int): 累计计数。
			max_count (int): 最大计数。

		Returns:
			bool
		"""
		if count >= max_count:
			return False
		else:
			self.get_sun_proxy()
			# 搜索航班
			self.RCR.url = "https://booking.hkexpress.com/zh-CN/agencies/booking/search/"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "booking.hkexpress.com",
				"Referer": "https://booking.hkexpress.com/zh-CN/agencies/agencybookings",
				"Upgrade-Insecure-Requests": "1"
			})
			if self.RCR.request_to_get():
				
				self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/session"
				self.RCR.param_data = None
				# self.RCR.header = self.BFR.format_to_same(self.init_header)
				# self.RCR.header.update({
				# 	"Accept": "*/*",
				# 	"Access-Control-Request-Method": "GET",
				# 	"Access-Control-Request-Headers": "apikey",
				# 	"Host": "booking-api.hkexpress.com",
				# 	"Origin": "https://booking.hkexpress.com",
				# 	"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
				# })
				# self.RCR.request_to_options()
				
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "application/json, text/plain, */*",
					"Host": "booking-api.hkexpress.com",
					"Origin": "https://booking.hkexpress.com",
					"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
					"ApiKey": self.api_key
				})
				if self.RCR.request_to_get("json"):
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/session"
					self.RCR.param_data = None
					# self.RCR.header = self.BFR.format_to_same(self.init_header)
					# self.RCR.header.update({
					# 	"Accept": "*/*",
					# 	"Access-Control-Request-Method": "DELETE",
					# 	"Access-Control-Request-Headers": "apikey,content-type",
					# 	"Host": "booking-api.hkexpress.com",
					# 	"Origin": "https://booking.hkexpress.com",
					# 	"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
					# })
					# self.RCR.request_to_options()
					
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Accept": "application/json, text/plain, */*",
						"Host": "booking-api.hkexpress.com",
						"Origin": "https://booking.hkexpress.com",
						"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
						"ApiKey": self.api_key
					})
					self.RCR.post_data = {}
					if self.RCR.request_to_delete("json", "json"):
						self.verify_token = self.RCR.page_source.get("token")
						if self.verify_token:
							
							self.RCR.url = "https://ancillaries-api.hkexpress.com/api/v1.0/insurance/clear"
							self.RCR.param_data = None
							# self.RCR.header = self.BFR.format_to_same(self.init_header)
							# self.RCR.header.update({
							# 	"Accept": "*/*",
							# 	"Access-Control-Request-Method": "DELETE",
							# 	"Access-Control-Request-Headers": "apikey,content-type",
							# 	"Host": "ancillaries-api.hkexpress.com",
							# 	"Origin": "https://booking.hkexpress.com",
							# 	"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
							# })
							# self.RCR.post_data = None
							# self.RCR.request_to_options()
							
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								"Accept": "application/json, text/plain, */*",
								"Host": "ancillaries-api.hkexpress.com",
								"Origin": "https://booking.hkexpress.com",
								"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
								"ApiKey": self.ancillaries_apikey
							})
							self.RCR.post_data = {}
							if self.RCR.request_to_delete("json", "json"):
								
								if not self.circle():
									return False
								else:
									flights, temp_html = self.BPR.parse_to_path('$..flights', self.temp_source)
									if not flights:
										self.logger.info("无航班")
										self.callback_msg = "无航班数据"
										return False
									
									is_flight = 0
									sellKey = ""
									fares = ""
									productClass = ""
									
									for i in flights:
										for x in i.get('segments'):
											if x.get('flightNumber') == self.CPR.flight_num:
												for y in i.get("fares"):
													sellKey = i.get('sellKey')
													fares = y.get('fareId')
													productClass = y.get('productClass')
													self.logger.info(f"匹配航班信息成功(*^__^*)【{self.CPR.flight_num}】")
													is_flight = 1
													break
									
									if not is_flight:
										self.logger.info(f"匹配不到航班信息(*>﹏<*)【{self.CPR.flight_num}】")
										self.callback_msg = f"匹配不到航班信息【{self.CPR.flight_num}】"
										return False
									
									self.RCR.url = "https://booking.hkexpress.com/zh-CN/agencies/booking/select/"
									self.RCR.param_data = None
									self.RCR.header = self.BFR.format_to_same(self.init_header)
									self.RCR.header.update({
										"Host": "booking.hkexpress.com",
										"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/search/",
										"Upgrade-Insecure-Requests": "1"
									})
									if self.RCR.request_to_get():
										# return True
										
										self.RCR.url = 'https://booking-api.hkexpress.com/api/v1.0/booking/flight'
										self.RCR.param_data = None
										self.RCR.header = self.BFR.format_to_same(self.init_header)
										self.RCR.header.update({
											"Accept": "application/json, text/plain, */*",
											"Content-Type": "application/json; charset=UTF-8",
											"Host": "booking-api.hkexpress.com",
											"Origin": "https://booking.hkexpress.com",
											"Referer": "https://booking.hkexpress.com/zh-CN/agencies/booking/select/",
											"apiKey": self.api_key
										})
										
										self.RCR.post_data = {
											"journeys": [{"departureStationCode": self.CPR.departure_code,
											              "arrivalStationCode": self.CPR.arrival_code,
											              "journeyId": sellKey.replace('^', '5E'),
											              "fareId": fares, "productClass": productClass}]}
										
										if self.RCR.request_to_post("json", "json"):
											
											self.RCR.url = 'https://booking.hkexpress.com/zh-CN/agencies/booking/detail/'
											self.RCR.header = self.BFR.format_to_same(self.init_header)
											self.RCR.header.update({
												"Host": "booking.hkexpress.com",
												'Upgrade-Insecure-Requests': '1',
												'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/select/',
											})
											if self.RCR.request_to_get():
												return True
			
			self.logger.info(f"查询第{count + 1}次超时或者错误(*>﹏<*)【query】")
			self.callback_msg = f"查询第{count + 1}次超时或者错误"
			
			self.get_sun_proxy()
			return self.process_to_search(count + 1, max_count)
	
	def process_to_passenger(self, count: int = 0, max_count: int = 4) -> bool:
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
			# 拼接乘客信息
			passengers = {}
			passengers_list = []
			#  男士 M, MR,  Male
			#  女士 F, MRS, Female
			#  男孩 MASTER
			#  女孩 MISS
			for i in self.CPR.adult_list:  # 拼接成人乘客参数
				# 乘客性别
				temp = {
					"firstName": i.get("first_name"),
					"lastName": i.get("last_name"),
					"dateOfBirth": self.DFR.format_to_transform(i.get("birthday"), "%Y%m%d").strftime(
						"%Y-%m-%dT%H:%M:%S"),
					"memberNumber": "",
				}
				if i.get("gender") == "M":
					temp['title'] = "MR"
				elif i.get("gender") == "F":
					temp['title'] = "MRS"
				passengers_list.append(temp)
			for i in self.CPR.child_list:  # 拼接儿童乘客信息
				temp = {
					"firstName": i.get("first_name"),
					"lastName": i.get("last_name"),
					"dateOfBirth": self.DFR.format_to_transform(i.get("birthday"), "%Y%m%d").strftime(
						"%Y-%m-%dT%H:%M:%S"),
					"memberNumber": "",
				}
				# 乘客性别
				if i.get("gender") == "M":
					temp['title'] = "MASTER"
				elif i.get("gender") == "F":
					temp['title'] = "MISS"
				passengers_list.append(temp)
			passengers['passengers'] = passengers_list
			self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/passenger"
			self.RCR.post_data = str(passengers)
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json; charset=UTF-8",
				"Host": "booking-api.hkexpress.com",
				"Origin": "https://booking.hkexpress.com",
				"apiKey": self.api_key,
				'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/detail/',
			})
			if self.RCR.request_to_post("data"):  # 提交乘客信息
				self.RCR.url = "https://booking.hkexpress.com/zh-CN/agencies/booking/ancillaries"
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Host": "booking.hkexpress.com",
					"Upgrade-Insecure-Requests": "1",
					'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/detail/',
				})
				if self.RCR.request_to_get():
					return True
			
			self.logger.info(f"乘客第{count + 1}次超时或者错误(*>﹏<*)【query】")
			self.callback_msg = f"乘客第{count + 1}次超时或者错误"
			
			self.get_sun_proxy()
			return self.process_to_passenger(count + 1, max_count)
	
	def process_to_service(self, count: int = 0, max_count: int = 4) -> bool:
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
			# # # 请求行李页面
			self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/DefaultAncillariesSelector"
			self.RCR.post_data = '{"headers":{"normalizedNames":{},"lazyUpdate":null,"lazyInit":null,"headers":{}}}'
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json",
				"Host": "booking-api.hkexpress.com",
				"Origin": "https://booking.hkexpress.com",
				"apiKey": self.api_key,
				'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/ancillaries',
			})
			if self.RCR.request_to_post("data"):
				self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/availableAncillaries?AncillaryTypes=Meal,Baggage,Oversize,Priority"
				self.RCR.post_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "application/json, text/plain, */*",
					"Content-Type": "application/json; charset=UTF-8",
					"Host": "booking-api.hkexpress.com",
					"Origin": "https://booking.hkexpress.com",
					"apiKey": self.api_key,
					"Upgrade-Insecure-Requests": "1",
					'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/ancillaries',
				})
				if self.RCR.request_to_get():
					# 获取行李信息
					html = self.BPR.parse_to_dict(self.RCR.page_source).get('ancillaries')
					temp = []  # 行李参数
					# 乘客总人数
					nums = [i for i in range(len(self.CPR.adult_list) + len(self.CPR.child_list))]
					
					# 添加行李服务
					for i in self.CPR.adult_list:  # 遍历成人乘客信息， 是否有行李服务
						for h in html:  # 遍历网站提供的附加服务信息
							if h.get('type') == 'Baggage':  # 判断服务是否是行李服务
								if not i.get('baggage'):
									continue
								
								# # # 判断接口给的行李重量， 是否在网站提供的行李数据中
								if str(i.get('baggage')[0]['weight']) in h.get('code'):
									accessorial_server = {}
									for a in h.get('availability'):
										ssr_codes = []
										passenger = []
										ssr_codes.append(
											{
												"code": h.get('code'),
												"unit": '1'
											}
										)
										passenger.append({
											"passengerNumber": self.CPR.adult_list.index(i),
											"ssrCodes": ssr_codes
										}
										)
										accessorial_server['ancillaries'] = [
											{
												"sellkey": a.get('sellKey'),
												"passengers": passenger
											}
										]
									temp.append(accessorial_server)
								# self.logger.info(accessorial_server)
								else:
									continue
							
							else:
								continue
					
					for i in self.CPR.child_list:  # 遍历儿童乘客信息， 是否有行李服务
						for h in html:  # 遍历网站提供的附加服务信息
							if h.get('type') == 'Baggage':  # 判断服务是否是行李服务
								if not i.get('baggage'):
									continue
								
								# # # 判断接口给的行李重量， 是否在网站提供的行李数据中
								if str(i.get('baggage')[0]['weight']) in h.get('code'):
									accessorial_server = {}
									for a in h.get('availability'):
										ssr_codes = []
										passenger = []
										ssr_codes.append(
											{
												"code": h.get('code'),
												"unit": '1'
											}
										)
										passenger.append({
											"passengerNumber": self.CPR.child_list.index(i),
											"ssrCodes": ssr_codes
										}
										)
										accessorial_server['ancillaries'] = [
											{
												"sellkey": a.get('sellKey'),
												"passengers": passenger
											}
										]
									temp.append(accessorial_server)
							else:
								continue
					# self.logger.info(temp)
					# time.sleep(100000)
					
					if temp:
						# 提交行李信息
						for data in temp:
							# self.logger.info(data)
							self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/ancillary"
							self.RCR.post_data = str(data)
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								"Accept": "application/json, text/plain, */*",
								"Content-Type": "application/json; charset=UTF-8",
								"Host": "booking-api.hkexpress.com",
								"Origin": "https://booking.hkexpress.com",
								"apiKey": self.api_key,
								'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/ancillaries',
							})
							if self.RCR.request_to_post("data"):
								continue
							else:
								self.logger.info(f"添加行李失败 (*>﹏<*)【{data}】")
								self.callback_msg = "添加行李失败"
								return False
					
					# 座位
					self.RCR.url = "https://booking.hkexpress.com/zh-CN/agencies/booking/seat"
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Content-Type": "application/json; charset=UTF-8",
						"Host": "booking.hkexpress.com",
						"Origin": "https://booking.hkexpress.com",
						"apiKey": self.api_key,
						"Upgrade-Insecure-Requests": "1",
						'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/ancillaries',
					})
					if self.RCR.request_to_get():
						self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/session"
						self.RCR.param_data = None
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							'Accept': 'application/json, text/plain, */*',
							'Referer': 'https://booking.hkexpress.com/zh-HK/agencies/booking/seat',
							'Origin': 'https://booking.hkexpress.com',
							'Sec-Fetch-Mode': 'cors',
							"Content-Type": "application/json",
							"Host": "booking-api.hkexpress.com",
							"apiKey": self.api_key
						})
						if self.RCR.request_to_get():
							self.segmentId, temp_html = self.BPR.parse_to_path(path_syntax='$..segmentId',
							                                                   source_data=json.loads(
								                                                   self.RCR.page_source))
							if self.segmentId:
								self.RCR.url = f"https://booking-api.hkexpress.com/api/v1.0/booking/seatmap?segmentId={self.segmentId}"
								self.logger.info(self.RCR.url)
								self.RCR.post_data = None
								self.RCR.header = self.BFR.format_to_same(self.init_header)
								self.RCR.header.update({
									"Accept": "application/json, text/plain, */*",
									"Content-Type": "application/json; charset=UTF-8",
									"Host": "booking-api.hkexpress.com",
									"Origin": "https://booking.hkexpress.com",
									"apiKey": self.api_key,
									'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/seat',
								})
								if self.RCR.request_to_get():
									return True
			
			self.logger.info(f"行李第{count + 1}次超时或者错误(*>﹏<*)【query】")
			self.callback_msg = f"行李第{count + 1}次超时或者错误"
			
			self.get_sun_proxy()
			return self.process_to_service(count + 1, max_count)
	
	def process_to_payment(self, count: int = 0, max_count: int = 4) -> bool:
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
			self.RCR.url = "https://booking.hkexpress.com/zh-CN/agencies/booking/payment"
			self.RCR.post_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "booking.hkexpress.com",
				"Upgrade-Insecure-Requests": "1",
				'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/seat',
			})
			if self.RCR.request_to_get():
				self.RCR.url = "https://booking.hkexpress.com/umbraco/api/PagePropertyValuesApi/GetPropertyValue/?url=/zh-CN/agencies/booking/payment&propertyName=hideCurrencyTopMenuTab"
				self.RCR.post_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "application/json, text/plain, */*",
					"Host": "booking.hkexpress.com",
					"Content-Type": "application/json; charset=utf-8",
					'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/payment',
				})
				if self.RCR.request_to_get():
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/available?currencyCode="
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Accept": "application/json, text/plain, */*",
						"Host": "booking-api.hkexpress.com",
						"Content-Type": "application/json; charset=utf-8",
						'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/payment',
						"Origin": "https://booking.hkexpress.com",
						"apiKey": self.api_key,
					})
					if self.RCR.request_to_get():
						self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/agencycredit"
						self.RCR.post_data = None
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							"Accept": "application/json, text/plain, */*",
							"Host": "booking-api.hkexpress.com",
							"Content-Type": "application/json; charset=utf-8",
							'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/payment',
							"Origin": "https://booking.hkexpress.com",
							"apiKey": self.api_key,
						})
						if self.RCR.request_to_get():
							# 提交联系人信息
							self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/contact"
							self.RCR.post_data = '{"title":"MR","firstName":"%s","lastName":"%s","cultureCode":"zh-CN","email":"%s","phone":"%s","sendSMSItinerary":false,"phoneCountryPreffix":"86","newsletter":false,"address":{"address1":"","cityCode":"","countryCode":"CN","zipCode":""},"rememberData":true}' % (
								self.CPR.contact_first, self.CPR.contact_last, self.CPR.contact_email,
								self.CPR.contact_mobile,
							)
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								"Accept": "application/json, text/plain, */*",
								"Content-Type": "application/json; charset=UTF-8",
								"Host": "booking-api.hkexpress.com",
								"Origin": "https://booking.hkexpress.com",
								"apiKey": self.api_key,
								'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/payment',
							})
							if self.RCR.request_to_post("data"):
								# 取消付款
								self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/cancelinprocesspayment"
								self.RCR.post_data = None
								self.RCR.header = self.BFR.format_to_same(self.init_header)
								self.RCR.header.update({
									"Accept": "application/json, text/plain, */*",
									"Host": "booking-api.hkexpress.com",
									"Origin": "https://booking.hkexpress.com",
									"Upgrade-Insecure-Requests": "1",
									"apiKey": self.api_key,
									'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/payment',
								})
								if self.RCR.request_to_delete():
									# 订单暂停支付
									self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/onhold"
									self.RCR.post_data = ''
									self.RCR.header = self.BFR.format_to_same(self.init_header)
									self.RCR.header.update({
										"Accept": "application/json, text/plain, */*",
										"Content-Type": "application/json; charset=UTF-8",
										"Host": "booking-api.hkexpress.com",
										"Origin": "https://booking.hkexpress.com",
										"apiKey": self.api_key,
										'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/payment',
									})
									if self.RCR.request_to_post():
										self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking"
										self.RCR.post_data = None
										self.RCR.header = self.BFR.format_to_same(self.init_header)
										self.RCR.header.update({
											"Accept": "application/json, text/plain, */*",
											"Content-Type": "application/json; charset=UTF-8",
											"Host": "booking-api.hkexpress.com",
											"Origin": "https://booking.hkexpress.com",
											"apiKey": self.api_key,
											'Referer': 'https://booking.hkexpress.com/zh-CN/agencies/booking/payment',
											"Accept-Language": "zh-CN,zh;q=0.9"
										})
										if self.RCR.request_to_post('json', 'json'):
											# pnr
											self.record, temp_fee = self.BPR.parse_to_path('$...recordLocator',
											                                               self.RCR.page_source)
											if not self.record:
												self.logger.info("获取PNR失败")
												self.callback_msg = "获取PNR失败"
												return False
											else:
												# pnr 超时时间
												self.pnr_timeout = self.DFR.format_to_now(custom_hours=6)
												self.pnr_timeout = self.pnr_timeout.strftime("%Y-%m-%d %H:%M:%S")
												# 货币
												self.CPR.currency, temp_fee = self.BPR.parse_to_path('$...currency',
												                                                     self.RCR.page_source)
												# 总价
												self.total_price, temp_fee = self.BPR.parse_to_path('$...totalAmount',
												                                                    self.RCR.page_source)
												
												# 票价
												self.fare_price, fare_price_list = self.BPR.parse_to_path(
													'$...farePrice',
													self.RCR.page_source)
												# 行李总价
												baggage_price, baggage_price_list = self.BPR.parse_to_path(
													'$.bookingFees..[?("ServiceCharge")].amount', self.RCR.page_source)
												if baggage_price_list:
													for i in baggage_price_list:
														if i > 0:
															self.baggage_price = self.baggage_price + i
												else:
													self.baggage_price = -1
												return True
			
			self.logger.info(f"占仓第{count + 1}次超时或者错误(*>﹏<*)【query】")
			self.callback_msg = f"占仓第{count + 1}次超时或者错误"
			
			self.get_sun_proxy()
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
			# # 根据 PNR 获取订单
			self.RCR.url = "https://booking.hkexpress.com/zh-HK/agencies/agencybookings"
			self.RCR.param_data = None
			self.RCR.post_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				'Host': 'booking.hkexpress.com',
				'Upgrade-Insecure-Requests': '1',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				'Origin': 'https://www.ryanair.com',
				'Referer': self.RCR.response_url,
			})
			if not self.RCR.request_to_get(is_redirect=True):
				self.logger.info(f"跳转订单页面失败 | {self.RCR.url}")
				self.callback_msg = f"跳转订单页面失败"
				return False
			else:
				self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/MemberBooking"
				self.RCR.param_data = (
					('beginDate',
					 self.DFR.format_to_custom(source_time=self.DFR.format_to_now(), custom_days=-1).strftime(
						 '%Y-%m-%d')),
					('endDate', self.DFR.format_to_custom(source_time=self.DFR.format_to_now(), custom_days=1).strftime(
						'%Y-%m-%d')),
				)
				self.RCR.post_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "application/json, text/plain, */*",
					"Host": "booking-api.hkexpress.com",
					"Referer": "https://booking.hkexpress.com/zh-HK/agencies/agencybookings",
					"Origin": 'https://booking.hkexpress.com',
					"apiKey": self.api_key,
				})
				if self.RCR.request_to_get(is_redirect=True, page_type='json'):
					# 判断返回是否成功，如果不成功重试一次
					response_status, temp_list = self.BPR.parse_to_path('$.success', self.RCR.page_source)
					if not response_status:
						self.logger.info(f"获取指定日期内的 PNR 失败 {self.RCR.param_data}")
						self.callback_msg = f"获取指定日期内的 PNR 失败 {self.RCR.param_data}"
						return False
					
					flightInfo, flightInfo_list = self.BPR.parse_to_path('$.flightInfoByCustomerResponses',
					                                                     self.RCR.page_source)
					if not flightInfo:
						self.logger.info(f"未查到订单可能已经飞走{flightInfo_list}")
						self.callback_msg = f"未查到订单可能已经飞走{flightInfo_list}"
						return False
					
					last_name = ''  # 乘客姓氏  lastname
					for i in self.CPR.adult_list:  # 遍历成人乘客信息
						last_name = i.get('last_name')
						break
					
					self.RCR.url = f"https://booking-api.hkexpress.com/api/v1.0/booking/ManageBookingLogin?recordLocator={self.CPR.pnr_code}&lastName={last_name}"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header.update({
						"Accept": "application/json, text/plain, */*",
						"Host": "booking-api.hkexpress.com",
						"Referer": "https://booking.hkexpress.com/zh-HK/agencies/agencybookings",
						"Origin": 'https://booking.hkexpress.com',
						"apiKey": self.api_key,
					})
					if not self.RCR.request_to_get('json'):
						self.logger.info(f"待支付票号获取失败")
						self.callback_msg = f"待支付票号获取失败"
						return False
					# 票号信息异常~~~
					response_status, temp_list = self.BPR.parse_to_path('$.success', self.RCR.page_source)
					error, error_list = self.BPR.parse_to_path('$.errors', self.RCR.page_source)
					if response_status == False:
						self.logger.info(f"票号信息获取失败 {self.CPR.pnr_code} | Error: {error}")
						self.callback_msg = f"票号信息获取失败 {self.CPR.pnr_code} | Error: {error}"
						return False
					
					order_status, temp_list = self.BPR.parse_to_path('$..status', self.RCR.page_source)
					if order_status == "Confirmed":
						self.logger.info(f"票号状态：{order_status}， 已经支付完成，{self.CPR.pnr_code} 出票失败 ")
						self.callback_msg = f"票号状态：{order_status}， 已经支付完成，{self.CPR.pnr_code} 出票失败 "
						return False
					
					# 航司货币
					self.CPR.currency, temp_list = self.BPR.parse_to_path('$..bookingInfo.currency',
					                                                      self.RCR.page_source)
					if not self.CPR.currency:
						self.logger.info(f"货币提取失败： {self.CPR.pnr_code} {self.RCR.page_source} 出票失败 ")
						self.callback_msg = f"货币提取失败：{self.CPR.pnr_code} 出票失败"
						return False
					
					# 总价
					self.total_price, temp_list = self.BPR.parse_to_path('$..totalAmount',
					                                                     self.RCR.page_source)
					if not self.total_price:
						self.logger.info(f"当前票号总价提取失败： {self.CPR.pnr_code} 出票失败 ")
						self.callback_msg = f"当前票号总价提取失败：{self.CPR.pnr_code} 出票失败"
						return False
					
					# 除了行李的所有价格
					self.return_price, temp_list = self.BPR.parse_to_path('$...totalPrice',
					                                                      self.RCR.page_source)
					
					# # 行李总价
					baggage_price, baggage_price_list = self.BPR.parse_to_path(
						'$..bookingFees', self.RCR.page_source)
					
					for n, i in enumerate(self.CPR.adult_list):  # 遍历成人乘客信息
						if not i.get('baggage'):  # 判断 是否有行李服务
							continue
						for h in baggage_price:  # 遍历网站提供的附加服务信息
							for x in i.get('baggage'):
								if str(x.get('weight')) in h.get('feeCode') and n == h.get(
										'passengerNumber'):  # 判断服务是否是行李服务
									for m in h.get('charges'):
										x['price'] = m.get('foreignAmount')
										self.CPR.return_baggage.append(x)
					
					for n, i in enumerate(self.CPR.child_list):  # 遍历儿童乘客信息
						if not i.get('baggage'):  # 判断 是否有行李服务
							continue
						for h in baggage_price:  # 遍历网站提供的附加服务信息
							for x in i.get('baggage'):
								if str(x.get('weight')) in h.get('feeCode') and n == h.get(
										'passengerNumber'):  # 判断服务是否是行李服务
									for m in h.get('charges'):
										x['price'] = m.get('foreignAmount')
										self.CPR.return_baggage.append(x)
					
					# # # # 进行比价
					if self.process_to_compare() == False:
						return False
					
					# time.sleep(1000)
					self.RCR.url = "https://booking.hkexpress.com/zh-HK/manage/payment"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking.hkexpress.com',
						'Upgrade-Insecure-Requests': '1',
						'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
						'Referer': 'https://booking.hkexpress.com/zh-HK/agencies/agencybookings',
					})
					if not self.RCR.request_to_get(is_redirect=True):
						self.logger.info(f"支付页面获取失败")
						self.callback_msg = f"支付页面获取失败"
						return False
					
					# time.sleep(10000)
					###### 进行支付 ######
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/session"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Accept': 'application/json, text/plain, */*',
						"apiKey": self.api_key,
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
					})
					if not self.RCR.request_to_get(page_type='json'):
						return False
					
					# 获取货币
					self.RCR.url = f"https://booking-api.hkexpress.com/api/v1.0/resources/mcpcurrency?currencyCode={self.CPR.currency}"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Accept': 'application/json, text/plain, */*',
						'apiKey': self.api_key,
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
						'Origin': 'https://booking.hkexpress.com',
					})
					if not self.RCR.request_to_get(page_type='json'):
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/available?currencyCode="
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Accept': 'application/json, text/plain, */*',
						'Origin': 'https://booking.hkexpress.com',
						'apiKey': self.api_key,
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
					})
					if not self.RCR.request_to_get():
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/agencycredit"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Origin': 'https://www.ryanair.com',
						'Accept': 'application/json, text/plain, */*',
						'apiKey': self.api_key,
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
					})
					if not self.RCR.request_to_get():
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/cancelinprocesspayment"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Origin': 'https://booking.hkexpress.com',
						'Access-Control-Request-Method': 'DELETE',
						'Access-Control-Request-Headers': 'apikey',
						'Accept': '*/*',
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
					})
					if not self.RCR.request_to_options():
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/cancelinprocesspayment"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Accept': 'application/json, text/plain, */*',
						'Origin': 'https://booking.hkexpress.com',
						'apiKey': self.api_key,
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
					})
					if not self.RCR.request_to_delete():
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/payment/agencycredit"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Accept': 'application/json, text/plain, */*',
						'Origin': 'https://booking.hkexpress.com',
						'apiKey': self.api_key,
						'Content-Type': 'application/json; charset=UTF-8',
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
					})
					if not self.RCR.request_to_post():
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Accept': 'application/json, text/plain, */*',
						'Origin': 'https://booking.hkexpress.com',
						'apiKey': self.api_key,
						'Content-Type': 'application/json; charset=UTF-8',
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
					})
					if not self.RCR.request_to_post():
						return False
					
					self.RCR.url = "https://booking.hkexpress.com/zh-HK/manage/itinerary/"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking.hkexpress.com',
						'Upgrade-Insecure-Requests': '1',
						'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/payment',
					})
					if not self.RCR.request_to_get():
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/agent"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Accept': 'application/json, text/plain, */*',
						'apiKey': self.api_key,
						'Origin': 'https://booking.hkexpress.com',
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/itinerary/',
					})
					if not self.RCR.request_to_get():
						return False
					
					self.RCR.url = "https://booking-api.hkexpress.com/api/v1.0/booking/refresh?pageRequest=itinerary"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'booking-api.hkexpress.com',
						'Accept': 'application/json, text/plain, */*',
						'apiKey': self.api_key,
						'Origin': 'https://booking.hkexpress.com',
						'Content-Type': 'application/json; charset=utf-8',
						'Referer': 'https://booking.hkexpress.com/zh-HK/manage/itinerary/',
					})
					if not self.RCR.request_to_get(page_type='json'):
						return False
					
					# # 除了行李的所有价格
					self.return_price, temp_list = self.BPR.parse_to_path('$...totalPrice',
					                                                      self.RCR.page_source)
					
					return True
	
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
		               f"foreignCurrency={self.CPR.currency}&carrier=UO"
		self.RCR.param_data = None
		self.RCR.header = self.BFR.format_to_same(self.init_header)
		self.RCR.post_data = None
		if self.RCR.request_to_get("json"):
			# errot = self.RCR.page_source.get(self.CPR.currency)
			# # # 解析汇率转换人民币价格。
			exchange = self.RCR.page_source.get(self.CPR.currency)
			if not exchange:
				self.logger.info(f"转换汇率价格失败(*>﹏<*)【{self.RCR.page_source}】")
				self.callback_msg = "转换汇率价格失败，请通知技术检查程序。"
				return False
			exchange_price = self.BFR.format_to_float(2, self.total_price * exchange)  # 总价
			# # # 进行接口比价。
			target_price = self.BFR.format_to_float(2, self.CPR.target_price)  # 目标价格
			diff_price = self.BFR.format_to_float(2, self.CPR.diff_price)  # 查价
			target_total = self.BFR.format_to_float(2, target_price + diff_price)
			if exchange_price > target_total:
				self.logger.info(f"出票价格过高(*>﹏<*)【{target_total}】【{exchange_price}】")
				self.callback_msg = f"出票价格上限为{target_total}元。出票失败，出票价格过高， {exchange_price}元。"
				return False
			return True
		
		# # # 错误重试。
		self.logger.info(f"查询汇率接口第{count + 1}次超时(*>﹏<*)【compare】")
		self.callback_msg = f"查询汇率接口第{count + 1}次超时，请重试。"
		return self.process_to_compare(count + 1, max_count)
	
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