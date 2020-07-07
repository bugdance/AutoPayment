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
import time


class PersFRScraper(RequestWorker):
	"""FR采集器，FR网站流程交互 """
	
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
		self.redirect_url: str = ""  # 支付链接。
		# # # 返回中用到的变量。
		self.total_price: float = 0.0  # 总价。
		self.return_price: float = 0.0  # 返回价格。
		self.baggage_price: float = 0.0  # 行李总价。
		self.record: str = ""  # 票号。
		self.temp_source: str = ""  # 临时储存数据
		self.flightKey: str = ""  # 航班Key
		self.fareKey: str = ""  # 提交航班需要的Key
		self.basketId: str = ""  # 提交航班需要的Id
		self.tempId: str = ""  # 临时Id
		self.sessionId: str = ""  # sessionId
		self.temp_url: str = ""  # 临时url
		self.token: str = ""  # 登录获取的 Token
		self.customerId: str = ""  # url 参数
	
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
		
		# 格式化日期
		self.CPR.flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
		self.CPR.flight_date = self.CPR.flight_date.strftime("%Y-%m-%d")
		
		# # # 主体流程。
		# 判断是否包含儿童， 如果不包含儿童，程序继续往下走， 如果包含则直接返回失败
		if not self.CPR.child_num:
			if self.process_to_home(max_count=self.retry_count):
				if self.process_to_query(max_count=self.retry_count):
					if self.process_to_passenger(max_count=self.retry_count):
						if self.process_to_service(max_count=self.retry_count):
							if self.process_to_other_services(max_count=self.retry_count):
								if self.process_to_record(max_count=self.retry_count):
									self.process_to_return()
									self.logger.info(self.RCR.get_from_cookies())
									self.logger.removeHandler(self.handler)
									return self.callback_data
		else:
			self.callback_msg = "FR | 包含儿童需要选座，暂时不做"
		
		# # # 错误返回。
		self.callback_data['msg'] = self.callback_msg
		# self.callback_data['msg'] = "解决问题中，请手工支付。"
		self.logger.info(self.callback_data)
		self.logger.removeHandler(self.handler)
		return self.callback_data
	
	def process_to_home(self, count: int = 0, max_count: int = 2) -> bool:
		"""Query process. 首页。

		Args:
			count (int): 累计计数。
			max_count (int): 最大计数。

		Returns:
			bool
		"""
		if count >= max_count:
			return False
		else:
			# 请求首页
			self.RCR.url = "https://www.ryanair.com/cn/zh/"
			self.RCR.param_data = None
			self.RCR.post_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
				"Upgrade-Insecure-Requests": "1",
				"Host": "www.ryanair.com"
			})
			if self.RCR.request_to_get(is_redirect=True):
				return True
			
			self.callback_msg = "请求首页失败。"
			return self.process_to_home(count + 1, max_count)
	
	def process_to_query(self, count: int = 0, max_count: int = 2) -> bool:
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
			# 设置 Cookie
			self.RCR.set_to_cookies(include_domain=False, cookie_list=
			[
				{'name': 'mkt', 'value': '/cn/zh/'},
			]
			                        )
			# 查询
			self.RCR.url = "https://www.ryanair.com/cn/zh/trip/flights/select"
			self.RCR.param_data = (
				('ADT', self.CPR.adult_num),  # 成人人数
				('TEEN', '0'),  # 青少年人数
				('CHD', self.CPR.child_num),  # 儿童人数
				('INF', "0"),  # 婴儿人数
				('DateOut', self.CPR.flight_date),  # 出发日期
				('DateIn', ''),
				('Origin', self.CPR.departure_code),  # 出发三字码
				('Destination', self.CPR.arrival_code),  # 到达三字码
				('isConnectedFlight', 'false'),
				('RoundTrip', 'false'),
				('Discount', '0'),
				('tpAdults', self.CPR.adult_num),
				('tpTeens', '0'),
				('tpChildren', self.CPR.child_num),
				('tpInfants', "0"),
				('tpStartDate', self.CPR.flight_date),
				('tpEndDate', ''),
				('tpOriginIata', self.CPR.departure_code),
				('tpDestinationIata', self.CPR.arrival_code),
				('tpIsConnectedFlight', 'false'),
				('tpIsReturn', 'false'),
				('tpDiscount', '0'),
			)
			self.RCR.post_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
				"Upgrade-Insecure-Requests": "1",
				"referer": "https://www.ryanair.com/cn/zh",
			})
			if self.RCR.request_to_get(is_redirect=True):
				
				self.temp_url = self.RCR.response_url
				self.RCR.url = "https://polyfill.ryanair.com/?features=css-vars,object-fit,focus-within,smoothscroll,date-input"
				self.RCR.post_data = None
				self.RCR.param_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					'Host': 'polyfill.ryanair.com',
					'Origin': 'https://www.ryanair.com',
					"Accept": "*/*",
					"Upgrade-Insecure-Requests": "1",
				})
				if self.RCR.request_to_get(is_redirect=True):
					
					self.RCR.url = "https://www.ryanair.com/flightselect_dist/desktop/main.d61e7ff06995138f4477.js"
					self.RCR.post_data = None
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'www.ryanair.com',
						'Origin': 'https://www.ryanair.com',
						"Accept": "*/*",
						'Referer': self.temp_url,
						"Upgrade-Insecure-Requests": "1",
					})
					# if self.RCR.request_to_get(is_redirect=True):
					self.RCR.request_to_get(is_redirect=True)
					self.RCR.url = "https://www.ryanair.com/apps/ryanair/i18n.frontend.auth.flightselect.legalfooter.networkerrors.passengers.input-desktop.sessionexpiration.zh-cn.json"
					self.RCR.post_data = None
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'www.ryanair.com',
						'Origin': 'https://www.ryanair.com',
						"Accept": "application/json, text/plain, */*",
						'Referer': self.temp_url,
						"Upgrade-Insecure-Requests": "1",
					})
					if self.RCR.request_to_get(is_redirect=True):
						
						self.RCR.url = "https://www.ryanair.com/flightselect_dist/desktop/assets/feature-keys.json"
						self.RCR.post_data = None
						self.RCR.param_data = None
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							'Host': 'www.ryanair.com',
							'Origin': 'https://www.ryanair.com',
							"Accept": "application/json, text/plain, */*",
							"Upgrade-Insecure-Requests": "1",
						})
						if self.RCR.request_to_get(is_redirect=True):
							
							self.RCR.url = "https://www.ryanair.com/apps/ryanair/i18n.frontend.gdpr.zh-cn.json"
							self.RCR.post_data = None
							self.RCR.param_data = None
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								'Host': 'www.ryanair.com',
								'Origin': 'https://www.ryanair.com',
								"Accept": "application/json, text/plain, */*",
								"Upgrade-Insecure-Requests": "1",
							})
							if self.RCR.request_to_get(is_redirect=True):
								
								self.RCR.url = "https://www.ryanair.com/cn/zh.headerenclosedlinks.json"
								self.RCR.post_data = None
								self.RCR.param_data = None
								self.RCR.header = self.BFR.format_to_same(self.init_header)
								self.RCR.header.update({
									'Host': 'www.ryanair.com',
									'Origin': 'https://www.ryanair.com',
									"Accept": "application/json, text/plain, */*",
									"Upgrade-Insecure-Requests": "1",
									'Referer': self.temp_url,
								})
								self.RCR.request_to_get(is_redirect=True)
								self.RCR.url = "https://api.ryanair.com/usrprof/v2/loggedin"
								self.RCR.post_data = None
								self.RCR.param_data = None
								self.RCR.header = self.BFR.format_to_same(self.init_header)
								self.RCR.header.update({
									'Host': 'api.ryanair.com',
									'Origin': 'https://www.ryanair.com',
									"Accept": "application/json, text/plain, */*",
									"Upgrade-Insecure-Requests": "1",
								})
								self.RCR.request_to_get(is_redirect=True, status_code=204)
								# 获取航班提交信息
								if self.availability():
									flight_dates, flight_dates_list = self.BPR.parse_to_path('$..dates',
									                                                         self.RCR.page_source)
									if flight_dates:
										for i in flight_dates:
											if str(self.CPR.flight_date) in i.get('dateOut'):
												for flightKey in i.get('flights'):
													
													self.flightKey, flight_list = self.BPR.parse_to_path(
														'$.flightKey', flightKey)
													self.fareKey, temp_list = self.BPR.parse_to_path(
														'$...fareKey', flightKey)
													
													if self.CPR.flight_num in str(self.flightKey).replace('~', ''):
														break
													
													else:
														self.callback_msg = f"航班号匹配失败 | 系统参数：{self.CPR.flight_num} | 网站参数：{str(self.flightKey).replace('~', '')[:7]}"
														return False
												else:
													self.callback_msg = f"当前日期没有航班 {self.CPR.flight_num} | {self.CPR.flight_date}"
													self.logger.info(
														f"当前日期没有航班 (*>﹏<*)【{self.CPR.flight_num}】| {self.CPR.flight_date}")
													return False
									else:
										message, message_list = self.BPR.parse_to_path(
											'$.message', self.RCR.page_source)
										self.callback_msg = f"航班信息获取失败 | 异常信息： {message}"
										self.logger.info(f"航班信息获取失败 (*>﹏<*) | 异常信息： {message}")
										return False
									
									# 校检航班号，是否正确
									if self.submit_flight():
										return True
									else:
										return False
								else:
									return False
			
			self.callback_msg = "查询失败"
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
			# 拼接提交的乘客信息
			variables = {}
			passengers = []
			
			# # # 追加每个成人具体的参数。
			# 乘客总人数
			for n, v in enumerate(self.CPR.adult_list):
				
				# # # 名字不要空格。
				adult_batch = {}
				last_name = v.get("last_name")
				last_name = self.BPR.parse_to_clear(last_name)
				first_name = v.get("first_name")
				first_name = self.BPR.parse_to_clear(first_name)
				
				adult_batch['type'] = 'ADT'
				adult_batch['dob'] = 'null'
				adult_batch['first'] = first_name
				adult_batch['last'] = last_name
				adult_batch['middle'] = ''
				if v.get('gender') == "M":
					adult_batch['title'] = 'MR'
				else:
					adult_batch['title'] = 'MRS'
				adult_batch['paxNum'] = n
				adult_batch['specialAssistance'] = []
				passengers.append(adult_batch)
			
			# # # 追加每个儿童具体的参数。
			if self.CPR.child_num:
				for n, v in enumerate(self.CPR.child_list):
					n += self.CPR.adult_num
					last_name = v.get("last_name")
					last_name = self.BPR.parse_to_clear(last_name)
					first_name = v.get("first_name")
					first_name = self.BPR.parse_to_clear(first_name)
					adult_batch = {}
					adult_batch['type'] = 'CHD'
					adult_batch['dob'] = 'null'
					adult_batch['first'] = first_name
					adult_batch['last'] = last_name
					adult_batch['middle'] = ''
					adult_batch['title'] = 'CHD'
					adult_batch['paxNum'] = n
					adult_batch['specialAssistance'] = []
					passengers.append(adult_batch)
			
			variables['passengers'] = passengers
			variables['basketId'] = self.basketId
			variables = str(variables).replace('\'', '\"')
			variables = self.BPR.parse_to_clear(variables)
			variables = variables.replace('\"null\"', 'null')
			
			# 添加乘客信息
			self.RCR.url = "https://personapi.ryanair.com/api/zh-cn/graphql"
			self.RCR.param_data = None
			self.RCR.post_data = '''{"query":"mutation AddPassengers($passengers: [InputPassenger] = null, $basketId: String!) {\n  addPassengers(passengers: $passengers, basketId: $basketId) {\n    ...PassengersResponse\n  }\n}\n\nfragment PassengersResponse on PassengersResponse {\n  passengers {\n    ...PassengersPassenger\n  }\n}\n\nfragment PassengersPassenger on Passenger {\n  paxNum\n  type\n  title\n  first\n  middle\n  last\n  dob\n  inf {\n    ...PassengersInfant\n  }\n  specialAssistance {\n    ...PassengersPassengerPrmSsrType\n  }\n}\n\nfragment PassengersInfant on Infant {\n  first\n  middle\n  last\n  dob\n}\n\nfragment PassengersPassengerPrmSsrType on PassengerPrmSsrType {\n  codes\n  journeyNum\n  segmentNum\n}\n","variables":''' + variables + "}"
			self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				'Host': 'personapi.ryanair.com',
				'Content-Type': 'application/json',
				'Accept': 'application/json, text/plain, */*',
				'Origin': 'https://www.ryanair.com',
				'Sec-Fetch-Site': 'same-site',
				'Sec-Fetch-Mode': 'cors',
			})
			if self.RCR.request_to_post(is_redirect=True, page_type='json'):
				
				# 请求座位页面
				self.RCR.url = f"https://www.ryanair.com/cn/zh/trip/flights/seats?tpAdults={self.CPR.adult_num}&tpTeens=0&tpChildren={self.CPR.child_num}&tpInfants=0&tpStartDate={self.CPR.flight_date}&tpEndDate=&tpOriginIata={self.CPR.departure_code}&tpDestinationIata={self.CPR.arrival_code}&tpIsConnectedFlight=false&tpIsReturn=false&tpDiscount=0"
				self.RCR.param_data = None
				self.RCR.post_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					'Host': 'www.ryanair.com',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Referer': self.temp_url,
				})
				if self.RCR.request_to_get(is_redirect=True):
					
					self.temp_url = self.BFR.format_to_same(self.RCR.response_url)
					self.RCR.url = "https://www.ryanair.com/api/booking/v5/zh-cn/Passenger"
					self.RCR.param_data = None
					self.RCR.post_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'www.ryanair.com',
						'Accept': 'application/json, text/plain, */*',
						'Referer': self.RCR.response_url,
						'X-Session-Token': self.sessionId,
						'Content-Type': 'application/json;charset=UTF-8',
					})
					if self.RCR.request_to_get(is_redirect=True):
						
						self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
						self.RCR.param_data = None
						self.RCR.post_data = '''{"query":"query GetBasket($basketId: String!, $isGettingAroundAvailable: Boolean!, $isThingsToDoAvailable: Boolean!) {\n  basket(id: $basketId) {\n    ...BasketCommon\n    gettingAround @include(if: $isGettingAroundAvailable) {\n      ...GettingAroundPillar\n    }\n    thingsToDo @include(if: $isThingsToDoAvailable) {\n      ...ThingsToDoPillar\n    }\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n\nfragment GettingAroundPillar on GettingAroundType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    payLater {\n      amountWithTaxes\n      total\n    }\n    variant {\n      ...VariantCar\n      ...VariantCarRental\n      ...VariantGroundTransfer\n    }\n  }\n}\n\nfragment VariantCar on VariantUnionType {\n  ... on Car {\n    rentPrice\n    carName\n    refId\n    engineLoadId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n    }\n    residence\n    age\n  }\n}\n\nfragment VariantCarRental on VariantUnionType {\n  ... on CarRental {\n    rentPrice\n    carName\n    refId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n      payNow\n    }\n    residence\n    age\n    searchId\n  }\n}\n\nfragment ThingsToDoPillar on ThingsToDoType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    variant {\n      ... on Ticket {\n        name\n        reservationCode\n        activityTime\n        address\n      }\n    }\n  }\n}\n","variables":{"basketId":"''' + self.basketId + '''","isGettingAroundAvailable":true,"isThingsToDoAvailable":true},"operationName":"GetBasket"}'''
						self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							'Host': 'basketapi.ryanair.com',
							'Accept': 'application/json, text/plain, */*',
							'Origin': 'https://www.ryanair.com',
							'Content-Type': 'application/json',
						})
						if self.RCR.request_to_post(is_redirect=True, page_type='json'):
							
							self.RCR.url = "https://catalogapi.ryanair.com/api/zh-cn/graphql"
							self.RCR.param_data = None
							self.RCR.post_data = '''{"variables":{"basketId":"''' + self.basketId + '''"},"query":"query FligthExtrasQuery($basketId: String!) {\n  flightExtras(basketId: $basketId, products: [FAST, INSURANCE, PARKING, EQUIPMENT, SEATS, BAGS, CBAG, PRIOBRDNG, INFLIGHT]) {\n    ...ExtraFrag\n  }\n}\n\nfragment ExtraFrag on FlightExtra {\n  code\n  maxPerPassenger\n  minPrice\n  priceDetails {\n    journeyNumber\n  }\n}\n"}'''
							self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								'Host': 'catalogapi.ryanair.com',
								'Accept': 'application/json, text/plain, */*',
								'Origin': 'https://www.ryanair.com',
								'Content-Type': 'application/json',
							})
							if self.RCR.request_to_post(is_redirect=True, page_type='json'):
								
								# 不选择座位，提交信息
								self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
								self.RCR.param_data = None
								self.RCR.post_data = '''{"query":"mutation AssignSeat($basketId: String!, $seats: [SeatInputType]!) {\n  assignSeat(basketId: $basketId, seats: $seats) {\n    ...BasketCommon\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n","variables":{"basketId":"''' + self.basketId + '''","seats":[]},"operationName":"AssignSeat"}'''
								self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
								self.RCR.header = self.BFR.format_to_same(self.init_header)
								self.RCR.header.update({
									'Host': 'basketapi.ryanair.com',
									'Accept': 'application/json, text/plain, */*',
									'Origin': 'https://www.ryanair.com',
									'Content-Type': 'application/json',
								})
								if self.RCR.request_to_post(is_redirect=True, page_type='json'):
									# 提取货币
									self.CPR.currency, temp_list = self.BPR.parse_to_path(
										"$..currency", self.RCR.page_source)
									# self.logger.info(self.CPR.currency)
									return True
								
								self.logger.info(f"座位提交失败： {count + 1} (*>﹏<*)【{self.RCR.url}】")
								self.callback_msg = f"座位提交失败： {count + 1} (*>﹏<*)【{self.RCR.url}】"
								return False
			
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
			# 行李页面
			self.RCR.url = "https://www.ryanair.com/cn/zh/trip/flights/bags"
			self.RCR.param_data = (
				('tpAdults', self.CPR.adult_num),
				('tpTeens', '0'),
				('tpChildren', self.CPR.child_num),
				('tpInfants', '0'),
				('tpStartDate', self.CPR.flight_date),
				('tpEndDate', ''),
				('tpOriginIata', self.CPR.departure_code),
				('tpDestinationIata', self.CPR.arrival_code),
				('tpIsConnectedFlight', 'false'),
				('tpIsReturn', 'false'),
				('tpDiscount', '0'),
			)
			self.RCR.post_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "www.ryanair.com",
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
				"Sec-Fetch-Mode": "navigate",
				"Content-Type": "application/x-www-form-urlencoded",
				"Origin": "https://booking.flypeach.com",
				"Referer": self.temp_url,
				"Upgrade-Insecure-Requests": "1"
			})
			if self.RCR.request_to_get(is_redirect=True):
				
				self.temp_url = self.BFR.format_to_same(self.RCR.response_url)
				self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
				self.RCR.param_data = None
				self.RCR.post_data = '''{"query":"query GetBasket($basketId: String!, $isGettingAroundAvailable: Boolean!, $isThingsToDoAvailable: Boolean!) {\n  basket(id: $basketId) {\n    ...BasketCommon\n    gettingAround @include(if: $isGettingAroundAvailable) {\n      ...GettingAroundPillar\n    }\n    thingsToDo @include(if: $isThingsToDoAvailable) {\n      ...ThingsToDoPillar\n    }\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n\nfragment GettingAroundPillar on GettingAroundType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    payLater {\n      amountWithTaxes\n      total\n    }\n    variant {\n      ...VariantCar\n      ...VariantCarRental\n      ...VariantGroundTransfer\n    }\n  }\n}\n\nfragment VariantCar on VariantUnionType {\n  ... on Car {\n    rentPrice\n    carName\n    refId\n    engineLoadId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n    }\n    residence\n    age\n  }\n}\n\nfragment VariantCarRental on VariantUnionType {\n  ... on CarRental {\n    rentPrice\n    carName\n    refId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n      payNow\n    }\n    residence\n    age\n    searchId\n  }\n}\n\nfragment ThingsToDoPillar on ThingsToDoType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    variant {\n      ... on Ticket {\n        name\n        reservationCode\n        activityTime\n        address\n      }\n    }\n  }\n}\n","variables":{"basketId":"''' + self.basketId + '''","isGettingAroundAvailable":true,"isThingsToDoAvailable":true},"operationName":"GetBasket"}'''
				self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					'Origin': 'https://www.ryanair.com',
					'Host': 'basketapi.ryanair.com',
					'Content-Type': 'application/json',
					'Accept': 'application/json, text/plain, */*',
				})
				if self.RCR.request_to_post(is_redirect=True, page_type='json'):
					
					self.RCR.url = "https://catalogapi.ryanair.com/api/zh-cn/graphql"
					self.RCR.param_data = None
					self.RCR.post_data = '''{"query":"query ProductsQuery($basketId: String!, $products: [Product]!, $query: FlightExtrasQuery) {\n  cabinBags(basketId: $basketId) {\n    ...CabinBagFrag\n  }\n  priorityBoarding(basketId: $basketId) {\n    code\n    price\n    paxType\n    journeyNumber\n    segmentNumber\n  }\n  bags(basketId: $basketId) {\n    ...BagFrag\n  }\n  flightExtras(basketId: $basketId, products: $products, query: $query) {\n    ...ExtraFrag\n  }\n}\n\nfragment CabinBagFrag on CabinBag {\n  journeyNum\n  maxPerPassenger\n  offers {\n    ...CabinBagOfferFrag\n  }\n}\n\nfragment CabinBagOfferFrag on CabinBagOffer {\n  code\n  price {\n    ...CabinBagOfferPriceFrag\n  }\n}\n\nfragment CabinBagOfferPriceFrag on CabinBagOfferPrice {\n  paxNum\n  paxType\n  total\n}\n\nfragment BagFrag on Bag {\n  journeyNum\n  maxPerPassenger\n  offers {\n    ...BagOfferFrag\n  }\n}\n\nfragment BagOfferFrag on BagOffer {\n  code\n  price {\n    ...BagOfferPriceFrag\n  }\n}\n\nfragment BagOfferPriceFrag on BagOfferPrice {\n  discountPercentage\n  discountType\n  originalPrice\n  paxType\n  total\n  totalDiscount\n}\n\nfragment ExtraFrag on FlightExtra {\n  code\n  discountPercentage\n  discountType\n  minOriginalPrice\n  minPrice\n  totalDiscount\n  priceDetails {\n    journeyNumber\n    segmentNumber\n    minPrice\n    minOriginalPrice\n    discountType\n    totalDiscount\n    dsc\n  }\n}\n","variables":{"basketId":"''' + self.basketId + '''","products":["PRIOBRDNG","BAGS","CBAG"]}}'''
					self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Origin': 'https://www.ryanair.com',
						'Host': 'catalogapi.ryanair.com',
						'Content-Type': 'application/json',
						'Accept': 'application/json, text/plain, */*',
					})
					if self.RCR.request_to_post(is_redirect=True, page_type='json'):
						
						self.RCR.url = "https://personapi.ryanair.com/api/zh-cn/graphql"
						self.RCR.param_data = None
						self.RCR.post_data = '''{"query":"query GetPassengers($basketId: String!) {\n  passengers(basketId: $basketId) {\n    ...PassengersResponse\n  }\n}\n\nfragment PassengersResponse on PassengersResponse {\n  passengers {\n    ...PassengersPassenger\n  }\n}\n\nfragment PassengersPassenger on Passenger {\n  paxNum\n  type\n  title\n  first\n  middle\n  last\n  dob\n  inf {\n    ...PassengersInfant\n  }\n  specialAssistance {\n    ...PassengersPassengerPrmSsrType\n  }\n}\n\nfragment PassengersInfant on Infant {\n  first\n  middle\n  last\n  dob\n}\n\nfragment PassengersPassengerPrmSsrType on PassengerPrmSsrType {\n  codes\n  journeyNum\n  segmentNum\n}\n","variables":{"basketId":"''' + self.basketId + '''"}}'''
						self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							'Origin': 'https://www.ryanair.com',
							'Host': 'personapi.ryanair.com',
							'Content-Type': 'application/json',
							'Accept': 'application/json, text/plain, */*',
						})
						if self.RCR.request_to_post(is_redirect=True, page_type='json'):
							# 添加行李
							if self.baggage_parameters():
								return True
							else:
								return False
			
			# # # 错误重试。
			self.logger.info(f"服务第{count + 1}次超时或者错误(*>﹏<*)【service】")
			self.callback_msg = f"请求服务第{count + 1}次超时"
			return self.process_to_service(count + 1, max_count)
	
	def process_to_other_services(self, count: int = 0, max_count: int = 1) -> bool:
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
			# 确认航班信息， 航班， 乘客， 行李， 价格
			self.RCR.url = "https://www.ryanair.com/cn/zh/trip/flights/extras"
			self.RCR.param_data = (
				('tpAdults', self.CPR.adult_num),
				('tpTeens', '0'),
				('tpChildren', self.CPR.child_num),
				('tpInfants', '0'),
				('tpStartDate', self.CPR.flight_date),
				('tpEndDate', ''),
				('tpOriginIata', self.CPR.departure_code),
				('tpDestinationIata', self.CPR.arrival_code),
				('tpIsConnectedFlight', 'false'),
				('tpIsReturn', 'false'),
				('tpDiscount', '0'),
			)
			self.RCR.post_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "www.ryanair.com",
				'Referer': self.temp_url,
				'Upgrade-Insecure-Requests': '1',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			})
			if self.RCR.request_to_get(is_redirect=True):
				
				self.temp_url = self.BFR.format_to_same(self.RCR.response_url)
				self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
				self.RCR.param_data = None
				self.RCR.post_data = '''{"query":"query GetBasket($basketId: String!, $isGettingAroundAvailable: Boolean!, $isThingsToDoAvailable: Boolean!) {\n  basket(id: $basketId) {\n    ...BasketCommon\n    gettingAround @include(if: $isGettingAroundAvailable) {\n      ...GettingAroundPillar\n    }\n    thingsToDo @include(if: $isThingsToDoAvailable) {\n      ...ThingsToDoPillar\n    }\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n\nfragment GettingAroundPillar on GettingAroundType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    payLater {\n      amountWithTaxes\n      total\n    }\n    variant {\n      ...VariantCar\n      ...VariantCarRental\n      ...VariantGroundTransfer\n    }\n  }\n}\n\nfragment VariantCar on VariantUnionType {\n  ... on Car {\n    rentPrice\n    carName\n    refId\n    engineLoadId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n    }\n    residence\n    age\n  }\n}\n\nfragment VariantCarRental on VariantUnionType {\n  ... on CarRental {\n    rentPrice\n    carName\n    refId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n      payNow\n    }\n    residence\n    age\n    searchId\n  }\n}\n\nfragment ThingsToDoPillar on ThingsToDoType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    variant {\n      ... on Ticket {\n        name\n        reservationCode\n        activityTime\n        address\n      }\n    }\n  }\n}\n","variables":{"basketId":"''' + self.basketId + '''","isGettingAroundAvailable":true,"isThingsToDoAvailable":true},"operationName":"GetBasket"}'''
				self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					'Origin': 'https://www.ryanair.com',
					'Host': 'basketapi.ryanair.com',
					'Content-Type': 'application/json',
					'Accept': 'application/json, text/plain, */*',
				})
				if self.RCR.request_to_post(is_redirect=True, page_type='json'):
					
					# 获取航班价格， 乘客信息， 行李信息， 对比航班号
					self.temp_source = self.BFR.format_to_same(self.RCR.page_source)
					self.total_price, temp_list = self.BPR.parse_to_path('$...total', self.temp_source)
					
					# # # 提取行李价格
					final_result, result_list = self.BPR.parse_to_path(
						"$...components", self.temp_source)
					
					# # # 遍历成人行李信息
					for n, v in enumerate(self.CPR.adult_list):  # 遍历成人乘客信息
						for i in final_result:  # 遍历行李价格
							for x in v.get('baggage'):  # 遍历每个乘客的行李参数
								
								# 判断行李规格， 目前 FR 支持两种规格， 10 公斤 1 份， 20 公斤最多 3 份
								if i.get('quantity') == 1 and n == i.get('variant').get(
										'paxNumber') and i.get('type') == "CABIN_BAG" and x.get('weight') == 10:
									x['price'] = i.get('price').get('amountWithTaxes')
									self.CPR.return_baggage.append(x)
								
								# 行李规格 20
								elif i.get('quantity') == int(int(x.get('weight')) / 20) and n == i.get('variant').get(
										'paxNumber') and i.get('type') == "BAG" and x.get('weight') >= 20:
									x['price'] = i.get('price').get('amountWithTaxes')
									self.CPR.return_baggage.append(x)
								else:
									self.callback_msg = f"行李规格有误 | {x}"
					
					# 票价及其他费用， 不包含行李的价格
					if final_result:
						for i in final_result:
							if i.get('type') == "FARE":
								self.return_price = self.BFR.format_to_float(2, i.get('price').get('amountWithTaxes'))
					
					# # # # 计算最终返回价格，不含行李价格。
					# if self.baggage_price:
					#     self.baggage_price = self.BFR.format_to_float(2, self.baggage_price)
					#     self.return_price = self.total_price - self.baggage_price
					#     self.return_price = self.BFR.format_to_float(2, self.return_price)
					# else:
					#     self.return_price = self.total_price
					# self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
					# # # # 比价格是否要继续支付。
					# if self.process_to_compare():
					self.RCR.url = "https://catalogapi.ryanair.com/api/zh-cn/graphql"
					self.RCR.param_data = None
					self.RCR.post_data = '''{"variables":{"basketId":"''' + self.basketId + '''"},"query":"query FligthExtrasQuery($basketId: String!) {\n  flightExtras(basketId: $basketId, products: [FAST, INSURANCE, PARKING, EQUIPMENT, SEATS, BAGS, CBAG, PRIOBRDNG, INFLIGHT]) {\n    ...ExtraFrag\n  }\n}\n\nfragment ExtraFrag on FlightExtra {\n  code\n  maxPerPassenger\n  minPrice\n  priceDetails {\n    journeyNumber\n  }\n}\n"}'''
					self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Origin': 'https://www.ryanair.com',
						'Host': 'catalogapi.ryanair.com',
						'Content-Type': 'application/json',
						'Accept': 'application/json, text/plain, */*',
					})
					if self.RCR.request_to_post(is_redirect=True, page_type='json'):
						
						self.RCR.url = "https://catalogapi.ryanair.com/api/zh-cn/graphql"
						self.RCR.param_data = None
						self.RCR.post_data = '''{"query":"query FligthExtrasDesktopQuery($basketId: String!) {\n  fastTracks(basketId: $basketId) {\n    ...FastTrackFrag\n  }\n  flightExtras(basketId: $basketId, products: [FAST, INSURANCE, PARKING, INFLIGHT, PRES]) {\n    ...ExtraFrag\n  }\n  parking(basketId: $basketId) {\n    code\n  }\n}\n\nfragment ExtraFrag on FlightExtra {\n  code\n  discountPercentage\n  discountType\n  minOriginalPrice\n  minPrice\n  totalDiscount\n}\n\nfragment FastTrackFrag on FastTrack {\n  code\n  journeyNum\n  paxType\n  price\n}\n","variables":{"basketId":"''' + self.basketId + '''"}}'''
						self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							'Origin': 'https://www.ryanair.com',
							'Host': 'catalogapi.ryanair.com',
							'Content-Type': 'application/json',
							'Accept': 'application/json, text/plain, */*',
						})
						if self.RCR.request_to_post(is_redirect=True, page_type='json'):
							
							self.RCR.url = "https://www.ryanair.com/cn/zh/trip"
							self.RCR.param_data = (
								('tpAdults', self.CPR.adult_num),
								('tpTeens', '0'),
								('tpChildren', self.CPR.child_num),
								('tpInfants', '0'),
								('tpStartDate', self.CPR.flight_date),
								('tpEndDate', ''),
								('tpOriginIata', self.CPR.departure_code),
								('tpDestinationIata', self.CPR.arrival_code),
								('tpIsConnectedFlight', 'false'),
								('tpIsReturn', 'false'),
								('tpDiscount', '0'),
							)
							self.RCR.post_data = None
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								'Upgrade-Insecure-Requests': '1',
								'Sec-Fetch-User': '?1',
								'Host': 'www.ryanair.com',
								'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
								'Referer': self.temp_url,
							})
							if self.RCR.request_to_get(is_redirect=False):
								self.temp_url = self.BFR.format_to_same(self.RCR.response_url)
								# 进行登录
								if self.login_account():
									self.RCR.url = "https://api.ryanair.com/usrprof/v2/loggedin"
									self.RCR.param_data = None
									self.RCR.post_data = None
									self.RCR.header = self.BFR.format_to_same(self.init_header)
									self.RCR.header.update({
										'Host': 'api.ryanair.com',
										'Accept': 'application/json, text/plain, */*',
										'Origin': 'https://www.ryanair.com',
									})
									if self.RCR.request_to_get(is_redirect=True, page_type='json'):
										
										self.customerId, temp_list = self.BPR.parse_to_path('$.customerId',
										                                                    self.RCR.page_source)
										self.RCR.url = f"https://api.ryanair.com/usrprof/v2/customers/{self.customerId}/travelCredits"
										self.RCR.param_data = None
										self.RCR.post_data = None
										self.RCR.header = self.BFR.format_to_same(self.init_header)
										self.RCR.header.update({
											'Host': 'api.ryanair.com',
											'Accept': 'application/json, text/plain, */*',
											'Origin': 'https://www.ryanair.com',
										})
										if self.RCR.request_to_get(is_redirect=True, page_type='json'):
											
											self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
											self.RCR.param_data = None
											self.RCR.post_data = '''{"query":"query GetBasket($basketId: String!, $isGettingAroundAvailable: Boolean!, $isThingsToDoAvailable: Boolean!) {\n  basket(id: $basketId) {\n    ...BasketCommon\n    gettingAround @include(if: $isGettingAroundAvailable) {\n      ...GettingAroundPillar\n    }\n    thingsToDo @include(if: $isThingsToDoAvailable) {\n      ...ThingsToDoPillar\n    }\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n\nfragment GettingAroundPillar on GettingAroundType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    payLater {\n      amountWithTaxes\n      total\n    }\n    variant {\n      ...VariantCar\n      ...VariantCarRental\n      ...VariantGroundTransfer\n    }\n  }\n}\n\nfragment VariantCar on VariantUnionType {\n  ... on Car {\n    rentPrice\n    carName\n    refId\n    engineLoadId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n    }\n    residence\n    age\n  }\n}\n\nfragment VariantCarRental on VariantUnionType {\n  ... on CarRental {\n    rentPrice\n    carName\n    refId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n      payNow\n    }\n    residence\n    age\n    searchId\n  }\n}\n\nfragment ThingsToDoPillar on ThingsToDoType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    variant {\n      ... on Ticket {\n        name\n        reservationCode\n        activityTime\n        address\n      }\n    }\n  }\n}\n","variables":{"basketId":"''' + self.basketId + '''","isGettingAroundAvailable":true,"isThingsToDoAvailable":true},"operationName":"GetBasket"}'''
											self.RCR.header = self.BFR.format_to_same(self.init_header)
											self.RCR.header.update({
												'Host': 'basketapi.ryanair.com',
												'Accept': 'application/json, text/plain, */*',
												'Origin': 'https://www.ryanair.com',
												'Content-Type': 'application/json',
											})
											if self.RCR.request_to_post(is_redirect=True, page_type='json'):
												return True
								
								else:
									return False
			
			# # # 获取支付需要的参数。
			self.callback_msg = f"请求支付第{count + 1}次超时，请重试。"
			return self.process_to_other_services(count + 1, max_count)
	
	def process_to_payment(self, count: int = 0, max_count: int = 1) -> bool:
		'''
		支付过程
		Args:
			count:
			max_count:

		Returns:

		'''
		if count >= max_count:
			return False
		
		self.RCR.url = "https://www.ryanair.com/cn/zh/booking/active?confirmation=true"
		self.RCR.param_data = None
		self.RCR.post_data = None
		self.RCR.header = self.BFR.format_to_same(self.init_header)
		self.RCR.header.update({
			'Host': 'www.ryanair.com',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Referer': 'https://www.ryanair.com/cn/zh/payment',
			'Upgrade-Insecure-Requests': '1',
		})
		if self.RCR.request_to_get(is_redirect=True):
			
			# 获取 pnr ， 获取订单状态
			self.RCR.url = "https://www.ryanair.com/api/booking/v4/zh-cn/Refresh"
			self.RCR.param_data = None
			self.RCR.post_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				'Host': 'www.ryanair.com',
				'Upgrade-Insecure-Requests': '1',
				'Referer': 'https://www.ryanair.com/cn/zh/booking/active?confirmation=true',
				'X-Session-Token': self.sessionId,
			})
			if self.RCR.request_to_get(is_redirect=True, page_type='json'):
				return True
		
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
		               f"foreignCurrency={self.CPR.currency}&carrier=FR"
		self.RCR.param_data = None
		self.RCR.header = self.BFR.format_to_same(self.init_header)
		self.RCR.post_data = None
		if self.RCR.request_to_get("json"):
			# # # 解析汇率转换人民币价格。
			exchange = self.RCR.page_source.get(self.CPR.currency)
			exchange_price = self.BFR.format_to_float(2, self.total_price * exchange)
			if not exchange or not exchange_price:
				self.logger.info(f"转换汇率价格失败(*>﹏<*)【{self.RCR.page_source}】")
				self.callback_msg = "转换汇率价格失败，请通知技术检查程序。"
				return False
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
			
			# 进行支付
			if self.payment_page():  # 支付请求
				
				# 登录后，获取token
				self.RCR.url = f"https://api.ryanair.com/usrprof/v2/accounts/{self.customerId}/sessionToken"
				self.RCR.param_data = None
				self.RCR.post_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					'Host': 'api.ryanair.com',
					'Accept': 'application/json, text/plain, */*',
					'Origin': 'https://www.ryanair.com',
				})
				if self.RCR.request_to_get(is_redirect=True, page_type='json'):
					
					self.token, temp_list = self.BPR.parse_to_path('$.token',
					                                               self.RCR.page_source)
					if not self.token:
						self.logger.info(f"提取 token 失败(*>﹏<*) | {self.RCR.url}")
						self.callback_msg = f"提取 token 失败(*>﹏<*)|{self.RCR.url}"
						return False
					# self.logger.info(self.token)
					self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
					self.RCR.param_data = None
					self.RCR.post_data = '''{"query":"query GetBasket($basketId: String!, $isGettingAroundAvailable: Boolean!, $isThingsToDoAvailable: Boolean!) {\n  basket(id: $basketId) {\n    ...BasketCommon\n    gettingAround @include(if: $isGettingAroundAvailable) {\n      ...GettingAroundPillar\n    }\n    thingsToDo @include(if: $isThingsToDoAvailable) {\n      ...ThingsToDoPillar\n    }\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n\nfragment GettingAroundPillar on GettingAroundType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    payLater {\n      amountWithTaxes\n      total\n    }\n    variant {\n      ...VariantCar\n      ...VariantCarRental\n      ...VariantGroundTransfer\n    }\n  }\n}\n\nfragment VariantCar on VariantUnionType {\n  ... on Car {\n    rentPrice\n    carName\n    refId\n    engineLoadId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n    }\n    residence\n    age\n  }\n}\n\nfragment VariantCarRental on VariantUnionType {\n  ... on CarRental {\n    rentPrice\n    carName\n    refId\n    pickUpTime\n    pickUpLocation {\n      countryCode\n      code\n      name\n    }\n    dropOffTime\n    dropOffLocation {\n      countryCode\n      code\n      name\n    }\n    insurance\n    extras {\n      totalPrice\n      includedInRate\n      code\n      price\n      selected\n      type\n      payNow\n    }\n    residence\n    age\n    searchId\n  }\n}\n\nfragment ThingsToDoPillar on ThingsToDoType {\n  ...PillarCommon\n  price {\n    amount\n    discount\n    amountWithTaxes\n    total\n  }\n  taxes {\n    amount\n  }\n  components {\n    ...ComponentCommon\n    variant {\n      ... on Ticket {\n        name\n        reservationCode\n        activityTime\n        address\n      }\n    }\n  }\n}\n","variables":{"basketId":"''' + self.basketId + '''","isGettingAroundAvailable":true,"isThingsToDoAvailable":true},"operationName":"GetBasket"}'''
					self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Origin': 'https://www.ryanair.com',
						'Host': 'basketapi.ryanair.com',
						'Content-Type': 'application/json',
						'Accept': 'application/json, text/plain, */*',
					})
					if self.RCR.request_to_post(is_redirect=True, page_type='json'):
						
						self.RCR.url = f"https://api.ryanair.com/usrprof/v2/customers/{self.customerId}/travelCredits"
						self.RCR.param_data = None
						self.RCR.post_data = None
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							'Host': 'api.ryanair.com',
							'Accept': 'application/json, text/plain, */*',
							'Origin': 'https://www.ryanair.com',
						})
						if self.RCR.request_to_get(is_redirect=True, page_type='json'):
							
							self.RCR.url = "https://catalogapi.ryanair.com/zh-cn/graphql"
							self.RCR.param_data = None
							self.RCR.post_data = '''{"query":"query InsuranceQuery($basketId: String!, $queries: [InsuranceQuery]!)\n  {\n    insurances(basketId: $basketId, queries: $queries) {\n      country\n      paxNum\n      offers {\n        code\n        offerKey\n        price\n        skuKey\n      }\n    }\n  }","variables":{"basketId":"''' + self.basketId + '''","queries":[{"country":"IT","paxNum":0,"insuranceTypes":["PLUS"]}]}}'''
							self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
							self.RCR.header = self.BFR.format_to_same(self.init_header)
							self.RCR.header.update({
								'Origin': 'https://www.ryanair.com',
								'Host': 'catalogapi.ryanair.com',
								'Content-Type': 'application/json',
								'Accept': 'application/json, text/plain, */*',
							})
							if self.RCR.request_to_post(is_redirect=True, page_type='json'):
								
								self.RCR.url = "https://paymentapi.ryanair.com/zh-cn/paymentMethods?basketId=" + self.basketId
								self.RCR.param_data = None
								self.RCR.post_data = None
								self.RCR.header = self.BFR.format_to_same(
									self.init_header)
								self.RCR.header.update({
									'Origin': 'https://www.ryanair.com',
									'Host': 'paymentapi.ryanair.com',
									'Content-Type': 'application/json',
									'Accept': 'application/json, text/plain, */*',
								})
								if self.RCR.request_to_get(is_redirect=True):
									pass
								
								#### 支付
								temp = {
									"accountNumber": self.CPR.card_num,  # 银行卡号
									"basketId": self.basketId,
									"myRyanairCustomerId": self.customerId,
									"myRyanairToken": self.token
								}
								
								self.RCR.url = "https://paymentapi.ryanair.com/zh-cn/currencyConversion/getOptions"
								self.RCR.param_data = None
								self.RCR.post_data = str(temp).replace(' ', '')
								self.RCR.header = self.BFR.format_to_same(self.init_header)
								self.RCR.header.update({
									'Host': 'paymentapi.ryanair.com',
									'Accept': 'application/json, text/plain, */*',
									'Origin': 'https://www.ryanair.com',
									'Content-Type': 'application/json',
								})
								if self.RCR.request_to_post(is_redirect=True, page_type='json'):
									
									# 计算手续费
									handling_fee, handling_fee_list = self.BPR.parse_to_path(
										'$..feeValue',
										self.RCR.page_source)
									if not handling_fee:
										self.logger.info(f"获取手续费失败 (*>﹏<*) | {self.RCR.url}")
										self.callback_msg = f"获取手续费失败 (*>﹏<*) | {self.RCR.url}"
										return False
									
									# self.logger.info(handling_fee)
									self.return_price = self.BFR.format_to_float(2,
									                                             self.return_price) + self.BFR.format_to_float(
										2, handling_fee)
									# self.logger.info(self.return_price)
									
									# # # # 进行比价
									if self.process_to_compare() == False:
										return False
									
									card_code = self.AFR.decrypt_into_aes(
										self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.card_code)
									if not card_code:
										self.logger.info(f"解密支付卡失败(*>﹏<*)【{self.CPR.card_code}】")
										self.callback_msg = "解密支付卡失败，请通知技术检查程序。"
										return False
									
									self.CPR.contact_mobile = '17776014856'
									data = {
										"basketId": self.basketId,
										"myRyanairToken": self.token,
										"myRyanairCustomerId": self.customerId,
										"agreeNewsletters": "true",
										"payment": {
											"contact": {
												"email": self.CPR.contact_email,
												"phoneNumber": self.CPR.contact_mobile,
												"phoneCode": 86,
												"countryCode": "CN"
											},
											"threeDsIFrameSize": 5,
											"accountNumber": self.CPR.card_num,
											# "6250760009388151",  # self.CPR.card_num,   # 银行卡号
											"accountName": self.CPR.card_last + self.CPR.card_first,  # "ZHAOCONGCONG",
											"verificationCode": card_code,  # self.CPR.card_code,      # 支付卡验证码
											"expiration": f"20{self.CPR.card_date[:2]}-{self.CPR.card_date[2:]}-01",
											# 支付卡到期时间  2022-02-01
											# f"20{self.CPR.card_date[:2]}-{self.CPR.card_date[2:]}-01",
											"paymentMethodCode": "DS",
											"address": {
												"city": "BEIJING",
												"line1": "BEIJING",
												"line2": "BEIJING",
												"country": "CN",
												"postal": "100000"
											},
											"currencyConversion": {
												"foreignCurrencyCode": "USD",
												"currencyConversionId": ""
											}
										}
									}
									
									self.RCR.url = "https://paymentapi.ryanair.com/zh-cn/payment"
									self.RCR.param_data = None
									self.RCR.post_data = str(data).replace('\"true\"', 'true').replace(' ', '').replace(
										'\'', '\"')
									self.RCR.header = self.BFR.format_to_same(self.init_header)
									self.RCR.header.update({
										'Host': 'paymentapi.ryanair.com',
										'Accept': 'application/json, text/plain, */*',
										'Origin': 'https://www.ryanair.com',
										'Content-Type': 'application/json',
									})
									if self.RCR.request_to_post(is_redirect=True, page_type='json'):
										
										payment_id, temp_list = self.BPR.parse_to_path('$.paymentId',
										                                               self.RCR.page_source)
										self.RCR.url = f"https://paymentapi.ryanair.com/payment/status?paymentId={payment_id}&waitTimeSeconds=50"
										self.RCR.param_data = None
										self.RCR.post_data = None
										self.RCR.header = self.BFR.format_to_same(self.init_header)
										self.RCR.header.update({
											'Host': 'paymentapi.ryanair.com',
											'Accept': 'application/json, text/plain, */*',
											'Origin': 'https://www.ryanair.com',
										})
										if self.RCR.request_to_get(is_redirect=True, page_type='json'):
											
											# 判断支付状态
											# Completed  成功
											payment_status, status_list = self.BPR.parse_to_path('$.status',
											                                                     self.RCR.page_source)
											if payment_status == "Completed":
												
												if self.process_to_payment():
													# 判断机票状态
													# 正确的机票状态 Confirmed
													order_status, status_list = self.BPR.parse_to_path('$.status',
													                                                   self.RCR.page_source)
													if order_status == "Confirmed":
														# # # 提取 PNR。
														self.record, temp_list = self.BPR.parse_to_path('$.pnr',
														                                                self.RCR.page_source)
														self.record = self.BPR.parse_to_clear(self.record)
														
														if not self.record:
															self.logger.info(f"获取 PNR 失败 或者支付失败 | 机票状态: {order_status}")
															self.callback_msg = f"获取 PNR 失败 或者支付失败 | 机票状态: {order_status}"
															self.callback_data["orderIdentification"] = 2
															return False
													else:
														self.logger.info(f"机票状态有误 (*>﹏<*)【{order_status}")
														self.callback_msg = f"机票状态有误 (*>﹏<*)【{order_status}"
														self.callback_data["orderIdentification"] = 2
														return False
												else:
													return False
											else:
												# errorMessage
												error, temp_list = self.BPR.parse_to_path('$.errorMessage',
												                                          self.RCR.page_source)
												self.logger.info(f"支付失败 (*>﹏<*)【{error}】 | 支付状态： {payment_status}")
												self.callback_msg = f"支付失败 (*>﹏<*)【{error}】 | 支付状态： {payment_status}"
												self.callback_data["orderIdentification"] = 2
												return False
											
											return True
			
			return False
	
	def login_account(self, count: int = 0, max_count: int = 2) -> bool:
		'''
		进行登录
		Returns:
		'''
		if count >= max_count:
			return False
		else:
			
			password = self.AFR.decrypt_into_aes(
				self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.password)
			
			self.RCR.url = "https://api.ryanair.com/usrprof/rest/api/v1/login"
			self.RCR.param_data = None
			self.RCR.post_data = {
				'username': self.CPR.username,
				'password': password,
				'policyAgreed': 'true'
			}
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				'Host': 'api.ryanair.com',
				'Origin': 'https://www.ryanair.com',
				'Content-Type': 'application/x-www-form-urlencoded',
				'Accept': 'application/json, text/plain, */*',
			})
			if self.RCR.request_to_post(is_redirect=True, page_type='json'):
				if "customerId" in str(self.RCR.page_source):
					return True
				else:
					error, temp_list = self.BPR.parse_to_path('$.message', self.RCR.page_source)
					self.callback_msg = f"登录失败 {self.RCR.url} | 异常信息： {error}"
					return False
			
			self.callback_msg = f"登录失败 {self.RCR.url}"
			return self.login_account(count + 1, max_count)
	
	def availability(self, count: int = 0, max_count: int = 2) -> bool:
		'''
		获取 Key， 获取航班信息参数
		Args:
			count:
			max_count:

		Returns:

		'''
		if count >= max_count:
			return False
		else:
			
			self.RCR.set_to_cookies(include_domain=False, cookie_list=
			[
				{'name': 's_cc', 'value': 'true'},
				{'name': '_hjIncludedInSample', 'value': '1'},
			]
			                        )
			self.RCR.url = "https://www.ryanair.com/api/booking/v4/zh-cn/availability"
			self.RCR.param_data = (
				('ADT', self.CPR.adult_num),
				('CHD', self.CPR.child_num),
				('DateIn', ''),
				('DateOut', self.CPR.flight_date),
				('Destination', self.CPR.arrival_code),
				('Disc', '0'),
				('INF', '0'),
				('Origin', self.CPR.departure_code),
				('RoundTrip', 'false'),
				('TEEN', '0'),
				('FlexDaysIn', '2'),
				('FlexDaysBeforeIn', '2'),
				('FlexDaysOut', '2'),
				('FlexDaysBeforeOut', '2'),
				('ToUs', 'AGREED'),
				('IncludeConnectingFlights', 'false'),
			)
			self.RCR.post_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "application/json, text/plain, */*",
				"Upgrade-Insecure-Requests": "1",
				'referer': self.RCR.response_url
			})
			if self.RCR.request_to_get(is_redirect=True, page_type='json'):
				return True
			
			self.callback_msg = f"获取航班号失败 {self.RCR.url}"
			return self.availability(count + 1, max_count)
	
	def submit_flight(self, count: int = 0, max_count: int = 3) -> bool:
		'''
		提交航班
		Args:
			count:
			max_count:

		Returns:

		'''
		if count >= max_count:
			return False
		else:
			
			self.RCR.url = "https://www.ryanair.com/api/booking/v5/zh-cn/FareOptions"
			self.RCR.param_data = (
				('OutboundFlightKey', self.flightKey),
				('OutboundFareKey', self.fareKey),
				('AdultsCount', self.CPR.adult_num),
				('ChildrenCount', self.CPR.child_num),
				('InfantCount', '0'),
				('TeensCount', '0'),
			)
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				'Referer': self.temp_url,
				'Accept': 'application/json, text/plain, */*',
				'Host': 'www.ryanair.com',
			})
			if self.RCR.request_to_get(is_redirect=True, page_type='json'):
				
				# 创建预订
				self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
				self.RCR.param_data = None
				self.RCR.post_data = '''{"query":"mutation CreateBooking($basketId: String, $createBooking: CreateBookingInput!, $culture: String!) {\n  createBooking(basketId: $basketId, createBooking: $createBooking, culture: $culture) {\n    ...BasketCommon\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n","variables":{"createBooking":{"adults":''' + str(
					self.CPR.adult_num) + ''',"children":''' + str(
					self.CPR.child_num) + ''',"infants":0,"teens":0,"flights":[{"flightKey":"''' + self.flightKey + '''","fareKey":"''' + self.fareKey + '''","fareOption":null}],"discount":0},"culture":"zh-cn"},"operationName":"CreateBooking"}'''
				self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					'Content-Type': 'application/json',
					'Accept': 'application/json, text/plain, */*',
					'Origin': 'https://www.ryanair.com',
					'Sec-Fetch-Site': 'same-site',
					'Sec-Fetch-Mode': 'cors',
				})
				if self.RCR.request_to_post(is_redirect=True, page_type='json'):
					
					self.basketId, temp_list = self.BPR.parse_to_path('$..id', self.RCR.page_source)
					if not self.basketId:
						self.callback_msg = f"basketId 提交参数获取失败 {self.RCR.url}"
						return False
					# 提交预订
					self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
					self.RCR.param_data = None
					self.RCR.post_data = '''{"query":"mutation CommitBooking($basketId: String!) {\n  commitBooking(basketId: $basketId) {\n    ...BasketCommon\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n","variables":{"basketId":"''' + self.basketId + '''"},"operationName":"CommitBooking"}'''
					self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						'Host': 'basketapi.ryanair.com',
						'Content-Type': 'application/json',
						'Accept': 'application/json, text/plain, */*',
						'Origin': 'https://www.ryanair.com',
						'Sec-Fetch-Site': 'same-site',
						'Sec-Fetch-Mode': 'cors',
					})
					if self.RCR.request_to_post(is_redirect=True, page_type='json'):
						
						self.sessionId, temp_list = self.BPR.parse_to_path('$..dotrezSessionId', self.RCR.page_source)
						if not self.sessionId:
							self.callback_msg = f"basketId 提交参数获取失败 {self.RCR.url}"
							return False
						
						self.RCR.url = "https://personapi.ryanair.com/api/zh-cn/graphql"
						self.RCR.param_data = None
						self.RCR.post_data = '''{"query":"query GetPassengers($basketId: String!) {\n  passengers(basketId: $basketId) {\n    ...PassengersResponse\n  }\n}\n\nfragment PassengersResponse on PassengersResponse {\n  passengers {\n    ...PassengersPassenger\n  }\n}\n\nfragment PassengersPassenger on Passenger {\n  paxNum\n  type\n  title\n  first\n  middle\n  last\n  dob\n  inf {\n    ...PassengersInfant\n  }\n  specialAssistance {\n    ...PassengersPassengerPrmSsrType\n  }\n}\n\nfragment PassengersInfant on Infant {\n  first\n  middle\n  last\n  dob\n}\n\nfragment PassengersPassengerPrmSsrType on PassengerPrmSsrType {\n  codes\n  journeyNum\n  segmentNum\n}\n","variables":{"basketId":"''' + self.basketId + '''"}}'''
						self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							'Host': 'personapi.ryanair.com',
							'Content-Type': 'application/json',
							'Accept': 'application/json, text/plain, */*',
							'Origin': 'https://www.ryanair.com',
							'Sec-Fetch-Site': 'same-site',
							'Sec-Fetch-Mode': 'cors',
						})
						if self.RCR.request_to_post(is_redirect=True, page_type='json'):
							return True
					
					self.callback_msg = f"提交航班预订信息失败 {self.RCR.url}"
					return self.submit_flight(count + 1, max_count)
			
			self.callback_msg = f"提交航班失败 {self.RCR.url}"
			return self.submit_flight(count + 1, max_count)
	
	def baggage_parameters(self, count: int = 0, max_count: int = 3) -> bool:
		'''
		解析行李信息，
		Args:
			count:
			max_count:

		Returns:

		'''
		if count >= max_count:
			return False
		
		else:
			
			# # # # 遍历每个成人具体的参数。
			for n, v in enumerate(self.CPR.adult_list):
				# # # 判断行李并累计公斤数。
				weight = v.get('baggage')
				kilogram = 0
				if weight:
					for w in weight:
						kilogram += self.BFR.format_to_int(w.get('weight'))
				# self.logger.info(f"{kilogram}")
				
				# # # 解析行李参数，只有件数，没有公斤数
				if kilogram:
					
					# if kilogram % 20 == 10 or kilogram % 20 == 0 and 10 < kilogram <= 70:
					# # 总公斤数除以20 的余数是否为 10, 或者 0
					# # FR 只支持 10 公斤 1 份， 20 公斤 最多 3 份
					if 10 <= kilogram <= 70:
						
						if kilogram % 20 == 0:  # 当余数为 0， 则添加 nums 个 20 公斤的行李
							nums = int(kilogram / 20)  # 件数
							for i in range(1, int(nums) + 1):
								self.RCR.post_data = '''{"query":"mutation AddBag($basketId: String!, $bags: [BagInputType]!) {\n  addBag(basketId: $basketId, bags: $bags) {\n    ...BasketCommon\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n","variables":{"basketId":"''' + self.basketId + '''","bags":[{"paxNum":''' + str(
									n) + ''',"qty":''' + str(
									i + 1) + ''',"journeyNum":0,"code":"BBG"}]},"operationName":"AddBag"}'''
								self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
								if self.add_bag() == False:
									return False
							
							return True
						
						elif kilogram % 20 == 10:
							
							# 添加 10 公斤
							self.RCR.post_data = '''{"query":"mutation AddCabinBag($basketId: String!, $cabinBags: [CabinBagInputType]!) {\n  addCabinBag(basketId: $basketId, cabinBags: $cabinBags) {\n    ...BasketCommon\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n","variables":{"basketId":"''' + self.basketId + '''","cabinBags":[{"paxNum":''' + str(
								n) + ''',"journeyNum":0}]},"operationName":"AddCabinBag"}'''
							self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
							if self.add_bag() == False:
								return False
							
							kilogram = kilogram - 10
							nums = int(kilogram / 20)  # 件数
							# self.logger.info(f"{kilogram}")
							if kilogram % 20 == 0:
								# 添加 20 公斤
								for i in range(1, int(nums) + 1):
									self.RCR.post_data = '''{"query":"mutation AddBag($basketId: String!, $bags: [BagInputType]!) {\n  addBag(basketId: $basketId, bags: $bags) {\n    ...BasketCommon\n  }\n}\n\nfragment BasketCommon on BasketType {\n  id\n  dotrezSessionId\n  currency\n  gettingThere {\n    ...GettingTherePillar\n  }\n  stayingThere {\n    ...StayingTherePillar\n  }\n  price {\n    ...TotalCommon\n  }\n  payLater {\n    ...PayLaterCommon\n  }\n}\n\nfragment GettingTherePillar on GettingThereType {\n  ...PillarCommon\n  journeys {\n    ... on JourneyType {\n      arrival\n      departure\n      destination\n      duration\n      fareClass\n      fareKey\n      fareOption\n      flightKey\n      flightNumber\n      isConnecting\n      isDomestic\n      journeyNum\n      origin\n      segments {\n        ... on SegmentType {\n          arrival\n          departure\n          destination\n          duration\n          flightNumber\n          segmentNum\n          origin\n        }\n      }\n    }\n  }\n  discounts {\n    ... on DiscountType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  taxes {\n    ... on TaxType {\n      amount\n      code\n      journeyNum\n      percentage\n      zone\n    }\n  }\n  components {\n    ... on ComponentType {\n      ...ComponentCommon\n      variant {\n        ...VariantUnionAddOn\n        ...VariantUnionFare\n        ...VariantUnionSsr\n        ...VariantUnionSeat\n        ...VariantGroundTransfer\n      }\n    }\n  }\n}\n\nfragment PillarCommon on PillarInterface {\n  price {\n    ...TotalCommon\n  }\n}\n\nfragment TotalCommon on PriceType {\n  total\n}\n\nfragment ComponentCommon on ComponentType {\n  id\n  parentId\n  code\n  type\n  quantity\n  removable\n  price {\n    ...PriceCommon\n  }\n}\n\nfragment PriceCommon on PriceType {\n  amountWithTaxes\n  total\n  discount\n  discountCode\n}\n\nfragment VariantUnionAddOn on VariantUnionType {\n  ... on AddOn {\n    itemId\n    provider\n    paxNumber\n    pax\n    src\n    start\n    end\n  }\n}\n\nfragment VariantUnionFare on VariantUnionType {\n  ... on Fare {\n    fareOption\n    journeyNumber\n  }\n}\n\nfragment VariantUnionSsr on VariantUnionType {\n  ... on Ssr {\n    journeyNumber\n    paxNumber\n    segmentNumber\n  }\n}\n\nfragment VariantUnionSeat on VariantUnionType {\n  ... on Seat {\n    paxNumber\n    journeyNumber\n    segmentNumber\n    seatType\n    designator\n    childSeatsWithAdult\n    hasAdditionalSeatCost\n  }\n}\n\nfragment VariantGroundTransfer on VariantUnionType {\n  ... on GroundTransfer {\n    pickUpLocation\n    dropOffLocation\n    routeType\n    startDate\n    endDate\n    itemId\n    location\n  }\n}\n\nfragment StayingTherePillar on StayingThereType {\n  ...PillarCommon\n  components {\n    ...ComponentCommon\n    price {\n      ...PriceCommon\n      fat\n      amount\n    }\n    payLater {\n      ...PriceCommon\n      fat\n      amount\n    }\n    variant {\n      ... on Hotel {\n        hotelName\n        reservationDescription\n        countryCode\n        city\n        startDate\n        endDate\n        provider\n        guestTotals {\n          adults\n          children\n        }\n      }\n    }\n  }\n  payLater {\n    total\n  }\n}\n\nfragment PayLaterCommon on PriceType {\n  total\n}\n","variables":{"basketId":"''' + self.basketId + '''","bags":[{"paxNum":''' + str(
										n) + ''',"qty":''' + str(
										i + 1) + ''',"journeyNum":0,"code":"BBG"}]},"operationName":"AddBag"}'''
									self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
									if self.add_bag() == False:
										return False
								
								return True
							
							else:
								self.logger.info(f"行李规格有误【{n}】【{v}】")
								self.callback_msg = f"行李规格有误【{n}】【{v}】"
								return False
						else:
							self.logger.info(f"行李规格有误【{n}】【{v}】")
							self.callback_msg = f"行李规格有误【{n}】【{v}】"
							return False
					
					else:
						self.logger.info(f"行李规格有误【{n}】【{v}】")
						self.callback_msg = f"行李规格有误【{n}】【{v}】"
						return False
				else:
					weight = ""
					self.logger.info(f"参数不包含行李【{n}】【{v}】")
					return True
			
			# # # # 遍历每个儿童具体的参数。
			if self.CPR.child_num:
				self.callback_msg = "FR | 包含儿童需要选座，暂时不做"
				return False
	
	def add_bag(self, count: int = 0, max_count: int = 2) -> bool:
		'''
		添加行李,
		Returns:

		'''
		if count >= max_count:
			return False
		
		self.RCR.url = "https://basketapi.ryanair.com/zh-cn/graphql"
		self.RCR.param_data = None
		self.RCR.header = self.BFR.format_to_same(self.init_header)
		self.RCR.header.update({
			'Origin': 'https://www.ryanair.com',
			'Host': 'basketapi.ryanair.com',
			'Content-Type': 'application/json',
			'Accept': 'application/json, text/plain, */*',
		})
		if self.RCR.request_to_post(is_redirect=True, page_type='json'):
			return True
		
		self.callback_msg = f"添加行李失败 {self.RCR.url}"
		return self.add_bag(count + 1, max_count)
	
	def payment_page(self, count: int = 0, max_count: int = 2) -> bool:
		'''
			   支付过程
			   Args:
				   count:
				   max_count:

			   Returns:

			   '''
		if count >= max_count:
			return False
		
		self.RCR.url = "https://www.ryanair.com/cn/zh/payment"
		self.RCR.param_data = None
		self.RCR.post_data = None
		self.RCR.header = self.BFR.format_to_same(self.init_header)
		self.RCR.header.update({
			"Host": "www.ryanair.com",
			'Referer': self.temp_url,
			'Upgrade-Insecure-Requests': '1',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		})
		if self.RCR.request_to_get(is_redirect=True):
			
			self.RCR.url = "https://catalogapi.ryanair.com/zh-cn/graphql"
			self.RCR.param_data = None
			self.RCR.post_data = '''{"query":"query FeesQuery($basketId: String!) {\n  fees(basketId: $basketId) {\n    amount\n    code\n  }\n}","variables":{"basketId":"''' + self.basketId + '''"}}'''
			self.RCR.post_data = self.RCR.post_data.replace('\n', '\\n')
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				'Host': 'catalogapi.ryanair.com',
				'Origin': 'https://www.ryanair.com',
				'Content-Type': 'application/json',
				'Accept': 'application/json, text/plain, */*',
			})
			if self.RCR.request_to_post(is_redirect=True, page_type='json'):
				return True
			
			self.callback_msg = f"费用查询失败 {self.RCR.url}"
			return self.payment_page(count + 1, max_count)
		
		self.callback_msg = f"支付失败 {self.RCR.url}"
		return self.payment_page(count + 1, max_count)
	
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