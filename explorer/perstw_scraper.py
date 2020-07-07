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


class PersTWScraper(RequestWorker):
	"""TW采集器，TW网站流程交互。行李是坑，不知道那些航线能选，行李价格不能区分人，强制过。"""
	
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
		self.booking_ticket: str = ""  # 认证token。
		self.csrf: str = ""  # 认证key。
		self.segment_info: str = ""
		self.adult_fare: str = ""
		self.child_fare: str = ""
		self.depart_name: str = ""
		self.arrival_name: str = ""
		
		self.param_key: str = ""  # 支付key。

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
		self.user_agent, self.init_header = self.RCR.build_to_header("Chrome")
		self.CPR.currency = "USD"
		# # # 主体流程。
		if self.process_to_search():
			if self.process_to_query():
				if self.process_to_detail():
					if self.process_to_passenger():
						if self.process_to_service():
							# if self.process_to_payment():
							# 	if self.process_to_record():
									self.process_to_return()
									self.logger.removeHandler(self.handler)
									return self.callback_data
		# # # 错误返回。
		self.callback_data['msg'] = self.callback_msg
		# self.callback_data['msg'] = "解决问题中，请手工支付。"
		self.logger.info(self.callback_data)
		self.logger.removeHandler(self.handler)
		return self.callback_data
	
	def process_to_verify(self, verify_url: str = "", count: int = 0, max_count: int = 6) -> bool:
		"""Verify process. 验证过程。

		Args:
			verify_url ( str): 认证地址。
			count (int): 累计计数。
			max_count (int): 最大计数。

		Returns:
			bool
		"""
		if count >= max_count:
			return False
		else:
			# # # 获取图片base64地址。
			img, temp_list = self.DPR.parse_to_attributes("src", "css", "form img", self.RCR.page_source)
			img = img.split(",")
			if img and len(img) > 1:
				img = img[1]
				# # # 进行打码，获取返回数字。
				self.RCR.url = "http://47.97.27.36:30002/5jweb/code"
				self.RCR.post_data = {'postdata': img}
				self.RCR.request_to_post("json")
				number = self.RCR.page_source
				number = self.BPR.parse_to_clear(number)
				if number:
					# # # 生成header, 进行认证。
					self.RCR.url = verify_url
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Content-Type": "application/x-www-form-urlencoded",
						"Host": "www.twayair.com",
						"Origin": "https://www.twayair.com",
						"Referer": verify_url,
						"Upgrade-Insecure-Requests": "1",
					})
					self.RCR.post_data = [("code", number)]
					if self.RCR.request_to_post(is_redirect=True, status_code=403):
						return True
			# # # 错误重试。
			self.logger.info(f"请求验证第{count + 1}次超时(*>﹏<*)【verify】")
			self.callback_msg = f"请求验证第{count + 1}次超时，请重试。"
			return self.process_to_verify(verify_url, count + 1, max_count)
	
	def process_to_search(self, count: int = 0, max_count: int = 1) -> bool:
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
			# # # 插入cookie，选择语言和地区。
			cookies = [
				{"name": "SETTINGS_LANGUAGE", "value": "zh-CN", "domain": "www.twayair.com", "path": "/"},
				{"name": "SETTINGS_REGION", "value": "CN", "domain": "www.twayair.com", "path": "/"},
			]
			self.RCR.set_to_cookies(True, cookies)
			# # # 生成header, 请求首页。
			self.RCR.url = "https://www.twayair.com/app/main"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "www.twayair.com",
				"Upgrade-Insecure-Requests": "1",
			})
			if self.RCR.request_to_get():
				# # # 查询是否需要打码。
				captcha, temp_list = self.DPR.parse_to_attributes(
					"placeholder", "css", "input[name=code]", self.RCR.page_source)
				if captcha and "Enter the captcha code" in captcha:
					if self.process_to_verify("https://www.twayair.com/app/main"):
						return self.process_to_search()
					else:
						return False
				# # #
				self.booking_ticket, temp_list = self.BPR.parse_to_regex("_t = '(.*?)'", self.RCR.page_source)
				self.csrf, temp_list = self.DPR.parse_to_attributes(
					"value", "css", "input[name=_csrf]", self.RCR.page_source)
				# # # 转换接口日期。
				flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
				# # # 生成header, 搜索航班数据。
				self.RCR.url = "https://www.twayair.com/app/booking/chooseItinerary"
				self.RCR.param_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Content-Type": "application/x-www-form-urlencoded",
					"Host": "www.twayair.com",
					"Origin": "https://www.twayair.com",
					"Referer": "https://www.twayair.com/app/main",
					"Upgrade-Insecure-Requests": "1",
				})
				# # # 基础参数。
				param_batch = [
					("promoCode", False, ""), ("bookingTicket", False, self.booking_ticket),
					("tripType", False, "OW"), ("bookingType", False, "HI"),
					("promoCodeDetails.promoCode", False, ""), ("validPromoCode", False, ""),
					("availabilitySearches[0].depAirport", False, self.CPR.departure_code),
					("availabilitySearches[0].arrAirport", False, self.CPR.arrival_code),
					("availabilitySearches[0].flightDate", False, flight_date.strftime("%Y-%m-%d")),
					("availabilitySearches[1].depAirport", False, ""),
					("availabilitySearches[1].arrAirport", False, ""),
					("availabilitySearches[1].flightDate", False, ""),
					("availabilitySearches[2].depAirport", False, ""),
					("availabilitySearches[2].arrAirport", False, ""),
					("availabilitySearches[2].flightDate", False, ""),
					("availabilitySearches[3].depAirport", False, ""),
					("availabilitySearches[3].arrAirport", False, ""),
					("availabilitySearches[3].flightDate", False, ""),
					("availabilitySearches[4].depAirport", False, ""),
					("availabilitySearches[4].arrAirport", False, ""),
					("availabilitySearches[4].flightDate", False, ""),
					("paxCountDetails[0].paxCount", False, self.CPR.adult_num),
					("paxCountDetails[1].paxCount", False, self.CPR.child_num),
					("paxCountDetails[2].paxCount", False, self.CPR.infant_num),
					("availabilitySearches[0].depAirportName", False, ""),
					("availabilitySearches[0].arrAirportName", False, ""),
					("availabilitySearches[1].depAirportName", False, ""),
					("availabilitySearches[1].arrAirportName", False, ""),
					("availabilitySearches[2].depAirportName", False, ""),
					("availabilitySearches[2].arrAirportName", False, ""),
					("availabilitySearches[3].depAirportName", False, ""),
					("availabilitySearches[3].arrAirportName", False, ""),
					("availabilitySearches[4].depAirportName", False, ""),
					("availabilitySearches[4].arrAirportName", False, ""),
					("_csrf", False, self.csrf), ("pax", False, self.CPR.adult_num),
					("pax", False, self.CPR.child_num), ("pax", False, self.CPR.infant_num),
					("deptAirportCode", False, self.CPR.departure_code),
					("arriAirportCode", False, self.CPR.arrival_code),
					("schedule", False, flight_date.strftime("%Y-%m-%d")),
				]
				# # # 生成请求参数。
				self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.page_source)
				if self.RCR.request_to_post():
					# # # 查询是否需要打码。
					captcha, temp_list = self.DPR.parse_to_attributes(
						"placeholder", "css", "input[name=code]", self.RCR.page_source)
					if captcha and "Enter the captcha code" in captcha:
						if self.process_to_verify("https://www.twayair.com/app/booking/chooseItinerary"):
							return self.process_to_search()
						else:
							return False
					
					# # # 生成header, 点击查询航班数据。
					self.RCR.url = "https://www.twayair.com/app/booking/layerAvailabilityList"
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Accept": "text/html, */*; q=0.01",
						"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
						"Host": "www.twayair.com",
						"Origin": "https://www.twayair.com",
						"Referer": "https://www.twayair.com/app/booking/chooseItinerary",
						"X-Requested-With": "XMLHttpRequest",
					})
					self.RCR.post_data = [("_csrf", self.csrf)]
					if self.RCR.request_to_post():
					
						return True
			# # # 错误重试。
			self.logger.info(f"搜索航班第{count + 1}次超时(*>﹏<*)【search】")
			self.callback_msg = f"搜索航班第{count + 1}次超时，请重试。"
			return self.process_to_query(count + 1, max_count)
	
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
			# # #
			table, table_list = self.DPR.parse_to_attributes(
				"text", "css",
				"#price_list_route_1 li.price_list.route_all.route_1 .bul_air_info", self.RCR.page_source)
			if not table_list:
				self.logger.info(
					f"获取不到航线数据(*>﹏<*)【{self.CPR.departure_code}】【{self.CPR.arrival_code}】")
				self.callback_msg = "该航线航班已售完。"
				return False
			# # # 解析接口航班号。
			interface_carrier = self.CPR.flight_num[:2]
			interface_no = self.CPR.flight_num[2:]
			interface_no = self.BFR.format_to_int(interface_no)
			# # # 转换接口日期。
			flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
			# # # 设置匹配航班标识和坐席标识。
			is_flight = False
			is_seat = False
			for n, v in enumerate(table_list):
				source_num = self.BPR.parse_to_clear(v)
				source_carrier = source_num[:2]
				source_no = source_num[2:]
				source_no = self.BFR.format_to_int(source_no)
				if interface_carrier == source_carrier and interface_no == source_no:
					is_flight = True
					
					seat, seat_list = self.DPR.parse_to_attributes(
						"data-faretype", "css",
						f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n+1}) "
						f".tripInfo",
						self.RCR.page_source)
					print(seat_list)
					for k, j in enumerate(seat_list):
						disabled, temp_list = self.DPR.parse_to_attributes(
							"disabled", "css",
							f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n+1}) "
							f".rate_box.fareType:nth-child({k+1}) .tripInfo",
							self.RCR.page_source)
						if not disabled:
							is_seat = True
							
							self.depart_name, temp_list = self.DPR.parse_to_attributes(
								"data-departureairportname", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							self.arrival_name, temp_list = self.DPR.parse_to_attributes(
								"data-arrivalairportname", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							carriercode, temp_list = self.DPR.parse_to_attributes(
								"data-carriercode", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							flightnumber, temp_list = self.DPR.parse_to_attributes(
								"data-flightnumber", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							flightdatewithday, temp_list = self.DPR.parse_to_attributes(
								"data-flightdatewithday", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							fareclass, temp_list = self.DPR.parse_to_attributes(
								"data-bookingclass", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							segmentindex, temp_list = self.DPR.parse_to_attributes(
								"data-segmentindex", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							segmentfareclass, temp_list = self.DPR.parse_to_attributes(
								"data-segmentfareclass", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							journeytime, temp_list = self.DPR.parse_to_attributes(
								"data-journeytime", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							daychange, temp_list = self.DPR.parse_to_attributes(
								"data-daychange", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							aircraftinfotype, temp_list = self.DPR.parse_to_attributes(
								"data-aircraftinfotype", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							aircraftinfoversion, temp_list = self.DPR.parse_to_attributes(
								"data-aircraftinfoversion", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							departuretime, temp_list = self.DPR.parse_to_attributes(
								"data-departuretime", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							arrivaltime, temp_list = self.DPR.parse_to_attributes(
								"data-arrivaltime", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							stops, temp_list = self.DPR.parse_to_attributes(
								"data-stops", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							departuretimezone, temp_list = self.DPR.parse_to_attributes(
								"data-departuretimezone", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							arrivaltimezone, temp_list = self.DPR.parse_to_attributes(
								"data-arrivaltimezone", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							departuredatetimeltc, temp_list = self.DPR.parse_to_attributes(
								"data-departuredatetimeltc", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							departuredatetimeutc, temp_list = self.DPR.parse_to_attributes(
								"data-departuredatetimeutc", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							arrivaldatetimeltc, temp_list = self.DPR.parse_to_attributes(
								"data-arrivaldatetimeltc", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							arrivaldatetimeutc, temp_list = self.DPR.parse_to_attributes(
								"data-arrivaldatetimeutc", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							faretransactionid, temp_list = self.DPR.parse_to_attributes(
								"data-faretransactionid", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							farebasis, temp_list = self.DPR.parse_to_attributes(
								"data-farebasis", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							farelevel, temp_list = self.DPR.parse_to_attributes(
								"data-farelevel", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .segmentInfo.debug",
								self.RCR.page_source)
							adult_base, temp_list = self.DPR.parse_to_attributes(
								"data-basefare_amount", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .pricingInfo.ADULT",
								self.RCR.page_source)
							adult_currency, temp_list = self.DPR.parse_to_attributes(
								"data-basefare_currencycode", "css",
								f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
								f".rate_box.fareType:nth-child({k + 1}) .pricingInfo.ADULT",
								self.RCR.page_source)
							
							self.segment_info = f"SegmentId=1&CarrierCode={carriercode}&FltNumber={flightnumber}" \
							               f"&FlightDate={flight_date.strftime('%Y-%m-%d')}" \
							               f"&FlightDateWithDay={flightdatewithday}&FareClass={fareclass}" \
							               f"&JourneyTime=0" \
							               f"&SegmentIndex={segmentindex}&SegmentFareClass={segmentfareclass}" \
							               f"&FlightSegmentGroupId=1&JourneyTime={journeytime}" \
							               f"&ArrivalDayChange={daychange}&AircraftType={aircraftinfotype}" \
							               f"&AircraftVersion={aircraftinfoversion}&Stops={stops}" \
							               f"&DepartureTime={departuretime}&ArrivalTime={arrivaltime}" \
							               f"&DepAirport={self.CPR.departure_code}" \
							               f"&DepartureTimeZone={departuretimezone}" \
							               f"&ScheduledDepartureDateTimeLTC={departuredatetimeltc}" \
							               f"&ScheduledDepartureDateTimeUTC={departuredatetimeutc}" \
							               f"&ArrAirport={self.CPR.arrival_code}" \
							               f"&ArrivalTimeZone={arrivaltimezone}" \
							               f"&ScheduledArrivalDateTimeLTC={arrivaldatetimeltc}" \
							               f"&ScheduledArrivalDateTimeUTC={arrivaldatetimeutc}"
						
							self.adult_fare = f"SegmentId=1&FlightSegmentGroupId=1&FareType={j}" \
							            f"&FareLevel={farelevel}&FareBasisCode={farebasis}" \
							            f"&FareClass={fareclass}&SegmentFareClass={segmentfareclass}" \
							            f"&PaxType=ADULT&FareTransactionId={faretransactionid}" \
							            f"&&BaseFare={adult_base}&Currency={adult_currency}"
								
							if self.CPR.child_num:
								child_base, temp_list = self.DPR.parse_to_attributes(
									"data-basefare_amount", "css",
									f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
									f".rate_box.fareType:nth-child({k + 1}) .pricingInfo.CHILD",
									self.RCR.page_source)
								child_currency, temp_list = self.DPR.parse_to_attributes(
									"data-basefare_currencycode", "css",
									f"#price_list_route_1 li.price_list.route_all.route_1:nth-child({n + 1}) "
									f".rate_box.fareType:nth-child({k + 1}) .pricingInfo.CHILD",
									self.RCR.page_source)
								self.child_fare = f"SegmentId=1&FlightSegmentGroupId=1&FareType={j}" \
								             f"&FareLevel={farelevel}&FareBasisCode={farebasis}" \
								             f"&FareClass={fareclass}&SegmentFareClass={segmentfareclass}" \
								             f"&PaxType=CHILD&FareTransactionId={faretransactionid}" \
								             f"&&BaseFare={child_base}&Currency={child_currency}"
								
							break
							
					if not is_seat:
						self.logger.info(f"该航班座位已售完(*>﹏<*)【{self.CPR.flight_num}】")
						self.callback_msg = "该航班座位已售完。"
						return False
					
					break
			# # # 没有找到航班号码。
			if not is_flight:
				self.logger.info(f"查找对应航班号失败(*>﹏<*)【{self.CPR.flight_num}】")
				self.callback_msg = f"查找对应航班号失败【{self.CPR.flight_num}】，请核实。"
				return False
			# # # 生成header, 点击提交航班数据。
			self.RCR.url = "https://www.twayair.com/app/booking/bundle"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "www.twayair.com",
				"Origin": "https://www.twayair.com",
				"Referer": "https://www.twayair.com/app/booking/layerAvailabilityList",
				"Upgrade-Insecure-Requests": "1",
			})
			# # # 基础参数。
			param_batch = [
				("promoCode", False, ""),
				("bookingTicket", False, self.booking_ticket),
				("tripType", False, "OW"),
				("bookingType", False, "HI"),
				("promoCodeDetails.promoCode", False, ""),
				("validPromoCode", False, ""),
				("availabilitySearches[0].depAirport", False, self.CPR.departure_code),
				("availabilitySearches[0].arrAirport", False, self.CPR.arrival_code),
				("availabilitySearches[0].flightDate", False, flight_date.strftime("%Y-%m-%d")),
				("availabilitySearches[1].depAirport", False, ""),
				("availabilitySearches[1].arrAirport", False, ""),
				("availabilitySearches[1].flightDate", False, ""),
				("availabilitySearches[2].depAirport", False, ""),
				("availabilitySearches[2].arrAirport", False, ""),
				("availabilitySearches[2].flightDate", False, ""),
				("availabilitySearches[3].depAirport", False, ""),
				("availabilitySearches[3].arrAirport", False, ""),
				("availabilitySearches[3].flightDate", False, ""),
				("paxCountDetails[0].paxCount", False, self.CPR.adult_num),
				("paxCountDetails[1].paxCount", False, self.CPR.child_num),
				("paxCountDetails[2].paxCount", False, self.CPR.infant_num),
				("availabilitySearches[0].depAirportName", False, self.depart_name),
				("availabilitySearches[0].arrAirportName", False, self.arrival_name),
				("_csrf", False, self.csrf),
				("routeCount", False, "1"),
				("PaxCountDetails", False, f"PaxType=ADULT&PaxCount={self.CPR.adult_num}"),
				("FlightSegmentInfo", False, self.segment_info),
				("FareInfoForGuestType", False, self.adult_fare),
				("pax", False, self.CPR.adult_num),
				("pax", False, self.CPR.child_num),
				("pax", False, self.CPR.infant_num),
				("deptAirportCode", False, self.CPR.departure_code),
				("arriAirportCode", False, self.CPR.arrival_code),
				("schedule", False, flight_date.strftime("%Y-%m-%d")),
			]
			if self.CPR.child_num:
				param_batch.extend([
					("PaxCountDetails", False, f"PaxType=CHILD&PaxCount={self.CPR.child_num}"),
					("FareInfoForGuestType", False, self.child_fare),
				])
			# # # 生成请求参数。
			self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.page_source)
			if self.RCR.request_to_post():
				return True
				
		# # # 错误重试。
		self.logger.info(f"提交查询第{count + 1}次超时(*>﹏<*)【query】")
		self.callback_msg = f"提交查询第{count + 1}次超时，请重试。"
		return self.process_to_query(count + 1, max_count)
	
	def process_to_detail(self, count: int = 0, max_count: int = 4) -> bool:
		"""Detail process. 细节过程。

		Returns:
			bool
		"""
		if count >= max_count:
			return False
		else:
			# # # 继承header, 点击查询航班数据。
			self.RCR.url = "https://www.twayair.com/app/login/memberLogin"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "www.twayair.com",
				"Origin": "null",
				"Upgrade-Insecure-Requests": "1",
			})
			# # # 转换接口日期。
			flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
			# # # 基础参数。
			param_batch = [
				("bookingTicket", False, self.booking_ticket),
				("routeCount", False, "1"),
				("tripType", False, "OW"),
				("bookingType", False, "HI"),
				("promoCode", False, ""),
				("deptAirportCode", False, self.CPR.departure_code),
				("arriAirportCode", False, self.CPR.arrival_code),
				("schedule", False, flight_date.strftime("%Y-%m-%d")),
				("pax", False, self.CPR.adult_num),
				("pax", False, self.CPR.child_num),
				("pax", False, self.CPR.infant_num),
				("PaxCountDetails", False, f"PaxType=ADULT&PaxCount={self.CPR.adult_num}"),
				("FlightSegmentInfo", False, self.segment_info),
				("FareInfoForGuestType", False, self.adult_fare),
				("bundleSearchFlag", False, "true"),
				("_csrf", False, self.csrf),
				("bundleCode", False, ""),
				("bundleSegmentId", False, "1"),
				("returnUrl", False, "/app/booking/paxGate"),
				("returnSubmitType", False, "POST"),
			]
			if self.CPR.child_num:
				param_batch.extend([
					("PaxCountDetails", False, f"PaxType=CHILD&PaxCount={self.CPR.child_num}"),
					("FareInfoForGuestType", False, self.child_fare),
				])
			# # # 生成请求参数。
			self.RCR.post_data = self.DPR.parse_to_batch(
				"value", "css", param_batch, self.RCR.page_source)
			if self.RCR.request_to_post():
				# # # 继承header, 点击查询航班数据。
				self.RCR.url = "https://www.twayair.com/app/login/captchaLoading"
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
					"Host": "www.twayair.com",
				})
				if self.RCR.request_to_get("content"):
					with open("captcha.png", "wb") as f:
						f.write(self.RCR.page_source)

					from PIL import Image
					import numpy as np
					from training.image_transform import convert2gray
					from training.image_test import captcha2text
					aa = "captcha.png"
					captcha_image = Image.open(aa)
					# 转化为np数组
					image = np.array(captcha_image)
					image = convert2gray(image)
					image = image.flatten() / 255
					pre_text = captcha2text([image])
					number = pre_text[0]
					# # # 继承header, 点击查询航班数据。
					self.RCR.url = "https://www.twayair.com/app/login/guestLoginExec"
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Content-Type": "application/x-www-form-urlencoded",
						"Host": "www.twayair.com",
						"Origin": "null",
						"Upgrade-Insecure-Requests": "1",
					})
					# # # 基础参数。
					self.RCR.post_data = [
						("email", self.CPR.contact_email),
						("captcharAnswer", number),
						("log2", "on"),
						("log3", "on"),
						("returnUrl", "/app/booking/paxGate"),
						("returnParameterNames", ""),
						("returnParameterValues", ""),
						("returnSubmitType", "POST"),
						("_csrf", self.csrf),
					]
					if self.RCR.request_to_post():
						# # # 继承header, 点击查询航班数据。
						self.RCR.url = "https://www.twayair.com/ajax/login/loginStatus"
						self.RCR.param_data = None
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							"Accept": "*/*",
							"Host": "www.twayair.com",
							"X-Requested-With": "XMLHttpRequest",
						})
						if self.RCR.request_to_get():
							if "guestCustomer" not in self.RCR.page_source:
								self.logger.info("没有访客登录状态【detail】")
								self.callback_msg = "没有访客登录状态"
								return self.process_to_detail(count + 1, max_count)
			
							# # # 继承header, 点击查询航班数据。
							self.RCR.url = "https://www.twayair.com/app/booking/pax"
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								"Content-Type": "application/x-www-form-urlencoded",
								"Host": "www.twayair.com",
								"Origin": "https://www.twayair.com",
								"Referer": "https://www.twayair.com/app/booking/bundle",
								"Upgrade-Insecure-Requests": "1",
							})
							# # # 转换接口日期。
							flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
							# # # 基础参数。
							param_batch = [
								("bookingTicket", False, self.booking_ticket),
								("routeCount", False, "1"),
								("tripType", False, "OW"),
								("bookingType", False, "HI"),
								("promoCode", False, ""),
								("deptAirportCode", False, self.CPR.departure_code),
								("arriAirportCode", False, self.CPR.arrival_code),
								("schedule", False, flight_date.strftime("%Y-%m-%d")),
								("pax", False, self.CPR.adult_num),
								("pax", False, self.CPR.child_num),
								("pax", False, self.CPR.infant_num),
								("PaxCountDetails", False, f"PaxType=ADULT&PaxCount={self.CPR.adult_num}"),
								("FlightSegmentInfo", False, self.segment_info),
								("FareInfoForGuestType", False, self.adult_fare),
								("bundleSearchFlag", False, "true"),
								("_csrf", False, self.csrf),
								("bundleCode", False, ""),
								("bundleSegmentId", False, "1"),
							]
							if self.CPR.child_num:
								param_batch.extend([
									("PaxCountDetails", False, f"PaxType=CHILD&PaxCount={self.CPR.child_num}"),
									("FareInfoForGuestType", False, self.child_fare),
								])
							# # # 生成请求参数。
							self.RCR.post_data = self.DPR.parse_to_batch(
								"value", "css", param_batch, self.RCR.page_source)
							if self.RCR.request_to_post():
								return True
			
			# # # 错误重试。
			self.logger.info(f"请求查询第{count + 1}次超时(*>﹏<*)【detail】")
			self.callback_msg = f"请求查询第{count + 1}次超时，请重试"
			return self.process_to_detail(count + 1, max_count)
	
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
			# # # 继承header, 点击查询航班数据。
			self.RCR.url = "https://www.twayair.com/app/booking/SSR"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "www.twayair.com",
				"Origin": "https://www.twayair.com",
				"Referer": "https://www.twayair.com/app/booking/pax",
				"Upgrade-Insecure-Requests": "1",
			})
			# # # 转换接口日期。
			flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
			# # # 基础参数。
			param_batch = [
				("bookingTicket", False, self.booking_ticket),
				("routeCount", False, "1"),
				("tripType", False, "OW"),
				("bookingType", False, "HI"),
				("promoCode", False, ""),
				("deptAirportCode", False, self.CPR.departure_code),
				("arriAirportCode", False, self.CPR.arrival_code),
				("schedule", False, flight_date.strftime("%Y-%m-%d")),
				("pax", False, self.CPR.adult_num),
				("pax", False, self.CPR.child_num),
				("pax", False, self.CPR.infant_num),
				("PaxCountDetails", False, f"PaxType=ADULT&PaxCount={self.CPR.adult_num}"),
				("FlightSegmentInfo", False, self.segment_info),
				("FareInfoForGuestType", False, self.adult_fare),
				("bundleSearchFlag", False, "true"),
				("_csrf", False, self.csrf),
				("bundleCode", False, ""),
				("bundleSegmentId", False, "1"),
				("PnrSessionId", True, "input[name=PnrSessionId]"),
				("pnrContact", False,
				 f"CellNumber={self.CPR.contact_mobile}&CellNumberCountryCode=86"
				 f"&EmailAddress={self.CPR.contact_email}"),
			]
			if self.CPR.child_num:
				param_batch.extend([
					("PaxCountDetails", False, f"PaxType=CHILD&PaxCount={self.CPR.child_num}"),
					("FareInfoForGuestType", False, self.child_fare),
				])
			# # # 追加每个成人具体的参数。
			for n, v in enumerate(self.CPR.adult_list):
				sex = v.get("gender")
				last_name = v.get("last_name")
				last_name = self.BPR.parse_to_clear(last_name)
				first_name = v.get("first_name")
				first_name = self.BPR.parse_to_separate(first_name)
				adult_batch = [
					(f"paxType", False, "ADULT"),
					(f"paxIndex", False, n+1),
					(f"gender_ADULT{n+1}", False, sex),
					(f"lastName", False, last_name),
					(f"firstName", False, first_name),
					(f"dateOfBirthYear", False, ""),
					(f"dateOfBirthMonth", False, ""),
					(f"dateOfBirthDay", False, ""),
					(f"paxsubtype", False, ""),
					("guestDetailList", False,
					 f"GuestId={n+1}&LastName={last_name}&FirstName="
					 f"{first_name}&PaxType=ADULT&DateOfBirth=--&Gender={sex}&SsrInfo="),
				]
				# # # 如果是第一个成人，需要添加联系信息。
				if n == 0:
					adult_batch.extend([
						(f"emailAddress", False, self.CPR.contact_email),
						(f"cellNumberCountryCode", False, "86"),
						(f"cellNumber", False, self.CPR.contact_mobile),
					])
				# # # 追加每个成人具体的参数。
				param_batch.extend(adult_batch)
			# # # 追加每个儿童具体的参数。
			if self.CPR.child_num:
				for n, v in enumerate(self.CPR.child_list):
					GuestId = n + self.CPR.adult_num
					sex = v.get("gender")
					birthday = self.DFR.format_to_transform(v.get("birthday"), "%Y%m%d")
					birth = birthday.strftime("%Y-%m-%d")
					last_name = v.get("last_name")
					last_name = self.BPR.parse_to_clear(last_name)
					first_name = v.get("first_name")
					first_name = self.BPR.parse_to_separate(first_name)
					child_batch = [
						(f"paxType", False, "CHILD"),
						(f"paxIndex", False, n + 1),
						(f"gender_CHILD{n + 1}", False, sex),
						(f"lastName", False, last_name),
						(f"firstName", False, first_name),
						(f"dateOfBirthYear", False, birthday.strftime("%Y")),
						(f"dateOfBirthMonth", False, birthday.strftime("%m")),
						(f"dateOfBirthDay", False, birthday.strftime("%d")),
						(f"paxsubtype", False, ""),
						("guestDetailList", False,
						 f"GuestId={GuestId+1}&LastName={last_name}&FirstName="
						 f"{first_name}&PaxType=CHILD&DateOfBirth={birth}&Gender={sex}&SsrInfo="),
					]
					# # # 追加每个儿童具体的参数。
					param_batch.extend(child_batch)
			# # # 生成请求参数。
			self.RCR.post_data = self.DPR.parse_to_batch(
				"value", "css", param_batch, self.RCR.page_source)
			if self.RCR.request_to_post():
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
			# # # 继承header, 点击查询航班数据。
			self.RCR.url = "https://www.twayair.com/app/booking/rule"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "www.twayair.com",
				"Origin": "https://www.twayair.com",
				"Referer": "https://www.twayair.com/app/booking/SSR",
				"Upgrade-Insecure-Requests": "1",
			})
			# # # 转换接口日期。
			flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
			# # # 基础参数。
			param_batch = [
				("bookingTicket", False, self.booking_ticket),
				("routeCount", False, "1"),
				("tripType", False, "OW"),
				("bookingType", False, "HI"),
				("promoCode", False, ""),
				("deptAirportCode", False, self.CPR.departure_code),
				("arriAirportCode", False, self.CPR.arrival_code),
				("schedule", False, flight_date.strftime("%Y-%m-%d")),
				("pax", False, self.CPR.adult_num),
				("pax", False, self.CPR.child_num),
				("pax", False, self.CPR.infant_num),
				("PaxCountDetails", False, f"PaxType=ADULT&PaxCount={self.CPR.adult_num}"),
				("FlightSegmentInfo", False, self.segment_info),
				("FareInfoForGuestType", False, self.adult_fare),
				("_csrf", False, self.csrf),
				("bundleSegmentId", False, "1"),
				("PnrSessionId", True, "input[name=PnrSessionId]"),
				("PnrNumber", True, "input[name=PnrNumber]"),
				("pnrContact", False,
				 f"CellNumber={self.CPR.contact_mobile}&CellNumberCountryCode=86"
				 f"&EmailAddress={self.CPR.contact_email}"),
			]
			if self.CPR.child_num:
				param_batch.extend([
					("PaxCountDetails", False, f"PaxType=CHILD&PaxCount={self.CPR.child_num}"),
					("FareInfoForGuestType", False, self.child_fare),
				])
			# # # 追加每个成人具体的参数。
			for n, v in enumerate(self.CPR.adult_list):
				# # # 判断行李并累计公斤数。
				weight = v.get('baggage')
				kilogram = 0
				if weight:
					for w in weight:
						kilogram += self.BFR.format_to_int(w.get('weight'))
				# # # 解析行李参数，必须5的倍数。
				if kilogram:
					if kilogram % 5 != 0:
						self.logger.info(f"公斤数不是5的倍数(*>﹏<*)【{n}】【{v}】")
						self.callback_msg = "匹配行李失败。"
						return False
					# # # 公斤数在15到35之间。
					if 15 > kilogram > 35:
						self.logger.info(f"公斤数不在15到35之间(*>﹏<*)【{n}】【{v}】")
						self.callback_msg = "匹配行李失败"
						return False
				
					adult_batch = [
						("GuestId", True, f"//div[contains(@class, 'guestDetails')][{n+1}]/@data-guestid"),
						("SegmentId", True, f"//div[contains(@class, 'guestDetails')][{n+1}]/@data-segmentid"),
						("IsFreeSsr", False, "false"),
						("SsrType", True, f"//div[contains(@class, 'guestDetails')][{n+1}]/@data-baggage_ssrtype"),
						("BaggageValue", False, kilogram),
						("BaggagePCS", True, f"//div[contains(@class, 'guestDetails')][{n+1}]/@data-baggage-pcs"),
						("BaggageAddType", False, "WT"),
					]
					adult_data = self.DPR.parse_to_batch(
					"value", "xpath", adult_batch, self.RCR.copy_source)
					adult_data = tuple(adult_data)
					adult_string = self.BPR.parse_to_url(adult_data)
					# # # 追加每个成人具体的参数。
					param_batch.append(("SavePnrElementInfo", False, adult_string),)
			# # # 追加每个儿童具体的参数。
			if self.CPR.child_num:
				for n, v in enumerate(self.CPR.child_list):
					GuestId = n + self.CPR.adult_num
					# # # 判断行李并累计公斤数。
					weight = v.get('baggage')
					kilogram = 0
					if weight:
						for w in weight:
							kilogram += self.BFR.format_to_int(w.get('weight'))
					# # # 解析行李参数，必须5的倍数。
					if kilogram:
						if kilogram % 5 != 0:
							self.logger.info(f"公斤数不是5的倍数(*>﹏<*)【{n}】【{v}】")
							self.callback_msg = "匹配行李失败。"
							return False
						# # # 公斤数在15到35之间。
						if 15 > kilogram > 35:
							self.logger.info(f"公斤数不在15到35之间(*>﹏<*)【{n}】【{v}】")
							self.callback_msg = "匹配行李失败"
							return False
					
						child_batch = [
							("GuestId", True, f"//div[contains(@class, 'guestDetails')][{GuestId+1}]/@data-guestid"),
							("SegmentId", True, f"//div[contains(@class, 'guestDetails')][{GuestId+1}]/@data-segmentid"),
							("IsFreeSsr", False, "false"),
							("SsrType", True, f"//div[contains(@class, 'guestDetails')][{GuestId+1}]/@data-baggage_ssrtype"),
							("BaggageValue", False, kilogram),
							("BaggagePCS", True, f"//div[contains(@class, 'guestDetails')][{GuestId+1}]/@data-baggage-pcs"),
							("BaggageAddType", False, "WT"),
						]
						child_data = self.DPR.parse_to_batch(
							"value", "xpath", child_batch, self.RCR.copy_source)
						child_data = tuple(child_data)
						child_string = self.BPR.parse_to_url(child_data)
						# # # 追加每个成人具体的参数。
						param_batch.append(("SavePnrElementInfo", False, child_string), )
			# # # 生成请求参数。
			self.RCR.post_data = self.DPR.parse_to_batch(
				"value", "css", param_batch, self.RCR.copy_source)
			if self.RCR.request_to_post():
				
				text, text_list = self.DPR.parse_to_attributes(
					"text", "css", ".table_round table.tb_col thead th", self.RCR.page_source)
				value, value_list = self.DPR.parse_to_attributes(
					"text", "css", ".table_round table.tb_col tbody td", self.RCR.page_source)
				print(text_list, value_list)
				# # #
				pnrNumber, temp_list = self.DPR.parse_to_attributes(
					"value", "css", "input[name=pnrNumber]", self.RCR.page_source)
				actionType, temp_list = self.DPR.parse_to_attributes(
					"value", "css", "input[name=actionType]", self.RCR.page_source)
				productType, temp_list = self.DPR.parse_to_attributes(
					"value", "css", "input[name=productType]", self.RCR.page_source)
				# # # 继承header, 点击查询航班数据。
				self.RCR.url = "https://www.twayair.com/ajax/booking/rulePnrNumberCheck"
				self.RCR.param_data = (
					("pnrNumber", pnrNumber),
				)
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "application/json, text/javascript, */*; q=0.01",
					"Host": "www.twayair.com",
					"X-Requested-With": "XMLHttpRequest",
				})
				if self.RCR.request_to_get():
					if "true" not in self.RCR.page_source:
						self.logger.info("服务检查没通过(*>﹏<*)【service】")
						self.callback_msg = "服务检查没通过"
						return self.process_to_service(count + 1, max_count)

					# # # 继承header, 点击查询航班数据。
					self.RCR.url = f"https://www.twayair.com/app/payment/payment"
					self.RCR.param_data = (
						("bookingTicket", self.booking_ticket),
						("pnrNumber", pnrNumber),
						("actionType", actionType),
						("productType", productType),
					)
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Host": "www.twayair.com",
						"Upgrade-Insecure-Requests": "1",
					})
					if self.RCR.request_to_get():
						# # # 安全通过。
						self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
						self.CPR.currency, temp_list = self.DPR.parse_to_attributes(
							"text", "css",
							"div[class*=paymentInfo] tbody>tr:first-child>td:first-child", self.RCR.page_source)
						self.CPR.currency = self.BPR.parse_to_clear(self.CPR.currency)
						self.total_price, temp_list = self.DPR.parse_to_attributes(
							"text", "css",
							"div[class*=paymentInfo] tbody>tr:first-child>td:first-child strong",
							self.RCR.page_source)
						self.total_price = self.BFR.format_to_float(2, self.total_price)
						print(self.total_price)
						if not self.CPR.currency or not self.total_price:
							self.logger.info("获取支付价格失败(*>﹏<*)【service】")
							self.callback_msg = "获取支付价格失败"
							return False
						
						# # # 追加每个成人具体的参数。
						for n, v in enumerate(self.CPR.adult_list):
							weight = v.get('baggage')
							if weight:
								for w in weight:
									w['price'] = 0.0
									self.CPR.return_baggage.append(w)
						# # # 追加每个儿童具体的参数。
						if self.CPR.child_num:
							for n, v in enumerate(self.CPR.child_list):
								weight = v.get('baggage')
								if weight:
									for w in weight:
										w['price'] = 0.0
										self.CPR.return_baggage.append(w)
						# # # 计算最终返回价格，含行李价格。
						self.return_price = self.total_price
						
						
						# # # 比价格是否要继续支付。
						if self.process_to_compare(max_count=self.retry_count):
							return True
						else:
							return False
						
			# # # 错误重试。
			self.logger.info(f"服务第{count + 1}次超时或者错误(*>﹏<*)【service】")
			self.callback_msg = f"请求服务第{count + 1}次超时"
			return self.process_to_service(count + 1, max_count)

	def process_to_compare(self, count: int = 0, max_count: int = 4) -> bool:
		"""Compare process. 对比过程。

		Args:
			count (int): 累计计数。
			max_count (int): 最大计数。

		Returns:
			bool
		"""
		# # # 生成header, 查询货币汇率。
		self.RCR.url = f"http://flight.yeebooking.com/yfa/tool/interface/convert_conversion_result?" \
		               f"foreignCurrency={self.CPR.currency}&carrier=TW"
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
			pnrNumber, temp_list = self.DPR.parse_to_attributes(
				"value", "css", "input[name=pnrNumber]", self.RCR.copy_source)
			actionType, temp_list = self.DPR.parse_to_attributes(
				"value", "css", "input[name=actionType]", self.RCR.copy_source)
			productType, temp_list = self.DPR.parse_to_attributes(
				"value", "css", "input[name=productType]", self.RCR.copy_source)
			cpnNo, temp_list = self.BPR.parse_to_regex(
				"\$\(\"input\:hidden\[name=\'cpnNo\'\]\"\)\.val\(\'(.*?)\'\)\;",
				self.RCR.copy_source)
			print(cpnNo)
			# # # 生成header，开始预支付。
			self.RCR.url = "https://www.twayair.com/app/payment/eximbayReq"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "www.twayair.com",
				"Origin": "null",
				"Upgrade-Insecure-Requests": "1",
			})
			self.RCR.post_data = [
				("_csrf", self.csrf), ("pastTotalAmountToBePaid", self.total_price),
				("pnrNumber", pnrNumber),
				("actionType", actionType), ("productType", productType),
				("encGuestId", ""), ("pos", ""), ("currency", ""), ("itineraryChangeType", ""),
				("pnrSessionId", ""), ("ssrInfoType", ""), ("infantAddType", ""),
				("bookingTicket", self.booking_ticket), ("extnAddInfo", ""), ("cpnNo", cpnNo),
				("paymentCode", "CCEB"), ("paymentDiv", "CC"), ("additionalDiscount", "N"),
				("usedcard_code", "016"), ("quota", "00"),
				("econCardNo01", ""), ("econCardNo02", ""), ("econCardNo03", ""), ("econCardNo04", ""),
				("econExpMonth", ""), ("econExpYear", ""), ("econCvc", ""), ("tx_bill_yn", "Y"),
				("paypalEmail", ""),
			]
			if self.RCR.request_to_post():
				# # # 匹配下一次请求地址和参数。
				request_url, temp_list = self.DPR.parse_to_attributes(
					"action", "css", "form#paymentForm", self.RCR.page_source)
				if not request_url:
					self.logger.info("获取支付卡页面地址失败(*>﹏<*)【payment】")
					self.callback_msg = "获取支付卡页面地址失败"
					return self.process_to_payment(count + 1, max_count)
				option_post = []
				option, option_list = self.DPR.parse_to_attributes(
					"name", "css", "form#paymentForm input[type=hidden]", self.RCR.page_source)
				for i in option_list:
					option, temp_list = self.DPR.parse_to_attributes(
						"value", "css", f"form#paymentForm input[name={i}]", self.RCR.page_source)
					option_post.append((f"{i}", option))
				# # # 生成header，开始支付。
				# # # https://secureapi.eximbay.com/Gateway/BasicProcessor.krp
				self.RCR.url = "https://secureapi.eximbay.com/Gateway/BasicProcessor.krp"
				self.RCR.param_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Content-Type": "application/x-www-form-urlencoded",
					"Host": "secureapi.eximbay.com",
					"Origin": "null",
					"Upgrade-Insecure-Requests": "1"
				})
				# # # 基础参数。
				self.RCR.post_data = option_post
				if self.RCR.request_to_post():
					self.param_key, temp_list = self.DPR.parse_to_attributes(
						"value", "css", "input[name=paramKey]", self.RCR.page_source)
					if not self.param_key:
						self.logger.info("获取支付卡页面失败(*>﹏<*)【payment】")
						self.callback_msg = "获取支付卡页面失败"
						return self.process_to_payment(count + 1, max_count)
					
					# # # 生成卡信息并判断，卡号不能小于7位。
					if not self.CPR.card_num or len(self.CPR.card_num) < 16:
						self.logger.info("支付卡号小于七位(*>﹏<*)【payment】")
						self.callback_msg = "初始化支付卡号失败，请检查支付卡信息是否准确。"
						return False
					card_num1 = self.CPR.card_num[:4]
					card_num2 = self.CPR.card_num[4:8]
					card_num3 = self.CPR.card_num[8:12]
					card_num4 = self.CPR.card_num[12:]
					card_date = self.DFR.format_to_transform("20" + self.CPR.card_date, "%Y%m")
					card_year = card_date.strftime("%Y")
					card_month = card_date.strftime("%m")
					card_code = self.AFR.decrypt_into_aes(
						self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.card_code)
					if not card_code:
						self.logger.info(f"解密支付卡失败(*>﹏<*)【{self.CPR.card_code}】")
						self.callback_msg = "解密支付卡失败，请通知技术检查程序。"
						return False

					# # # 生成header，开始预支付。
					self.RCR.url = "https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/step_cur_proc.do"
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Accept": "*/*",
						"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
						"Host": "secureapi.eximbay.com",
						"Origin": "https://secureapi.eximbay.com",
						"Referer": "https://secureapi.eximbay.com/Gateway/BasicProcessor.krp",
						"X-Requested-With": "XMLHttpRequest",
					})
					self.RCR.post_data = [
						("paramKey", self.param_key), ("rescode", ""), ("resmsg", ""), ("cardtype", "C000"),
						("dcctype", ""), ("apprvcurrency", ""), ("apprvamount", ""), ("mcpstatus", ""),
						("quotecurrency", ""), ("quoteamount", ""), ("payto", ""), ("finalCurrencyChoice", ""),
						("payment_method", "C000"), ("viewcardno1", card_num1), ("viewcardno2", card_num2),
						("viewcardno3", card_num3), ("viewcardno4", card_num4), ("month", card_month),
						("year", card_year), ("cvv", card_code),
						("fname", self.CPR.card_first), ("lname", self.CPR.card_last),
						("email", self.CPR.contact_email),
					]
					if self.RCR.request_to_post(page_type="json"):
						apprvamount = self.RCR.page_source.get("apprvamount")
						apprvamount = self.BFR.format_to_float(2, apprvamount)
						if apprvamount != self.total_price:
							self.logger.info("获取支付卡确认信息失败(*>﹏<*)【payment】")
							self.callback_msg = "获取支付卡确认信息失败"
							return self.process_to_payment(count + 1, max_count)
						# # # 安全通过。
						self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
						return True
			# # # 错误重试。
			self.logger.info(f"请求支付第{count + 1}次超时(*>﹏<*)【payment】")
			self.callback_msg = f"请求支付第{count + 1}次超时，请重试。"
			return self.process_to_payment(count + 1, max_count)

	def process_to_record(self, count: int = 0, max_count: int = 4) -> bool:
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
			# # # 生成卡信息并判断，卡号不能小于7位。
			if not self.CPR.card_num or len(self.CPR.card_num) < 16:
				self.logger.info("支付卡号小于七位(*>﹏<*)【payment】")
				self.callback_msg = "初始化支付卡号失败，请检查支付卡信息是否准确。"
				return False
			card_num1 = self.CPR.card_num[:4]
			card_num2 = self.CPR.card_num[4:8]
			card_num3 = self.CPR.card_num[8:12]
			card_num4 = self.CPR.card_num[12:]
			card_date = self.DFR.format_to_transform("20" + self.CPR.card_date, "%Y%m")
			card_year = card_date.strftime("%Y")
			card_month = card_date.strftime("%m")
			card_code = self.AFR.decrypt_into_aes(
				self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.card_code)
			if not card_code:
				self.logger.info(f"解密支付卡失败(*>﹏<*)【{self.CPR.card_code}】")
				self.callback_msg = "解密支付卡失败，请通知技术检查程序。"
				return False
			
			dcctype = self.RCR.copy_source.get("dcctype")
			apprvcurrency = self.RCR.copy_source.get("apprvcurrency")
			apprvamount = self.RCR.copy_source.get("apprvamount")
			mcpstatus = self.RCR.copy_source.get("mcpstatus")
			quotecurrency = self.RCR.copy_source.get("quotecurrency")
			quoteamount = self.RCR.copy_source.get("quoteamount")
			payto = self.RCR.copy_source.get("payto")
			# # # 生成header，开始预支付。
			self.RCR.url = "https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/auth_confirm.do"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "secureapi.eximbay.com",
				"Origin": "https://secureapi.eximbay.com",
				"Referer": "https://secureapi.eximbay.com/Gateway/BasicProcessor.krp",
				"Upgrade-Insecure-Requests": "1"
			})
			self.RCR.post_data = [
				("paramKey", self.param_key), ("rescode", ""), ("resmsg", ""), ("cardtype", "C000"),
				("dcctype", dcctype), ("apprvcurrency", apprvcurrency),
				("apprvamount", apprvamount), ("mcpstatus", mcpstatus),
				("quotecurrency", quotecurrency), ("quoteamount", quoteamount),
				("payto", payto), ("finalCurrencyChoice", apprvcurrency),
				("payment_method", "C000"), ("viewcardno1", card_num1), ("viewcardno2", card_num2),
				("viewcardno3", card_num3), ("viewcardno4", card_num4), ("month", card_month),
				("year", card_year), ("cvv", card_code),
				("fname", self.CPR.card_first), ("lname", self.CPR.card_last),
				("email", self.CPR.contact_email), ("dcc_payment", "on"), ("agree", "on"),
			]
			if self.RCR.request_to_post(is_redirect=True):
				# # # 匹配下一次请求地址和参数。
				request_url, temp_list = self.DPR.parse_to_attributes(
					"action", "css", "form[name=Visa3d]", self.RCR.page_source)
				if not request_url:
					self.logger.info("获取支付卡页面地址失败(*>﹏<*)【record】")
					self.callback_msg = "获取支付卡页面地址失败"
					return False
				option_post = []
				option, option_list = self.DPR.parse_to_attributes(
					"name", "css", "form[name=Visa3d] input[type=hidden]", self.RCR.page_source)
				for i in option_list:
					option, temp_list = self.DPR.parse_to_attributes(
						"value", "css", f"form[name=Visa3d] input[name={i}]", self.RCR.page_source)
					option_post.append((f"{i}", option))
				# # # 生成header，开始支付。
				# # # https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/step_proc_3dsk_veri.jsp?paramKey=3A3C54B5A316E369DDE965C40920A87DEE4DEF1A31272167DD69
				self.RCR.url = request_url
				self.RCR.param_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Content-Type": "application/x-www-form-urlencoded",
					"Host": "secureapi.eximbay.com",
					"Origin": "https://secureapi.eximbay.com",
					"Referer": f"https://secureapi.eximbay.com/Gateway/BasicProcessor/"
					           f"2.x/step_proc_3dsk.do?paramKey={self.param_key}",
					"Upgrade-Insecure-Requests": "1"
				})
				# # # 基础参数。
				# # # 重点替换
				option_post.remove(("exponent", ""))
				option_post.append(("exponent", "2"))
				self.RCR.post_data = option_post
				if self.RCR.request_to_post():
					referer_url = request_url
					request_url, temp_list = self.BPR.parse_to_regex(
						"frm\.action = \"(.*?)\";", self.RCR.page_source)
					if not request_url:
						return False

					option_post = []
					option, option_list = self.DPR.parse_to_attributes(
						"name", "css", "form[name=regForm] input[type=hidden]", self.RCR.page_source)
					for i in option_list:
						option, temp_list = self.DPR.parse_to_attributes(
							"value", "css", f"form[name=regForm] input[name={i}]", self.RCR.page_source)
						option_post.append((f"{i}", option))
					# # # 生成header，开始支付。
					# # # https://secure5.arcot.com/acspage/cap?RID=78528&VAA=A
					self.RCR.url = request_url
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Content-Type": "application/x-www-form-urlencoded",
						"Host": "secure5.arcot.com",
						"Origin": "https://secureapi.eximbay.com",
						"Referer": referer_url,
						"Upgrade-Insecure-Requests": "1"
					})
					# # # 基础参数。
					self.RCR.post_data = option_post
					if self.RCR.request_to_post():
						referer_url = request_url

						# # # 匹配下一次请求地址和参数。
						request_url, temp_list = self.DPR.parse_to_attributes(
							"action", "css", "form[name=downloadForm]", self.RCR.page_source)
						if not request_url:
							self.logger.info("获取支付卡页面地址失败(*>﹏<*)【record】")
							self.callback_msg = "获取支付卡页面地址失败"
							return False

						option_post = []
						option, option_list = self.DPR.parse_to_attributes(
							"name", "css", "form[name=downloadForm] input[type=hidden]", self.RCR.page_source)
						for i in option_list:
							option, temp_list = self.DPR.parse_to_attributes(
								"value", "css", f"form[name=downloadForm] input[name={i}]", self.RCR.page_source)
							option_post.append((f"{i}", option))
						# # # 生成header，开始支付。
						# # # https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/step_proc_3dsk_popup_blank.jsp?paramKey=3A3C54B5A316E369DDE965C40920A87DEE4DEF1A31272167DD69
						self.RCR.url = request_url
						self.RCR.param_data = None
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							"Content-Type": "application/x-www-form-urlencoded",
							"Host": "secureapi.eximbay.com",
							"Origin": "https://secure5.arcot.com",
							"Referer": referer_url,
							"Upgrade-Insecure-Requests": "1"
						})
						# # # 基础参数。
						self.RCR.post_data = option_post
						if self.RCR.request_to_post():
							referer_url = request_url
							request_url, temp_list = self.BPR.parse_to_regex(
								"location\.href=\"(.*?)\";", self.RCR.page_source)
							if not request_url:
								return False
							if "https://" not in request_url:
								request_url = "https://secureapi.eximbay.com" + request_url
							
							# # # 生成header，开始支付。
							# # # https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/auth_proc.do?paramKey=3A3C54B5A334980DFD36CCD6868D42DA51DACED20727EA1D7E7D
							self.RCR.url = request_url
							self.RCR.param_data = None
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								"Host": "secureapi.eximbay.com",
								"Referer": referer_url,
								"Upgrade-Insecure-Requests": "1"
							})
							# # # 基础参数。
							self.RCR.post_data = option_post
							if self.RCR.request_to_get():
								referer_url = request_url
								request_url, temp_list = self.BPR.parse_to_regex(
									"frm\.action = \"(.*?)\";", self.RCR.page_source)
								if "step2.do" not in request_url:
									return False
								if "https://" not in request_url:
									request_url = "https://secureapi.eximbay.com" + request_url
								
								# # # 生成header，开始支付。
								# # # https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/step2.do
								self.RCR.url = request_url
								self.RCR.param_data = None
								self.RCR.header = self.BFR.format_to_same(self.init_header)
								self.RCR.header.update({
									"Content-Type": "application/x-www-form-urlencoded",
									"Host": "secureapi.eximbay.com",
									"Origin": "https://secureapi.eximbay.com",
									"Referer": "https://secureapi.eximbay.com/Gateway/BasicProcessor.krp",
									"Upgrade-Insecure-Requests": "1"
								})
								self.RCR.post_data = [
									("paramKey", self.param_key), ("rescode", ""), ("resmsg", ""),
									("cardtype", "C000"),
									("dcctype", dcctype), ("apprvcurrency", apprvcurrency),
									("apprvamount", apprvamount), ("mcpstatus", mcpstatus),
									("quotecurrency", quotecurrency), ("quoteamount", quoteamount),
									("payto", payto), ("finalCurrencyChoice", apprvcurrency),
									("payment_method", "C000"), ("viewcardno1", card_num1),
									("viewcardno2", card_num2),
									("viewcardno3", card_num3), ("viewcardno4", card_num4), ("month", card_month),
									("year", card_year), ("cvv", card_code),
									("fname", self.CPR.card_first), ("lname", self.CPR.card_last),
									("email", self.CPR.contact_email), ("dcc_payment", "on"), ("agree", "on"),
								]
								if self.RCR.request_to_post():
									success, temp_list = self.DPR.parse_to_attributes(
										"text", "css", ".inp_wrap p", self.RCR.page_source)
									success = self.BPR.parse_to_clear(success)
									print(success)
									if "支付成功" not in success:
										error, temp_list = self.DPR.parse_to_attributes(
											"value", "xpath",
											"//div[contains(@class, 'inp_wrap02')]"
											"//text()[contains(., '处理结果')]", self.RCR.page_source)
										error = self.BPR.parse_to_separate(error)
										self.logger.info(f"支付处理结果页面失败(*>﹏<*)【{error}】")
										self.callback_msg = error
										return False
									
									referer_url = request_url
									request_url, temp_list = self.BPR.parse_to_regex(
										"frm\.action = \"(.*?)\";", self.RCR.page_source)
									if not request_url:
										return False
									
									option_post = []
									option, option_list = self.DPR.parse_to_attributes(
										"name", "css", "form#closeForm input[type=hidden]", self.RCR.page_source)
									for i in option_list:
										option, temp_list = self.DPR.parse_to_attributes(
											"value", "css", f"form#closeForm input[name={i}]", self.RCR.page_source)
										option_post.append((f"{i}", option))
									# # # 生成header，开始支付。
									# # # https://www.twayair.com/app/payment/eximbayRes?paymentKey=um3P7ppDCK80%2BUSg31dHRYfpMsueJOXOQvuuHuJj3qs%3D
									self.RCR.url = request_url
									self.RCR.param_data = None
									self.RCR.header = self.BFR.format_to_same(self.init_header)
									self.RCR.header.update({
										"Content-Type": "application/x-www-form-urlencoded",
										"Host": "www.twayair.com",
										"Origin": "https://secureapi.eximbay.com",
										"Referer": referer_url,
										"Upgrade-Insecure-Requests": "1"
									})
									# # # 基础参数。
									self.RCR.post_data = option_post
									if self.RCR.request_to_post():

										referer_url = request_url

										# # # 匹配下一次请求地址和参数。
										request_url, temp_list = self.DPR.parse_to_attributes(
											"action", "css", "form[name=paymentResForm]", self.RCR.page_source)
										if not request_url:
											self.logger.info("获取支付卡页面地址失败(*>﹏<*)【record】")
											self.callback_msg = "获取支付卡页面地址失败"
											return False
										if "https://" not in request_url:
											request_url = "https://www.twayair.com" + request_url

										option_post = []
										option, option_list = self.DPR.parse_to_attributes(
											"name", "css", "form[name=paymentResForm] input[type=hidden]", self.RCR.page_source)
										for i in option_list:
											option, temp_list = self.DPR.parse_to_attributes(
												"value", "css", f"form[name=paymentResForm] input[name={i}]", self.RCR.page_source)
											option_post.append((f"{i}", option))
										# # # 生成header，开始支付。
										# # # https://www.twayair.com/app/payment/eximbaySave
										self.RCR.url = request_url
										self.RCR.param_data = None
										self.RCR.header = self.BFR.format_to_same(self.init_header)
										self.RCR.header.update({
											"Content-Type": "application/x-www-form-urlencoded",
											"Host": "www.twayair.com",
											"Origin": "null",
											"Referer": referer_url,
											"Upgrade-Insecure-Requests": "1"
										})
										# # # 基础参数。
										self.RCR.post_data = option_post
										if self.RCR.request_to_post():
											
											request_url, temp_list = self.BPR.parse_to_regex(
												"(/app/payment/complete.*?)';", self.RCR.page_source)
											if not request_url:
												error, temp_list = self.DPR.parse_to_attributes(
													"text", "css",
													"div#content p.txt_paragraph", self.RCR.page_source)
												error = self.BPR.parse_to_separate(error)
												if error:
													self.logger.info(f"支付处理结果页面失败(*>﹏<*)【{error}】")
													self.callback_msg = error
													return False
											
											# # # 生成header，开始支付。
											# # # https://www.twayair.com/app/payment/complete?encPnrNumber=3JLbyC8h6Eu2fT4MSxjXDQ%3D%3D&encGuestId=&productType=TICK&pos=&currency=&paymentFlag=true
											self.RCR.url = request_url
											self.RCR.param_data = None
											self.RCR.header = self.BFR.format_to_same(self.init_header)
											self.RCR.header.update({
												"Host": "www.twayair.com",
												"Upgrade-Insecure-Requests": "1"
											})
											if self.RCR.request_to_get():
												self.record, temp_list = self.DPR.parse_to_attributes(
													"text", "css", "span.point", self.RCR.page_source)
												self.record = self.BPR.parse_to_clear(self.record)
												if not self.record:
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

