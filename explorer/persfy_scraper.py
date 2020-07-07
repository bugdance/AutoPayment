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


class PersFYScraper(RequestWorker):
	"""FY采集器，FY网站流程交互，行李价格前后不统一，无法区分人，最后支付步骤需要动态等待。"""
	
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
		self.baggage_kilogram: int = 0  # 行李添加总公斤数。
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
		# # # 启动爬虫，建立header，更新联系电话。
		self.RCR.set_to_session()
		self.RCR.set_to_proxy(enable_proxy, address)
		self.user_agent, self.init_header = self.RCR.build_to_header("none")
		self.CPR.contact_mobile = "16639167479"
		self.CPR.currency = "MYR"
		self.RCR.timeout = 30
		# # # 主体流程。
		if self.process_to_query(max_count=self.retry_count):
			if self.process_to_passenger(max_count=self.retry_count):
				if self.process_to_service(max_count=self.retry_count):
					if self.process_to_payment(max_count=self.retry_count):
						if self.process_to_record():
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
			# # # 生成header, 查询航班，必须这个页面进。
			self.RCR.url = "https://booking.fireflyz.com.my/Select.aspx"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "booking.fireflyz.com.my",
				"Upgrade-Insecure-Requests": "1",
			})
			if self.RCR.request_to_get():
				# # # 转换接口日期和7天后日期。
				flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
				now = self.DFR.format_to_now()
				future = self.DFR.format_to_now(custom_days=7)
				# # # 生成header, 点击查询航班数据。
				self.RCR.url = "https://booking.fireflyz.com.my/Select.aspx"
				self.RCR.header.update({
					"Content-Type": "application/x-www-form-urlencoded",
					"Host": "booking.fireflyz.com.my",
					"Origin": "https://booking.fireflyz.com.my",
					"Referer": "https://booking.fireflyz.com.my/Select.aspx",
					"Upgrade-Insecure-Requests": "1",
				})
				# # # 基础参数。
				param_batch = [
					("__EVENTTARGET", True, "#eventTarget"), ("__EVENTARGUMENT", True, "#eventArgument"),
					("__VIEWSTATE", True, "#viewState"), ("pageToken", True, "input[name=pageToken]"),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$RadioButtonMarketStructure",
					 False, "OneWay"),
					("ControlGroupSearchView_AvailabilitySearchInputSearchVieworiginStation1",
					 False, self.CPR.departure_code),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin1",
					 False, self.CPR.departure_code),
					("ControlGroupSearchView_AvailabilitySearchInputSearchViewdestinationStation1",
					 False, self.CPR.arrival_code),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination1",
					 False, self.CPR.arrival_code),
					("ControlGroupSearchView_AvailabilitySearchInputSearchVieworiginStation2",
					 False, ""),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketOrigin2",
					 False, ""),
					("ControlGroupSearchView_AvailabilitySearchInputSearchViewdestinationStation2",
					 False, ""),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxMarketDestination2",
					 False, ""),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay1",
					 False, flight_date.strftime("%d")),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth1",
					 False, flight_date.strftime("%Y-%m")),
					("date_picker", False, flight_date.strftime("%Y-%m-%d")),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketDay2",
					 False, now.strftime("%d")),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListMarketMonth2",
					 False, now.strftime("%Y-%m")),
					("date_picker", False, now.strftime("%Y-%m-%d")),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListCurrency",
					 False, self.CPR.currency),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_ADT",
					 False, self.CPR.adult_num + self.CPR.child_num),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListPassengerType_INFANT",
					 False, self.CPR.infant_num),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$TextBoxPromotionCode",
					 False, ""),
					("ControlGroupSearchView$AvailabilitySearchInputSearchView$DropDownListSearchBy",
					 False, "columnView"),
					("ControlGroupSearchView$ButtonSubmit", False, "Search"),
				]
				# # # 生成请求参数。
				self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.page_source)
				if self.RCR.request_to_post(is_redirect=True):
					# # # 查询错误信息。
					error, temp_list = self.DPR.parse_to_attributes(
						"value", "xpath", "//div[@id='errorSectionContent']//p/text()", self.RCR.page_source)
					if error:
						self.logger.info(f"提交查询失败(*>﹏<*)【{error}】")
						self.callback_msg = f"提交查询失败【{error}】。"
						return False
					# # # 解析接口航班号。
					interface_carrier = self.CPR.flight_num[:2]
					interface_no = self.CPR.flight_num[2:]
					interface_no = self.BFR.format_to_int(interface_no)
					# # # 匹配接口航班。
					is_flight = False
					key, key_list = self.DPR.parse_to_attributes(
						"value", "css",
						"input[id*=ControlGroupSelectView_AvailabilityInputSelectView_RadioButtonMkt1Fare]",
						self.RCR.page_source)
					for i in key_list:
						if "^" in i:
							continue
						else:
							flight_key = i.split("|")
							if len(flight_key) < 2:
								self.logger.info(
									f"解析航班号错误(*>﹏<*)【{self.CPR.flight_num}】")
								self.callback_msg = "解析航班号错误。"
								return False
							# # # 解析网页航班号。
							source_num, temp_list = self.BPR.parse_to_regex("(.*?)~ ", flight_key[1])
							source_num = self.BPR.parse_to_clear(source_num)
							source_carrier = source_num[:2]
							source_no = source_num[3:]
							source_no = self.BFR.format_to_int(source_no)
							# # # 匹配航班号。
							if interface_carrier == source_carrier and interface_no == source_no:
								is_flight = True
								key = i
								break
					if not is_flight:
						self.logger.info(f"匹配不到航班信息(*>﹏<*)【{self.CPR.flight_num}】")
						self.callback_msg = "该航线航班已售完。"
						return False
					# # # 继承header, 选完航班点击跳过查询。
					self.RCR.url = "https://booking.fireflyz.com.my/Select.aspx"
					# # # 基础参数。
					param_batch = [
						("__EVENTTARGET", True, "#eventTarget"), ("__EVENTARGUMENT", True, "#eventArgument"),
						("__VIEWSTATE", True, "#viewState"), ("pageToken", True, "input[name=pageToken]"),
						("AvailabilitySearchInputSelectView$DropDownListSearchBy", False, "columnView"),
						("AvailabilitySearchInputSelectView$RadioButtonMarketStructure", False, "OneWay"),
						("originStation1", False, self.CPR.departure_code),
						("AvailabilitySearchInputSelectView$TextBoxMarketOrigin1", False, self.CPR.departure_code),
						("destinationStation1", False, self.CPR.arrival_code),
						("AvailabilitySearchInputSelectView$TextBoxMarketDestination1", False, self.CPR.arrival_code),
						("originStation2", False, ""),
						("AvailabilitySearchInputSelectView$TextBoxMarketOrigin2", False, ""),
						("destinationStation2", False, ""),
						("AvailabilitySearchInputSelectView$TextBoxMarketDestination2", False, ""),
						("AvailabilitySearchInputSelectView$DropDownListMarketDay1",
						 False, flight_date.strftime("%d")),
						("AvailabilitySearchInputSelectView$DropDownListMarketMonth1",
						 False, flight_date.strftime("%Y-%m")),
						("date_picker", False, flight_date.strftime("%Y-%m-%d")),
						("AvailabilitySearchInputSelectView$DropDownListMarketDay2",
						 False, future.strftime("%d")),
						("AvailabilitySearchInputSelectView$DropDownListMarketMonth2",
						 False, future.strftime("%Y-%m")),
						("date_picker", False, future.strftime("%Y-%m-%d")),
						("AvailabilitySearchInputSelectView$DropDownListCurrency", False, self.CPR.currency),
						("AvailabilitySearchInputSelectView$DropDownListPassengerType_ADT",
						 False, self.CPR.adult_num + self.CPR.child_num),
						("AvailabilitySearchInputSelectView$DropDownListPassengerType_INFANT",
						 False, self.CPR.infant_num),
						("AvailabilitySearchInputSelectView$TextBoxPromotionCode", False, ""),
						("AvailabilitySearchInputSelectView$DropDownListFareTypes", False, ""),
						("ControlGroupSelectView$AvailabilityInputSelectView$market1", False, key),
						("ControlGroupSelectView$ButtonSubmit", False, "NEXT"),
					]
					# # # 生成请求参数。
					self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.page_source)
					if self.RCR.request_to_post(is_redirect=True):
						# # # 查询错误信息。
						error, temp_list = self.DPR.parse_to_attributes(
							"value", "xpath", "//div[@id='errorSectionContent']//p/text()", self.RCR.page_source)
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
			self.RCR.url = "https://booking.fireflyz.com.my/Passenger.aspx"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "booking.fireflyz.com.my",
				"Origin": "https://booking.fireflyz.com.my",
				"Referer": "https://booking.fireflyz.com.my/Passenger.aspx",
				"Upgrade-Insecure-Requests": "1",
			})
			# # # 基础参数。
			param_batch = [
				("__EVENTTARGET", True, "#eventTarget"), ("__EVENTARGUMENT", True, "#eventArgument"),
				("__VIEWSTATE", True, "#viewState"), ("pageToken", True, "input[name=pageToken]"),
				("MemberLoginViewPassengerView$TextBoxUserID", False, ""),
				("MemberLoginViewPassengerView$PasswordFieldPassword", False, ""),
				("CONTROLGROUPPASSENGER$ContactInputView$CONTROLGROUPPASSENGER"
				 "_ContactInputViewHtmlInputHiddenAntiForgeryTokenField", True,
				 "#CONTROLGROUPPASSENGER_ContactInputView_CONTROLGROUPPASSENGER"
				 "_ContactInputViewHtmlInputHiddenAntiForgeryTokenField"),
				("type", True, "Leisure"),
				("CONTROLGROUPPASSENGER$ContactInputView$DropDownListTitle", False, "MR"),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxFirstName", False, self.CPR.contact_first),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxLastName", False, self.CPR.contact_last),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxEmailAddress", False, self.CPR.contact_email),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxCompanyName", False, ""),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxAddressLine1", False, "No.1, 3rd Floor, CITTA Mall"),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxAddressLine2", False, "Jalan PJU 1A/48"),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxAddressLine3", False, "Ara Damansara"),
				("CONTROLGROUPPASSENGER$ContactInputView$DropDownListCountry", False, "CN"),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxCity", False, "Petaling Jaya"),
				("CONTROLGROUPPASSENGER$ContactInputView$DropDownListStateProvince", False, ""),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxPostalCode", False, "47301"),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxWorkPhone", False, f"86{self.CPR.contact_mobile}"),
				("CONTROLGROUPPASSENGER$ContactInputView$TextBoxOtherPhone", False, f"86{self.CPR.contact_mobile}"),
				("CONTROLGROUPPASSENGER$ItineraryDistributionInputView$Distribution", False, "2"),
				("CONTROLGROUPPASSENGER$ButtonSubmit", False, "Continue"),
			]
			# # # 追加每个成人具体的参数。
			for n, v in enumerate(self.CPR.adult_list):
				sex = "MR"
				if v.get("gender") == "F":
					sex = "MS"
				last_name = v.get("last_name")
				first_name = v.get("first_name")
				birthday = self.DFR.format_to_transform(v.get("birthday"), "%Y%m%d")
				nationality = v.get('nationality')
				adult_batch = [
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListTitle_{n}",
					 False, sex),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$TextBoxFirstName_{n}",
					 False, first_name),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$TextBoxLastName_{n}",
					 False, last_name),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListBirthDateDay_{n}",
					 False, birthday.day),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListBirthDateMonth_{n}",
					 False, birthday.month),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListBirthDateYear_{n}",
					 False, birthday.year),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListNationality_{n}",
					 False, nationality),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListProgram_{n}",
					 False, ""),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$TextBoxProgramNumber_{n}",
					 False, ""),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListOAFFCarriers0_{n}",
					 False, "FY"),
					(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$TextBoxtQAFFNumber0_{n}",
					 False, "")
				]
				# # # 追加每个成人具体的参数。
				param_batch.extend(adult_batch)
			# # # 追加每个儿童具体的参数。
			if self.CPR.child_num:
				for n, v in enumerate(self.CPR.child_list):
					n += self.CPR.adult_num
					last_name = v.get("last_name")
					first_name = v.get("first_name")
					birthday = self.DFR.format_to_transform(v.get("birthday"), "%Y%m%d")
					nationality = v.get('nationality')
					child_batch = [
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListTitle_{n}",
						 False, "CHD"),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$TextBoxFirstName_{n}",
						 False, first_name),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$TextBoxLastName_{n}",
						 False, last_name),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListBirthDateDay_{n}",
						 False, birthday.day),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListBirthDateMonth_{n}",
						 False, birthday.month),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListBirthDateYear_{n}",
						 False, birthday.year),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListNationality_{n}",
						 False, nationality),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListProgram_{n}",
						 False, ""),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$TextBoxProgramNumber_{n}",
						 False, ""),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$DropDownListOAFFCarriers0_{n}",
						 False, "FY"),
						(f"CONTROLGROUPPASSENGER$PassengerInputViewPassengerView$TextBoxtQAFFNumber0_{n}",
						 False, "")
					]
					# # # 追加每个儿童具体的参数。
					param_batch.extend(child_batch)
			# # # 生成请求参数。
			self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
			if self.RCR.request_to_post(is_redirect=True):
				# # # 查询错误信息。
				error, temp_list = self.DPR.parse_to_attributes(
					"value", "xpath", "//div[@id='errorSectionContent']//p/text()", self.RCR.page_source)
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
			# # # 生成header, 添加附加页面。
			self.RCR.url = "https://booking.fireflyz.com.my/AddOns.aspx"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "booking.fireflyz.com.my",
				"Origin": "https://booking.fireflyz.com.my",
				"Referer": "https://booking.fireflyz.com.my/AddOns.aspx",
				"Upgrade-Insecure-Requests": "1",
			})
			# # # 基础参数。
			param_batch = [
				("__EVENTTARGET", False, "CONTROLGROUPADDONS$LinkButtonSubmit"),
				("__EVENTARGUMENT", True, "#eventArgument"),
				("__VIEWSTATE", True, "#viewState"), ("pageToken", True, "input[name=pageToken]"),
				("CONTROLGROUPADDONS$FireflyInsuranceInputViewAddOnsView$RadioButtonInsurance",
				 False, "RadioButtonInsuranceNo")
			]
			flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
			flight_date = flight_date.strftime("%Y%m%d")
			# # # 追加每个成人具体的参数。
			for n, v in enumerate(self.CPR.adult_list):
				# # # 判断行李并累计公斤数。
				weight = v.get('baggage')
				kilogram = 0
				if weight:
					for w in weight:
						kilogram += self.BFR.format_to_int(w.get('weight'))
				# # # 解析行李参数。
				kilogram_value = ""
				if kilogram:
					self.baggage_kilogram += kilogram
					option, value_list = self.DPR.parse_to_attributes(
						"value", "css",
						f"#CONTROLGROUPADDONS_AddBaggageInputViewAddOnsView_DropDownListBaggage0_0_{n} option",
						self.RCR.copy_source)
					option, text_list = self.DPR.parse_to_attributes(
						"text", "css",
						f"#CONTROLGROUPADDONS_AddBaggageInputViewAddOnsView_DropDownListBaggage0_0_{n} option",
						self.RCR.copy_source)
					if not value_list or not text_list:
						self.logger.info(f"匹配行李价格失败(*>﹏<*)【{n}】【{v}】")
						self.callback_msg = "匹配行李失败"
						return False
					kilogram_text = f"{kilogram}kg"
					for i, j in enumerate(text_list):
						if kilogram_text in j:
							kilogram_value = value_list[i]
							break
				adult_batch = [
					(f"CONTROLGROUPADDONS$AddBaggageInputViewAddOnsView$DropDownListBaggage0_0_{n}",
					 False, kilogram_value),
					(f"CONTROLGROUPADDONS$AddSportsEquipmentInputViewAddOnsView$DropDownListSportsEquipment0_0_{n}",
					 False, ""),
					(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK010_0_{n}", False, "0"),
					(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK020_0_{n}", False, "0"),
					(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK030_0_{n}", False, "0"),
					(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK040_0_{n}", False, "0"),
					(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK050_0_{n}", False, "0"),
					(f"CONTROLGROUPADDONS$AddSkyLoungeInputViewAddOnsView$DropDownListSkyLounge"
					 f"{self.CPR.departure_code}_{self.CPR.arrival_code}_{flight_date}_{n}",
					 False, ""),
				]
				seat, temp_list = self.DPR.parse_to_attributes(
					"name", "css", f".passenger_1_1_{n+1}", self.RCR.copy_source)
				if seat:
					adult_batch.append((seat, False, ""))
				# # # 追加每个成人具体的参数。
				param_batch.extend(adult_batch)
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
					# # # 解析行李参数。
					kilogram_value = ""
					if kilogram:
						self.baggage_kilogram += kilogram
						option, value_list = self.DPR.parse_to_attributes(
							"value", "css",
							f"#CONTROLGROUPADDONS_AddBaggageInputViewAddOnsView_DropDownListBaggage0_0_{n} option",
							self.RCR.copy_source)
						option, text_list = self.DPR.parse_to_attributes(
							"text", "css",
							f"#CONTROLGROUPADDONS_AddBaggageInputViewAddOnsView_DropDownListBaggage0_0_{n} option",
							self.RCR.copy_source)
						if not value_list or not text_list:
							self.logger.info(f"匹配行李价格失败(*>﹏<*)【{n}】【{v}】")
							self.callback_msg = "匹配行李失败"
							return False
						kilogram_text = f"{kilogram}kg"
						for i, j in enumerate(text_list):
							if kilogram_text in j:
								kilogram_value = value_list[i]
								break
					child_batch = [
						(f"CONTROLGROUPADDONS$AddBaggageInputViewAddOnsView$DropDownListBaggage0_0_{n}",
						 False, kilogram_value),
						(f"CONTROLGROUPADDONS$AddSportsEquipmentInputViewAddOnsView$DropDownListSportsEquipment0_0_{n}",
						 False, ""),
						(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK010_0_{n}", False, "0"),
						(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK020_0_{n}", False, "0"),
						(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK030_0_{n}", False, "0"),
						(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK040_0_{n}", False, "0"),
						(f"CONTROLGROUPADDONS$AddMealInputViewAddOnsView$DropDownListMK050_0_{n}", False, "0"),
						(f"CONTROLGROUPADDONS$AddSkyLoungeInputViewAddOnsView$DropDownListSkyLounge"
						 f"{self.CPR.departure_code}_{self.CPR.arrival_code}_{flight_date}_{n}",
						 False, ""),
					]
					seat, temp_list = self.DPR.parse_to_attributes(
						"name", "css", f".passenger_1_1_{n + 1}", self.RCR.copy_source)
					if seat:
						child_batch.append((seat, False, ""))
					# # # 追加每个儿童具体的参数。
					param_batch.extend(child_batch)
			# # # 生成请求参数。
			self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
			if self.RCR.request_to_post(is_redirect=True):
				# # # 查询错误信息。
				error, temp_list = self.DPR.parse_to_attributes(
					"value", "xpath", "//div[@id='errorSectionContent']//p/text()", self.RCR.page_source)
				if error:
					self.logger.info(f"添加服务失败(*>﹏<*)【{error}】")
					self.callback_msg = f"添加服务失败【{error}】。"
					return False
				# # # 获取最终总价格。
				total, total_list = self.DPR.parse_to_attributes(
					"text", "css", ".booking-summary-body div:nth-child(3) table td", self.RCR.page_source)
				if len(total_list) != 2:
					self.logger.info(f"支付页面获取价格失败(*>﹏<*)【service】")
					self.callback_msg = "支付页面获取价格失败"
					return False
				if "Total Amount" not in total_list[0]:
					self.logger.info(f"支付页面获取价格失败(*>﹏<*)【service】")
					self.callback_msg = "支付页面获取价格失败"
					return False
				self.total_price, temp_list = self.BPR.parse_to_regex("(.*)MYR", total_list[1])
				self.total_price = self.BFR.format_to_float(2, self.total_price)
				# # # 解析行李价格，按人头和件数分价格。
				baggage, baggage_list = self.DPR.parse_to_attributes(
					"text", "css",
					".booking-summary-body div:nth-child(2) table:nth-child(5) td:nth-child(2) div",
					self.RCR.page_source)
				if baggage_list:
					for i in baggage_list:
						single_baggage, temp_list = self.BPR.parse_to_regex("(.*)MYR", i)
						single_baggage = self.BFR.format_to_float(2, single_baggage)
						self.baggage_price += single_baggage
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
		               f"foreignCurrency={self.CPR.currency}&carrier=FY"
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
			card_name = f"{self.CPR.card_last}{self.CPR.card_first}"
			card_year = f"20{self.CPR.card_date[:2]}"
			card_month = self.CPR.card_date[2:]
			card_code = self.AFR.decrypt_into_aes(
				self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.card_code)
			if not card_code:
				self.logger.info(f"解密支付卡失败(*>﹏<*)【{self.CPR.card_code}】")
				self.callback_msg = "解密支付卡失败，请通知技术检查程序。"
				return False
			# # # 生成header，开始预支付。
			self.RCR.url = "https://booking.fireflyz.com.my/Payment.aspx"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Content-Type": "application/x-www-form-urlencoded",
				"Host": "booking.fireflyz.com.my",
				"Origin": "https://booking.fireflyz.com.my",
				"Referer": "https://booking.fireflyz.com.my/Payment.aspx",
				"Upgrade-Insecure-Requests": "1",
			})
			total_price = self.BFR.format_to_cut(4, self.total_price)
			# # # 基础参数。
			param_batch = [
				("__EVENTTARGET", True, "#eventTarget"), ("__EVENTARGUMENT", True, "#eventArgument"),
				("__VIEWSTATE", True, "#viewState"), ("pageToken", True, "input[name=pageToken]"),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$DropDownListCurrency",
				 False, self.CPR.currency),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$TextBoxACCTNO", False, self.CPR.card_num),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$DropDownListEXPDAT_Month",
				 False, card_month),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$DropDownListEXPDAT_Year",
				 False, card_year),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$TextBoxCC::VerificationCode",
				 False, card_code),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$TextBoxCC::AccountHolderName",
				 False, card_name),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$TextBoxAMT", False, total_price),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$TextBoxVoucherNumber", False, ""),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$DropDownListVoucherExpirationDateDay",
				 False, ""),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$DropDownListVoucherExpirationDateMonth",
				 False, ""),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$DropDownListVoucherExpirationDateYear",
				 False, ""),
				("CONTROLGROUPPAYMENTBOTTOM$PaymentInputViewPaymentView$DropDownListPaymentMethodCode",
				 False, "ExternalAccount:MC"),
				("CONTROLGROUPPAYMENTBOTTOM$ButtonSubmit", False, "Next")
			]
			# # # 生成请求参数。
			self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
			if self.RCR.request_to_post():
				# # # 匹配下一次请求地址和参数。
				request_url, temp_list = self.DPR.parse_to_attributes(
					"action", "css", "form#redirectionPostForm", self.RCR.page_source)
				referer_url = "https://booking.fireflyz.com.my/Payment.aspx"
				option_post = []
				option, option_list = self.DPR.parse_to_attributes(
					"name", "css", "form#redirectionPostForm input[type=hidden]", self.RCR.page_source)
				for i in option_list:
					option, temp_list = self.DPR.parse_to_attributes(
						"value", "css", f"form#redirectionPostForm input[name={i}]", self.RCR.page_source)
					option_post.append((f"{i}", option))
				# # # 生成header，开始支付。
				# # # https://cap.attempts.securecode.com/acspage/cap?RID=136&VAA=B
				self.RCR.url = request_url
				self.RCR.param_data = None
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Content-Type": "application/x-www-form-urlencoded",
					"Host": "cap.attempts.securecode.com",
					"Origin": "https://booking.fireflyz.com.my",
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
					# # # https://booking.fireflyz.com.my/Payment.aspx
					self.RCR.url = request_url
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Content-Type": "application/x-www-form-urlencoded",
						"Host": "booking.fireflyz.com.my",
						"Origin": "https://cap.attempts.securecode.com",
						"Referer": referer_url,
						"Upgrade-Insecure-Requests": "1"
					})
					# # # 基础参数。
					self.RCR.post_data = option_post
					if self.RCR.request_to_post(is_redirect=True):
						return True
			# # # 错误重试。
			self.logger.info(f"请求支付第{count + 1}次超时(*>﹏<*)【payment】")
			self.callback_msg = f"请求支付第{count + 1}次超时，请重试。"
			self.callback_data["orderIdentification"] = 2
			return self.process_to_payment(count + 1, max_count)
	
	def process_to_record(self, count: int = 0, max_count: int = 10) -> bool:
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
			# # # 生成header，开始获取订单号。
			# # # https://booking.fireflyz.com.my/Wait.aspx
			self.RCR.url = "https://booking.fireflyz.com.my/Wait.aspx"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "booking.fireflyz.com.my",
				"Referer": "https://booking.fireflyz.com.my/Wait.aspx",
				"Upgrade-Insecure-Requests": "1"
			})
			self.RCR.post_data = None
			if self.RCR.request_to_get():
				payment_url, temp_list = self.DPR.parse_to_attributes("href", "css", "h2 a", self.RCR.page_source)
				payment_url = self.BPR.parse_to_clear(payment_url)
				if not payment_url:
					# # # 等待重试。
					self.logger.info(f"获取支付编码第{count + 1}次排队中(*>﹏<*)【record】")
					self.callback_msg = f"获取支付编码第{count + 1}次排队中。"
					self.callback_data["orderIdentification"] = 2
					time.sleep(10)
					return self.process_to_record(count + 1, max_count)
				if "/Payment.aspx" == payment_url:
					# # # 生成header，开始获取订单号。
					# # # https://booking.fireflyz.com.my/Wait.aspx
					self.RCR.url = "https://booking.fireflyz.com.my/Payment.aspx"
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Host": "booking.fireflyz.com.my",
						"Referer": "https://booking.fireflyz.com.my/Wait.aspx",
						"Upgrade-Insecure-Requests": "1"
					})
					self.RCR.post_data = None
					if self.RCR.request_to_get():
						# # # 查询错误信息。
						error, temp_list = self.DPR.parse_to_attributes(
							"value", "xpath", "//div[@id='errorSectionContent']//p/text()", self.RCR.page_source)
						if error:
							self.logger.info(f"获取支付编码失败(*>﹏<*)【{error}】")
							self.callback_msg = f"获取支付编码失败【{error}】。"
							self.callback_data["orderIdentification"] = 2
							return False
				if "/PaymentSuccess.aspx" == payment_url:
					# # # 生成header，开始获取订单号。
					# # # https://booking.fireflyz.com.my/PaymentSuccess.aspx
					self.RCR.url = "https://booking.fireflyz.com.my/PaymentSuccess.aspx"
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Host": "booking.fireflyz.com.my",
						"Referer": "https://booking.fireflyz.com.my/Wait.aspx",
						"Upgrade-Insecure-Requests": "1"
					})
					self.RCR.post_data = None
					if self.RCR.request_to_get(status_code=302):
						# # # 生成header，开始获取订单号。
						# # # https://booking.fireflyz.com.my/Itinerary.aspx
						self.RCR.url = "https://booking.fireflyz.com.my/Itinerary.aspx"
						self.RCR.param_data = None
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							"Host": "booking.fireflyz.com.my",
							"Referer": "https://booking.fireflyz.com.my/Wait.aspx",
							"Upgrade-Insecure-Requests": "1"
						})
						self.RCR.post_data = None
						if self.RCR.request_to_get():
							# # # 获取PNR。
							self.record, temp_list = self.DPR.parse_to_attributes(
								"value", "xpath",
								"//div[contains(., 'Confirmation Number')]//span/text()", self.RCR.page_source)
							self.record = self.BPR.parse_to_clear(self.record)
							if not self.record:
								self.logger.info("获取支付编码失败(*>﹏<*)【record】")
								self.callback_msg = "获取PNR失败，可能已出票，请核对。"
								self.callback_data["orderIdentification"] = 2
								return False
							confirmed = 0
							last_four = self.CPR.card_num[-4:]
							card, card_list = self.DPR.parse_to_attributes(
								"text", "css",
								"div[class*=payment-details-content] table td:nth-child(1)", self.RCR.page_source)
							approved, approved_list = self.DPR.parse_to_attributes(
								"text", "css",
								"div[class*=payment-details-content] table span", self.RCR.page_source)
							for n, v in enumerate(card_list):
								if last_four in v:
									status = approved_list[n]
									if "Approved" in status:
										confirmed = 1
										break
									else:
										self.logger.info(f"获取批准状态失败(*>﹏<*)【{status}】")
										self.callback_msg = f"获取批准状态失败，PNR是【{self.record}】，状态为【{status}】。"
										self.callback_data["orderIdentification"] = 2
										return False
							if not confirmed:
								self.logger.info(f"获取批准状态失败(*>﹏<*)【{self.record}】")
								self.callback_msg = f"获取批准状态失败，PNR是【{self.record}】，请核对批准状态。"
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

