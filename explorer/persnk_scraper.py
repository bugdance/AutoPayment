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


class PersNKScraper(RequestWorker):
	"""NK采集器，NK网站流程交互，需要登录账号，需要国外特殊机器。"""
	
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
		# # # 过程中重要的参数。
		self.verify_token: str = ""  # 认证token。
		self.verify_key: str = "d915d5442ee6427bb58e33dd93e253b8"  # 认证key。
		self.journey_key: str = ""  # 行程key。
		self.customer: str = ""  # 用户ID。
		self.passenger_key: list = []  # 乘客key。
		self.promo_success: bool = False  # 优惠码是否有效。
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
		self.CPR.currency = "USD"
		# # # 主体流程。
		if self.process_to_login(max_count=self.retry_count):
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
	
	def process_to_login(self, count: int = 0, max_count: int = 1) -> bool:
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
			# # # 生成header，获取首页，地址https://www.spirit.com打不开。
			self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/v1/token"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json",
				"Host": "api.spirit.com",
				"Origin": "https://www.spirit.com",
				"Referer": "https://www.spirit.com/",
				"Ocp-Apim-Subscription-Key": self.verify_key,
			})
			# # # 基础参数。
			self.RCR.post_data = {"applicationName":"dotRezWeb"}
			if self.RCR.request_to_post("json", "json", 201):
				# # # 查询认证参数。
				self.verify_token, temp_list = self.BPR.parse_to_path("$.data.token", self.RCR.page_source)
				if not self.verify_token:
					self.logger.info(f"获取认证值失败(*>﹏<*)【{self.RCR.page_source}】")
					self.callback_msg = "获取认证值失败。"
					return False
				password = self.AFR.decrypt_into_aes(
					self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.password)
				if not password:
					self.logger.info(f"解密账号密码失败(*>﹏<*)【{self.CPR.password}】")
					self.callback_msg = "解密账号密码失败，请通知技术检查程序。"
					return False
				# # # 继承header，登录。
				self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/token"
				self.RCR.header.update({"Authorization": f"Bearer {self.verify_token}"})
				self.RCR.post_data = {
					"credentials": {
						"username": self.CPR.username, "password": password, "domain": "WWW",
					                "applicationName": "dotRezWeb"
					},
					"replacePrimaryPassenger": False
				}
				if self.RCR.request_to_put("json", "json", 201):
					# # # 查询错误信息。
					error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
					if error:
						self.logger.info(f"请求登录失败(*>﹏<*)【{error}】")
						self.callback_msg = f"请求登录失败【{error}】。"
						return False
					# # # 继承header，查询登录后结果。
					self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/v1/user/person"
					self.RCR.post_data = None
					if self.RCR.request_to_get("json"):
						self.customer, temp_list = self.BPR.parse_to_path("$.data.customerNumber", self.RCR.page_source)
						if not self.customer:
							self.logger.info(f"登录失败(*>﹏<*)【{self.RCR.page_source}】")
							self.callback_msg = "登录失败。"
							return False
						# # # 安全通过。
						return True
			# # # 错误重试。
			self.logger.info(f"请求登录第{count + 1}次超时(*>﹏<*)【login】")
			self.callback_msg = f"请求登录第{count + 1}次超时，请重试"
			return self.process_to_login(count + 1, max_count)
	
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
			# # # 转换接口日期和优惠码日期。
			flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
			promo_date = self.DFR.format_to_custom(flight_date, custom_hours=-8)
			# # # 生成header, 查询航班。
			self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/promotions/validate"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json",
				"Host": "api.spirit.com",
				"Origin": "https://www.spirit.com",
				"Referer": "https://www.spirit.com/",
				"Ocp-Apim-Subscription-Key": self.verify_key,
				"Authorization": f"Bearer {self.verify_token}",
			})
			self.RCR.post_data = {"promoCode": self.CPR.promo, "originStationCode": self.CPR.departure_code,
			                      "destinationStationCode": self.CPR.arrival_code,
			                      "dates":[promo_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")]}
			if self.RCR.request_to_post("json", "json"):
				print(self.RCR.page_source)
				# # # 查询优惠码。
				self.promo_success, temp_list = self.BPR.parse_to_path("$.data", self.RCR.page_source)
				# # # 生成header, 查询航班。
				self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/availability/search"
				self.RCR.param_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "application/json, text/plain, */*",
					"Content-Type": "application/json",
					"Host": "api.spirit.com",
					"Origin": "https://www.spirit.com",
					"Referer": "https://www.spirit.com/",
					"Ocp-Apim-Subscription-Key": self.verify_key,
					"Authorization": f"Bearer {self.verify_token}",
				})
				types = [{"type": "ADT", "count": self.CPR.adult_num}]
				if self.CPR.child_num:
					types.append({"type": "CHD", "count": self.CPR.child_num})
					
				codes = {"currency": self.CPR.currency}
				if self.promo_success:
					codes["promotionCode"] = self.CPR.promo
	
				self.RCR.post_data = {
					"criteria": [
						{"stations": {
							"originStationCodes": [self.CPR.departure_code],
							"destinationStationCodes": [self.CPR.arrival_code],
							"searchDestinationMacs": True, "searchOriginMacs": True},
						"dates": {"beginDate": flight_date.strftime("%Y-%m-%d"),
						          "endDate": flight_date.strftime("%Y-%m-%d")}
						}],
					"passengers": {"types": types}, "codes": codes,
					"fareFilters": {}, "taxesAndFees": "TaxesAndFees"," originalJourneyKeys": [],
					"originalBookingRecordLocator": None, "infantCount": 0, "birthDates": []
				}
				if self.RCR.request_to_post("json", "json"):
					# # # 查询错误信息。
					error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
					if error:
						self.logger.info(f"提交查询失败(*>﹏<*)【{error}】")
						self.callback_msg = f"提交查询失败【{error}】。"
						return False
	
					table, temp_list = self.BPR.parse_to_path("$.data.trips[0].journeysAvailable", self.RCR.page_source)
					if not table:
						self.logger.info(f"匹配不到航班信息(*>﹏<*)【{self.CPR.flight_num}】")
						self.callback_msg = "该航线航班已售完。"
						return False
					# # # 解析接口航班号。
					interface_carrier = self.CPR.flight_num[:2]
					interface_no = self.CPR.flight_num[2:]
					interface_no = self.BFR.format_to_int(interface_no)
					# # # 匹配接口航班。
					is_flight = False  # 是否匹配到航班。
					fare_Key = ""
					fare_amount = ""
					for i in table:
						segments, temp_list = self.BPR.parse_to_path("$.segments", i)
						if not segments and len(segments) != 1:
							continue
						# # # 解析网页航班号。
						source_carrier, temp_list = self.BPR.parse_to_path("$.[0].identifier.carrierCode", segments)
						source_carrier = self.BPR.parse_to_clear(source_carrier)
						source_no, temp_list = self.BPR.parse_to_path("$.[0].identifier.identifier", segments)
						source_no = self.BFR.format_to_int(source_no)
						# # # 匹配航班号。
						if interface_carrier == source_carrier and interface_no == source_no:
							is_flight = True
							fares, fares_list = self.BPR.parse_to_path("$.fares", i)
							for j in fares_list:
								for k, v in j.items():
									# # # 非俱乐部价格。
									is_club, temp_list = self.BPR.parse_to_path("$.details.isClubFare", v)
									if is_club:
										continue
									else:
										print(v)
										fare_Key = k
										fare_amount, temp_list = self.BPR.parse_to_path(
											"$.details.passengerFares[0].fareAmount", v)
	
								self.journey_key, temp_list = self.BPR.parse_to_path("$.journeyKey", i)
							break
					print(fare_amount)
					# # # 没有找到航班号码。
					if not is_flight:
						self.logger.info(f"查找对应航班号失败(*>﹏<*)【{self.CPR.flight_num}】")
						self.callback_msg = f"查找对应航班号失败【{self.CPR.flight_num}】，请核实。"
						return False
					# # # 继承header, 提交查询。
					self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/trip/sell"
					self.RCR.post_data = {
						"preventOverlap": True,
						"keys":[{
							"journeyKey": self.journey_key,
							"fareAvailabilityKey": fare_Key,
							"standardKey": fare_Key, "standardFareAmount": fare_amount,
							"clubFareAmount": 0
						}],
						"suppressPassengerAgeValidation": True,
						"passengers":{"types": types},
						"currencyCode": self.CPR.currency, "infantCount": 0,
					}
					# # # 优惠码
					if self.promo_success:
						self.RCR.post_data['promotionCode'] = self.CPR.promo
					if self.RCR.request_to_post("json", "json"):
						# # # 查询错误信息。
						error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
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
			# # # 获取乘客key。
			passenger_dict, temp_list = self.BPR.parse_to_path("$.data.passengers", self.RCR.copy_source)
			for k, v in passenger_dict.items():
				self.passenger_key.append(k)
			# # # 生成header, 添加乘客信息。
			self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/passengers"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json",
				"Host": "api.spirit.com",
				"Origin": "https://www.spirit.com",
				"Referer": "https://www.spirit.com/book/passenger",
				"Ocp-Apim-Subscription-Key": self.verify_key,
				"Authorization": f"Bearer {self.verify_token}",
			})
			passengers = []
			birth_time = self.DFR.format_to_now(True, custom_hours=-1)
			birth_time = birth_time.strftime("%H:%M:%S.000Z")
			# # # 追加每个成人具体的参数。
			for n, v in enumerate(self.CPR.adult_list):
				sex = "MR"
				gender = "Male"
				if v.get("gender") == "F":
					sex = "MS"
					gender = "Female"
				last_name = v.get("last_name")
				last_name = self.BPR.parse_to_clear(last_name)
				first_name = v.get("first_name")
				first_name = self.BPR.parse_to_separate(first_name)
				
				birthday = self.DFR.format_to_transform(v.get("birthday"), "%Y%m%d")
				birthday = birthday.strftime("%Y-%m-%dT")
				birthday += birth_time
				
				adult_batch = {
					"passengerKey": self.passenger_key[n], "passengerAlternateKey": None, "fees": [],
					 "name":{
						"title": sex, "first": first_name, "middle": None, "last": last_name, "suffix": None
					 },
					 "passengerTypeCode": "ADT", "discountCode": "", "bags": [], "infant": None,
					 "info": {"nationality": "", "residentCountry": "US", "gender": gender,
					          "dateOfBirth": birthday, "familyNumber": 0},
					 "travelDocuments": [], "addresses": [], "weightCategory": 1}
				# # # 追加每个成人具体的参数。
				passengers.append(adult_batch)
			# # # 追加每个儿童具体的参数。
			if self.CPR.child_num:
				for n, v in enumerate(self.CPR.child_list):
					n += self.CPR.adult_num
					
					sex = "MR"
					gender = "Male"
					if v.get("gender") == "F":
						sex = "MS"
						gender = "Female"
					last_name = v.get("last_name")
					last_name = self.BPR.parse_to_clear(last_name)
					first_name = v.get("first_name")
					first_name = self.BPR.parse_to_separate(first_name)
					
					birthday = self.DFR.format_to_transform(v.get("birthday"), "%Y%m%d")
					birthday = birthday.strftime("%Y-%m-%dT")
					birthday += birth_time
					
					child_batch = {
						"passengerKey": self.passenger_key[n], "passengerAlternateKey": None, "fees": [],
						"name": {
							"title": sex, "first": first_name, "middle": None, "last": last_name, "suffix": None
						},
						"passengerTypeCode": "CHD", "discountCode": "", "bags": [], "infant": None,
						"info": {"nationality": "", "residentCountry": "US", "gender": gender,
						         "dateOfBirth": birthday, "familyNumber": 0},
						"travelDocuments": [], "addresses": [], "weightCategory": 1}
					# # # 追加每个成人具体的参数。
					passengers.append(child_batch)
			# # # 生成请求参数。
			self.RCR.post_data = {
				"hasPassword": False, "password":"",
				"passengers": passengers,
				"contact":{
					"name": {"title": None, "first": self.CPR.contact_first,
					         "middle": None, "last": self.CPR.contact_last,
					         "suffix": None},
					"address": {"lineOne": "BEIJINGHAIDIAN", "countryCode": "CN",
					            "provinceState": "NA", "city": "BEIJING", "postalCode":"100000"},
					"homePhone": f"86{self.CPR.contact_mobile}",
					"emailAddress": self.CPR.contact_email,
					"dateOfBirth": "1976-12-22T"+birth_time,
					"customerNumber": self.customer
				}
			}
			if self.RCR.request_to_put("json", "json"):
				# # # 查询错误信息。
				error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
				if error:
					self.logger.info(f"添加乘客失败(*>﹏<*)【{error}】")
					self.callback_msg = f"添加乘客失败【{error}】。"
					return False
				# # # 安全通过。
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
			self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/booking/bags"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json",
				"Host": "api.spirit.com",
				"Origin": "https://www.spirit.com",
				"Referer": "https://www.spirit.com/book/bags",
				"Ocp-Apim-Subscription-Key": self.verify_key,
				"Authorization": f"Bearer {self.verify_token}",
			})
			baggages = {}  # 行李信息。
			# # # 追加每个成人具体的参数。
			for n, v in enumerate(self.CPR.adult_list):
				# # # 判断行李并累计公斤数。
				single_baggage = []
				weight = v.get('baggage')
				kilogram = 0
				if weight:
					for w in weight:
						kilogram += self.BFR.format_to_int(w.get('weight'))
				# # # 解析行李参数，只有件数，没有公斤数，1件按18算。
				if kilogram:
					if kilogram % 18 != 0:
						self.logger.info(f"公斤数不是18的倍数(*>﹏<*)【{n}】【{v}】")
						self.callback_msg = "匹配行李失败"
						return False
					# # # 最多不能超过5件。
					weight = self.BFR.format_to_int(kilogram / 18)
					if weight > 5:
						self.logger.info(f"公斤数大于5件(*>﹏<*)【{n}】【{v}】")
						self.callback_msg = "匹配行李失败"
						return False
					for i in range(weight):
						single_baggage.append({"ssrCode": f"BAG{i+1}", "count": 1})
				# # # 追加每个成人具体的参数。
				baggages[self.passenger_key[n]] = single_baggage
			# # # 追加每个儿童具体的参数。
			if self.CPR.child_num:
				for n, v in enumerate(self.CPR.child_list):
					n += self.CPR.adult_num
					# # # 判断行李并累计公斤数。
					single_baggage = []
					weight = v.get('baggage')
					kilogram = 0
					if weight:
						for w in weight:
							kilogram += self.BFR.format_to_int(w.get('weight'))
					# # # 解析行李参数，只有件数，没有公斤数，1件按18算。
					if kilogram:
						if kilogram % 18 != 0:
							self.logger.info(f"公斤数不是18的倍数(*>﹏<*)【{n}】【{v}】")
							self.callback_msg = "匹配行李失败。"
							return False
						# # # 最多不能超过5件。
						weight = self.BFR.format_to_int(kilogram / 18)
						if weight > 5:
							self.logger.info(f"公斤数大于5件(*>﹏<*)【{n}】【{v}】")
							self.callback_msg = "匹配行李失败。"
							return False
						for i in range(weight):
							single_baggage.append({"ssrCode": f"BAG{i+1}", "count": 1})
					# # # 追加每个儿童具体的参数。
					baggages[self.passenger_key[n]] = single_baggage
			# # # 生成请求参数。
			self.RCR.post_data = {"bags": {self.journey_key : baggages}}
			if self.RCR.request_to_put("json", "json"):
				# # # 查询错误信息。
				error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
				if error:
					self.logger.info(f"添加服务失败(*>﹏<*)【{error}】")
					self.callback_msg = f"添加服务失败【{error}】。"
					return False
				# # # 继承header, 添加座位信息。
				self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/passengers/seats"
				self.RCR.header.update({
					"Referer": "https://www.spirit.com/book/seats",
				})
				# # # 基础参数。
				self.RCR.post_data = {"passengerSeatRequests":[]}
				if self.RCR.request_to_put("json", "json"):
					# # # 查询错误信息。
					error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
					if error:
						self.logger.info(f"添加服务失败(*>﹏<*)【{error}】")
						self.callback_msg = f"添加服务失败【{error}】。"
						return False
					# # # 安全通过。
					return True
			# # # 错误重试。
			self.logger.info(f"服务第{count + 1}次超时或者错误(*>﹏<*)【service】")
			self.callback_msg = f"请求服务第{count + 1}次超时"
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
			# # # 生成header，开始预支付。
			self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/package/type/commit"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json",
				"Host": "api.spirit.com",
				"Origin": "https://www.spirit.com",
				"Referer": "https://www.spirit.com/book/options",
				"Ocp-Apim-Subscription-Key": self.verify_key,
				"Authorization": f"Bearer {self.verify_token}",
			})
			self.RCR.post_data = None
			if self.RCR.request_to_post("json", "json"):
				# # # 查询错误信息。
				error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
				if error:
					self.logger.info(f"请求支付失败(*>﹏<*)【{error}】")
					self.callback_msg = f"请求支付失败【{error}】。"
					return False
				# # # 继承header，查询支付页面。
				self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/booking"
				if self.RCR.request_to_get("json"):
					# # # 查询错误信息。
					error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
					if error:
						self.logger.info(f"请求支付失败(*>﹏<*)【{error}】")
						self.callback_msg = f"请求支付失败【{error}】。"
						return False
					# # # 获取最终总价格。
					print(self.RCR.page_source)
					self.total_price, temp_list = self.BPR.parse_to_path(
						"$.data.breakdown.totalAmount", self.RCR.page_source)
					self.total_price = self.BFR.format_to_float(2, self.total_price)
					if not self.total_price:
						self.logger.info(f"支付页面获取价格失败(*>﹏<*)【payment】")
						self.callback_msg = "支付页面获取价格失败"
						return False
					# # # 解析行李价格，按人头和件数分价格。
					baggage_dict, temp_list = self.BPR.parse_to_path(
						"$.data.breakdown.passengers", self.RCR.page_source)
					if baggage_dict:
						# # # 追加每个成人具体的参数。
						for n, v in enumerate(self.CPR.adult_list):
							weight = v.get('baggage')
							# # # 要用乘客key来对应价格。
							key = self.passenger_key[n]
							baggage_total, temp_list = self.BPR.parse_to_path(
								f"$.{key}.specialServices.total", baggage_dict)
							if weight and baggage_total:
								# # # 每个乘客行李总价。
								baggage_total = self.BFR.format_to_float(2, baggage_total)
								self.baggage_price += baggage_total
								# # # 求出没件平均价格。
								numbers = 0
								for w in weight:
									number = self.BFR.format_to_int(w.get('number'))
									numbers += number
								single_price = baggage_total / numbers
								single_price = self.BFR.format_to_float(2, single_price)
								# # # 写入价格。
								for w in weight:
									number = self.BFR.format_to_int(w.get('number'))
									price = single_price * number
									price = self.BFR.format_to_float(2, price)
									w['price'] = price
									self.CPR.return_baggage.append(w)
						# # # 追加每个儿童具体的参数。
						if self.CPR.child_num:
							for n, v in enumerate(self.CPR.child_list):
								n += self.CPR.adult_num
								weight = v.get('baggage')
								# # # 要用乘客key来对应价格。
								key = self.passenger_key[n]
								baggage_total, temp_list = self.BPR.parse_to_path(
									f"$.{key}.specialServices.total", baggage_dict)
								if weight and baggage_total:
									# # # 每个乘客行李总价。
									baggage_total = self.BFR.format_to_float(2, baggage_total)
									self.baggage_price += baggage_total
									# # # 求出没件平均价格。
									numbers = 0
									for w in weight:
										number = self.BFR.format_to_int(w.get('number'))
										numbers += number
									single_price = baggage_total / numbers
									single_price = self.BFR.format_to_float(2, single_price)
									# # # 写入价格。
									for w in weight:
										number = self.BFR.format_to_int(w.get('number'))
										price = single_price * number
										price = self.BFR.format_to_float(2, price)
										w['price'] = price
										self.CPR.return_baggage.append(w)
					# # # 计算最终返回价格，不含行李价格。
					if self.baggage_price:
						self.baggage_price = self.BFR.format_to_float(2, self.baggage_price)
						self.return_price = self.total_price - self.baggage_price
						self.return_price = self.BFR.format_to_float(2, self.return_price)
					else:
						self.return_price = self.total_price

					# # # 比价格是否要继续支付。
					if self.process_to_compare(max_count=self.retry_count):
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
		# # # 生成header, 查询货币汇率。
		self.RCR.url = f"http://flight.yeebooking.com/yfa/tool/interface/convert_conversion_result?" \
		               f"foreignCurrency={self.CPR.currency}&carrier=NK"
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
			# # # 生成卡信息并判断，日期需要月底最后一天的UTC时间。
			card_name = self.CPR.card_last + self.CPR.card_first
			card_name = self.BPR.parse_to_clear(card_name)
			card_date = self.DFR.format_to_transform("20" + self.CPR.card_date, "%Y%m")
			card_day = self.DFR.format_to_last(card_date.year, card_date.month)
			card_day -= 1
			card_date = card_date.strftime("%Y-%m-") + f"{card_day}T16:00:00.000Z"
			card_code = self.AFR.decrypt_into_aes(
				self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.card_code)
			if not card_code:
				self.logger.info(f"解密支付卡失败(*>﹏<*)【{self.CPR.card_code}】")
				self.callback_msg = "解密支付卡失败，请通知技术检查程序。"
				return False
			# # # 生成header，开始支付。
			self.RCR.url = "https://api.spirit.com/dotrez2/api/nsk/nk/booking/book"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Content-Type": "application/json",
				"Host": "api.spirit.com",
				"Origin": "https://www.spirit.com",
				"Referer": "https://www.spirit.com/book/payment",
				"Ocp-Apim-Subscription-Key": self.verify_key,
				"Authorization": f"Bearer {self.verify_token}",
			})
			# # # 基础参数。
			self.RCR.post_data = {
				"payment": {
					"amount": self.total_price, "currencyCode": self.CPR.currency,
			        "creditCard": {
				        "name": card_name, "number": self.CPR.card_num, "cvv": card_code,
				        "expiration": card_date, "cardType": "MC",
				        "address": {"lineOne": "BEIJINGHAIDIAN", "city": "BEIJING",
				                    "postalCode": "100000", "provinceState":"NA", "countryCode":"CN"}
			        },
					"installments": 1,
					"deviceFingerprintId": "6a9e732d-8094-43dc-bcbb-c54e8dfa34eb"},
				"travelGuardSelected": False,
				"trialClubMembershipSelected": False,
				"checkInOptionSelected": "notdecideBPT", "paymentType": "navitaire", "flow": "book"
			}
			if self.RCR.request_to_post("json", "json", 201):
				# # # 查询错误信息。
				error, temp_list = self.BPR.parse_to_path("$.errors[0].rawMessage", self.RCR.page_source)
				if error:
					self.logger.info(f"请求支付失败(*>﹏<*)【{error}】")
					self.callback_msg = f"请求支付失败【{error}】。"
					self.callback_data["orderIdentification"] = 2
					return False
				# # # 获取PNR。
				success, temp_list = self.BPR.parse_to_path("$.data.paymentSucceeded", self.RCR.page_source)
				self.record, temp_list = self.BPR.parse_to_path("$.data.recordLocator", self.RCR.page_source)
				if success and self.record:
					return True
				else:
					self.logger.info("获取支付编码失败(*>﹏<*)【record】")
					self.callback_msg = "获取PNR失败，可能已出票，请核对。"
					self.callback_data["orderIdentification"] = 2
					return False
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
		if self.CPR.promo:
			if self.promo_success:
				self.callback_data['msg'] = f"出票成功，优惠码有效，【{self.CPR.promo}】。"
			else:
				self.callback_data['msg'] = f"出票成功，优惠码无效，【{self.CPR.promo}】。"
		else:
			self.callback_data['msg'] = "出票成功，无优惠码。"
		
		self.callback_data["success"] = "true"
		self.callback_data['totalPrice'] = self.return_price
		self.callback_data["currency"] = self.CPR.currency
		self.callback_data['pnrCode'] = self.record
		self.callback_data["orderIdentification"] = 3
		self.callback_data["baggages"] = self.CPR.return_baggage
		self.logger.info(self.callback_data)
		return True

