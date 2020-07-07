#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""Created on 2020-01-14 13:39:57
written by pyEd.
"""
import base64
import json
import time
from accessor.request_worker import RequestWorker
from accessor.request_crawler import RequestCrawler
from booster.aes_formatter import AESFormatter
from booster.basic_formatter import BasicFormatter
from booster.basic_parser import BasicParser
from booster.callback_formatter import CallBackFormatter
from booster.callin_parser import CallInParser
from booster.date_formatter import DateFormatter
from booster.dom_parser import DomParser


class PersBXScraper(RequestWorker):
	"""BX采集器，BX网站流程交互。"""
	
	def __init__(self) -> None:
		RequestWorker.__init__(self)
		self.RCR = RequestCrawler()  # 请求爬行器
		self.AFR = AESFormatter()  # AES格式器。
		self.BFR = BasicFormatter()  # 基础格式器
		self.BPR = BasicParser()  # 基础解析器
		self.CFR = CallBackFormatter()  # 回调格式器
		self.CPR = CallInParser(False)  # 接入解析器
		self.DFR = DateFormatter()  # 日期格式器
		self.DPR = DomParser()  # 文档解析器
		# # # 返回中用到的变量
		self.total_price: float = 0.0  # 总价
		self.return_price: float = 0.0  # 返回价格
		self.baggage_price: float = 0.0  # 行李总价
		self.kilogram:float = 0  # 行李总重量
		self.record: str = ""  # 票号
	
	def init_to_assignment(self) -> bool:
		"""Assignment to logger. 赋值logger。

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
		self.callback_data = self.CFR.format_to_async()
		# # # 解析接口参数。
		if not self.CPR.parse_to_interface(source_dict):
			self.callback_data['msg'] = "请通知技术检查接口数据参数。"
			return self.callback_data
		self.logger.info(source_dict)
		# # # # 启动爬虫，建立header。
		self.RCR.set_to_session()
		self.RCR.set_to_proxy(enable_proxy, address)
		self.user_agent, self.init_header = self.RCR.build_to_header("none")
		self.RCR.timeout = 30
		
		###### 测试
		# # # # #  返回行李
		# for passenger in self.CPR.adult_list:
		#     for i in passenger.get('baggage'):
		#         self.logger.info(i)
		#     if passenger['gender'] == 'M':
		#         title = 'MR'
		#     else:
		#         title = 'MS'
		#     passenger_dict = {'passengerType': 'AD', 'usrNo': '', 'lastName': passenger['last_name'],
		#                       'firstName': passenger['first_name'], 'title': title, 'phone': ''}
		#     self.passenger_list.append(passenger_dict)
		#
		# for passenger in self.CPR.child_list:
		#     if passenger['gemder'] == 'M':
		#         title = 'MSTR'
		#     else:
		#         title = 'MISS'
		#     passenger_dict = {'passengerType': 'AD', 'usrNo': '', 'lastName': passenger['last_name'],
		#                       'firstName': passenger['first_name'], 'title': title, 'phone': '',
		#                       'birthYYYYMMDD': passenger['birthday']}
		#     self.passenger_list.append(passenger_dict)
		
		# # # 更新联系方式
		self.CPR.contact_email = "168033518@qq.com"
		self.CPR.contact_mobile = "16639168284"
		
		if self.process_to_index():
			if self.process_to_query():
				if self.process_to_login():
					if self.process_to_segment():
						if self.process_to_captcha():
							if self.process_to_passenger():
								if self.process_to_service():
									#     if self.process_to_record():
									if self.process_to_payment():
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
	
	def process_to_index(self, count: int = 0, max_count: int = 2) -> bool:
		"""获取首页"""
		if count >= max_count:
			return False
		
		self.RCR.url = 'https://cn.airbusan.com/content/individual/'
		self.RCR.post_data = None
		self.RCR.param_data = (
			('', ''),
			('city', ''),
		)
		self.RCR.header = self.BFR.format_to_same(self.init_header)
		if self.RCR.request_to_get():
			return True
		
		self.logger.info("首页超时或者错误 (*>﹏<*)【process_to_index】")
		self.callback_msg = "首页超时或者错误"
		return self.process_to_index(count + 1, max_count)
	
	def process_to_query(self, count: int = 0, max_count: int = 1) -> bool:
		"""查询"""
		if count >= max_count:
			return False
		
		self.RCR.url = 'https://cn.airbusan.com/web/bookingApi/flightsAvail'
		self.RCR.param_data = None
		self.RCR.header.update(
			{
				'Host': 'cn.airbusan.com',
				'Referer': 'https://cn.airbusan.com/web/individual/booking/flightsAvail',
				'Origin': 'https://cn.airbusan.com',
			}
		)
		if len(self.CPR.flight_num) == 5:
			self.CPR.flight_num = self.CPR.flight_num[0:2] + '0' + self.CPR.flight_num[2:]
		
		self.RCR.post_data = {
			'bookingCategory': 'Individual',
			'focYn': 'N',
			'tripType': 'OW',
			'depCity1': self.CPR.departure_code,
			'arrCity1': self.CPR.arrival_code,
			'depDate1': self.CPR.flight_date[0:4] + '-' + self.CPR.flight_date[4:6] + '-' + self.CPR.flight_date[6:],
			'paxCountCorp': '0',
			'paxCountAd': self.CPR.adult_num,
			'paxCountCh': self.CPR.child_num,
			'paxCountIn': self.CPR.infant_num
		}
		
		if self.RCR.request_to_post(page_type='json'):
			
			self.paxCountCorp, temp_list = self.BPR.parse_to_path('$..param.paxCountCorp', self.RCR.page_source)
			self.paxCountAd, temp_list = self.BPR.parse_to_path('$..param.paxCountAd', self.RCR.page_source)
			self.paxCountCh, temp_list = self.BPR.parse_to_path('$..param.paxCountCh', self.RCR.page_source)
			self.paxCountIn, temp_list = self.BPR.parse_to_path('$..param.paxCountIn', self.RCR.page_source)
			self.focYn, temp_list = self.BPR.parse_to_path('$..param.focYn', self.RCR.page_source)
			self.taxAd, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.taxAd', self.RCR.page_source)
			self.taxCh, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.taxCh', self.RCR.page_source)
			self.taxIn, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.taxIn', self.RCR.page_source)
			self.fuelAd, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.fuelAd', self.RCR.page_source)
			self.fuelCh, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.fuelCh', self.RCR.page_source)
			self.fuelIn, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.fuelIn', self.RCR.page_source)
			self.taxName, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.taxMapAd[*].taxName', self.RCR.page_source)
			self.tax, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.taxMapAd[*].tax', self.RCR.page_source)
			self.taxDescKo, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.taxMapAd[*].taxDescKo',
			                                                   self.RCR.page_source)
			self.taxDescEn, temp_list = self.BPR.parse_to_path('$..pubTaxFuel.taxMapAd[*].taxDescEn',
			                                                   self.RCR.page_source)
			
			# 判断航班
			flights, flight_list = self.BPR.parse_to_path('$...listFlight', self.RCR.page_source)
			if len(flights) < 1:
				self.logger.info(f"航线 {self.CPR.departure_code} - {self.CPR.arrival_code} 没有航班")
				return False
			
			for i in flights:
				# 判断长度是否包含 票价种类（A） 'cls': 'S',  逻辑没写
				# self.logger.info(i.get('listCls'))
				# self.logger.info(len(i.get('listCls')))
				for n, f in enumerate(i.get('listCls')):
					if i['flightNo'] == self.CPR.flight_num:
						# 获取航班 所有票价类型
						listClsPrice = []
						for m in i.get('listCls'):
							price = m['viewPriceAd']
							listClsPrice.append(price)
						
						# 判断最便宜的机票价格
						if f['viewPriceAd'] == min(listClsPrice):
							self.cls = f['cls']
							self.subCls = f['subCls']
							self.CPR.currency = f['currency']
							self.priceCorp = f['priceCorp']
							self.priceAd = f['priceAd']
							self.priceCh = f['priceCh']
							self.priceIn = f['priceIn']
							self.stampNeedCount = f['stampNeedCount']
							self.stampRefundChargeCount = f['stampRefundChargeCount']
							self.mplusnM = f['mplusnM']
							self.mplusnN = f['mplusnN']
							self.logger.info(f"获取价格成功 {min(listClsPrice)}")
							self.depDate = i['depDate']
							self.depTime = i['depTime']
							self.arrDate = i['arrDate']
							self.arrTime = i['arrTime']
							return True
			
			else:
				self.logger.info(f"当前日期（{self.CPR.flight_date}）没有 ({self.CPR.flight_num})该航班")
				self.callback_msg = f"当前日期（{self.CPR.flight_date}）没有 ({self.CPR.flight_num})该航班"
				return False
		
		self.logger.info("查询航班信息失败 (*>﹏<*)【process_to_query】")
		self.callback_msg = "查询航班信息失败"
		return self.process_to_query(count + 1, max_count)
	
	def process_to_login(self, count: int = 0, max_count: int = 1) -> bool:
		"""登录"""
		self.RCR.url = 'https://cn.airbusan.com/web/common/loginApi/memberLoginProc'
		self.RCR.param_data = None
		self.RCR.header.update(
			{
				'Referer': 'https://cn.airbusan.com/web/individual/booking/internationalOnewayPassenger',
				'Origin': 'https://cn.airbusan.com',
			}
		)
		password = self.AFR.decrypt_into_aes(
			self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.password)
		# self.logger.info(f"密码： {password}")
		self.RCR.post_data = {
			'loginType': '1',
			'userId': self.CPR.username,
			'password': password
		}
		if self.RCR.request_to_post(page_type="json"):
			status, temp_list = self.BPR.parse_to_path('$.errorDesc', self.RCR.page_source)
			if status:
				self.logger.info(f'登录失败 | {status.replace("<br/>", "")}')
				self.callback_msg = f'登录失败 | {status.replace("<br/>", "")}'
				return False
			return True
		
		self.logger.info("登录失败 (*>﹏<*)【process_to_login】")
		self.callback_msg = "登录失败"
		return self.process_to_login(count + 1, max_count)
	
	def process_to_segment(self, count: int = 0, max_count: int = 2) -> bool:
		"""提交航段信息"""
		if count >= max_count:
			return False
		
		self.RCR.url = 'https://cn.airbusan.com/web/individual/booking/internationalOnewayPassenger'
		self.RCR.header.update(
			{
				'Referer': 'https://cn.airbusan.com/web/individual/booking/flightsAvail',
			}
		)
		self.RCR.post_data = {
			'jsonString': '{"listItinerary":[{"depCity":"%s","arrCity":"%s","flightNoWWDDDD":"%s","cls":"%s","subCls":"%s","foc":"N","mplusnM":%s,"mplusnN":%s,"depDate":"%s","depTime":"%s","arrTime":"%s","delayDepDate":"","delayDepTime":"","delayArrDate":"","delayArrTime":"","priceCorp":0,"priceAd":%s,"priceCh":%s,"priceIn":%s,"stampNeedCount":%s,"stampRefundChargeCount":%s,"currency":"%s"}],"focYN":"%s","paxCountAd":%s,"paxCountCh":%s,"paxCountCorp":%s,"paxCountIn":%s,"tripType":"OW","taxAd":%s,"taxCh":%s,"taxIn":%s,"fuelAd":%s,"fuelCh":%s,"fuelIn":0,"currency":"%s","taxMapAd":[{"taxName":"%s","tax":"%s","taxDescKo":"%s","taxDescEn":"%s"}],"taxMapCh":[],"taxMapIn":[]}' % (
			self.CPR.departure_code, self.CPR.arrival_code, self.CPR.flight_num, self.cls, self.subCls, self.mplusnN,
			self.mplusnM, self.CPR.flight_date, self.depTime, self.arrTime, int(self.priceAd), int(self.priceCh),
			int(self.priceIn), int(self.stampNeedCount), int(self.stampRefundChargeCount), self.CPR.currency,
			self.focYn, int(self.paxCountAd), int(self.paxCountCh), int(self.paxCountCorp), int(self.paxCountIn),
			int(self.taxAd), int(self.taxCh), int(self.taxIn), int(self.fuelAd), int(self.fuelIn), self.CPR.currency,
			self.taxName, int(self.tax), self.taxDescKo, self.taxDescEn)
		}
		
		if self.RCR.request_to_post():
			self.logger.info("提交航段信息成功")
			self.hash, temp_list = self.BPR.parse_to_regex('paramReserve.hash = "(.*?)"', self.RCR.page_source)
			
			self.total, temp_list = self.BPR.parse_to_regex('paramReserve.requestTotalTotal = (.*?);',
			                                                self.RCR.page_source)
			self.logger.info(self.total)
			return True
		
		self.logger.info("提交航段信息失败 (*>﹏<*)【process_to_segment】")
		self.callback_msg = "提交航段信息失败"
		return self.process_to_segment(count + 1, max_count)
	
	def process_to_captcha(self, count: int = 0, max_count: int = 2) -> bool:
		"""处理验证码"""
		if count >= max_count:
			return False
		
		self.RCR.url = 'https://cn.airbusan.com/web/commonApi/captchaEx'
		if self.RCR.request_to_get():
			self.captcha_link = self.BPR.parse_to_dict(self.RCR.page_source)['imageUri']
			self.captcha_key = \
			self.BPR.parse_to_regex('https://cn.airbusan.com/web/commonApi/captchaImage/(.*)', self.captcha_link)[0]
		self.RCR.url = self.captcha_link
		if self.RCR.request_to_get(page_type='content'):
			data = base64.b64encode(self.RCR.page_source).decode()
			self.RCR.url = "http://47.97.27.36:30002/bxweb/code"
			self.RCR.post_data = "{'postdata': '%s'}" % data
		if self.RCR.request_to_post():
			self.captcha_code = self.RCR.page_source
			self.logger.info(self.captcha_code)
			return True
		
		self.logger.info("验证码接口识别失败 (*>﹏<*)【process_to_captcha】")
		self.callback_msg = "验证码接口识别失败"
		return self.process_to_captcha(count + 1, max_count)
	
	def process_to_passenger(self, count: int = 0, max_count: int = 2) -> bool:
		"""提交乘客信息"""
		if count >= max_count:
			return False
		
		self.passenger_list = []
		for passenger in self.CPR.adult_list:
			if passenger['gender'] == 'M':
				title = 'MR'
			else:
				title = 'MS'
			passenger_dict = {'passengerType': 'AD', 'usrNo': '', 'lastName': passenger['last_name'],
			                  'firstName': passenger['first_name'], 'title': title, 'phone': ''}
			self.passenger_list.append(passenger_dict)
		
		for passenger in self.CPR.child_list:
			if passenger['gemder'] == 'M':
				title = 'MSTR'
			else:
				title = 'MISS'
			passenger_dict = {'passengerType': 'AD', 'usrNo': '', 'lastName': passenger['last_name'],
			                  'firstName': passenger['first_name'], 'title': title, 'phone': '',
			                  'birthYYYYMMDD': passenger['birthday']}
			self.passenger_list.append(passenger_dict)
		
		self.RCR.url = 'https://cn.airbusan.com/web/bookingApi/internationalOnewayReserve'
		self.RCR.post_data = {
			'jsonString': str(
				'{"listItinerary":[{"depDate":"%s","depCity":"%s","arrCity":"%s","flightNoWWDDDD":"%s","cls":"%s","subCls":"%s"}],"listPassenger":%s,"tripType":"OW","focYN":"N","phoneNo":"8613810254174","bookingCategory":"Individual","requestTotalTotal":%s,"excludeMember":"Y","hash":"%s","emailId":"hthy666","emailDomain":"vip.163.com"}' % (
				self.depDate, self.CPR.departure_code, self.CPR.arrival_code, self.CPR.flight_num, self.cls,
				self.subCls, json.dumps(self.passenger_list), self.total, self.hash)).replace(' ', ''),
			'captchaExKey': self.captcha_key,
			'captchaExValue': self.captcha_code
		}
		self.logger.info(self.RCR.post_data)
		if self.RCR.request_to_post(page_type='json'):
			status, temp_list = self.BPR.parse_to_path('$.errorDesc', self.RCR.page_source)
			if status:
				self.logger.info(f'提交乘客信息失败 | {status}')
				self.callback_msg = "提交乘客信息失败"
				return False
			
			self.encryptPnr, temp_list = self.BPR.parse_to_path('$.encryptPnr', self.RCR.page_source)
			# self.logger.info('提交乘客信息成功')
			return True
		
		self.logger.info("提交乘客信息失败 (*>﹏<*)【process_to_passenger】")
		self.callback_msg = "提交乘客信息失败"
		self.process_to_captcha()
		return self.process_to_passenger(count + 1, max_count)
	
	def process_to_service(self, count: int = 0, max_count: int = 2) -> bool:
		"""提交辅营信息"""
		if count >= max_count:
			return False
		
		self.RCR.url = 'https://cn.airbusan.com/web/individual/booking/emdCart'
		self.RCR.post_data = {
			'encryptPnr': self.encryptPnr
		}
		if self.RCR.request_to_post():
			self.encryptPnr, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="encryptPnr"]',
			                                                          self.RCR.page_source)
			self.logger.info(self.encryptPnr)
			self.RCR.url = 'https://cn.airbusan.com/web/bookingApi/emdCartAdd'
			self.RCR.header.update(
				{
					'Referer': 'https://cn.airbusan.com/web/individual/booking/emdCart',
				}
			)
			baggage_list = []
			for n, v in enumerate(self.CPR.adult_list):
				# # # 判断行李并累计公斤数。
				weight = v.get('baggage')
				kilogram = 0
				if weight:
					for w in weight:
						kilogram += self.BFR.format_to_int(w.get('weight'))
				self.kilogram = kilogram  # 行李总量
				if kilogram % 15 == 0 and kilogram != 0:
					baggage = {"itinNoBaseOne": 1, "paxNoBaseOne": n + 1, "bundleCode": "", "prdCode": "EA",
					           "optCode": "01", "optRemark": "", "qty": int(kilogram / 15)}
					baggage_list.append(baggage)
			self.RCR.post_data = {
				'bookingCategory': 'Individual',
				'encryptPnr': self.encryptPnr,
				'cooperateType': '',
				'jsonArrayEmdWebOrder': json.dumps(baggage_list)
			}
			# self.logger.info(self.RCR.post_data)
			if self.RCR.request_to_post():
				self.encryptPnr = self.BPR.parse_to_dict(self.RCR.page_source).get('encryptPnr')
				self.logger.info("提交辅营页面成功")
				return True
		
		self.logger.info("提交辅营失败 (*>﹏<*)【process_to_service】")
		self.callback_msg = "提交辅营失败"
		return self.process_to_service(count + 1, max_count)
	
	def process_to_payment(self, count: int = 0, max_count: int = 2) -> bool:
		"""获取支付页面"""
		if count >= max_count:
			return False
		
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
		
		self.RCR.url = 'https://cn.airbusan.com/web/individual/booking/internationalPurchase'
		self.RCR.post_data = {
			'encryptPnr': self.encryptPnr,
			'cooperateType': '',
			'currencyLocale': 'undefined'
		}
		if self.RCR.request_to_post():
			
			encrypt, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="encrypt"]',
			                                                  self.RCR.page_source)
			purchaseFor, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="purchaseFor"]',
			                                                      self.RCR.page_source)
			if not purchaseFor:
				self.logger.info("支付失败, 支付参数获取失败 purchaseFor")
				self.callback_msg = "支付失败"
				return False
			
			if not encrypt:
				self.logger.info("支付失败, 支付参数获取失败 encrypt")
				self.callback_msg = "支付失败"
				return False
			
			self.RCR.url = 'https://cn.airbusan.com/web/PurchaseApi/needToPurchase'
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.param_data = None
			self.RCR.post_data = {
				'purchaseFor': purchaseFor,
				'encrypt': encrypt
			}
			self.RCR.header.update(
				{
					'Host': 'cn.airbusan.com',
					'Pragma': 'no-cache',
					'Cache-Control': 'no-cache',
					'Accept': 'application/json, text/javascript, */*; q=0.01',
					'Sec-Fetch-Dest': 'empty',
					'X-Requested-With': 'XMLHttpRequest',
					'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					'Origin': 'https://cn.airbusan.com',
					'Sec-Fetch-Site': 'same-origin',
					'Sec-Fetch-Mode': 'cors',
					'Referer': 'https://cn.airbusan.com/web/individual/booking/internationalPurchase',
				}
			)
			if not self.RCR.request_to_post(page_type='json'):
				self.logger.info(f"支付失败, 支付页面获取失败 {self.RCR.url}")
				self.callback_msg = "支付失败"
				return False
			
			# 支付弹窗
			self.RCR.url = 'https://cn.airbusan.com/web/external/eximbayPaymentPrepare'
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.param_data = None
			self.RCR.post_data = {
				'purchaseFor': purchaseFor,
				'encrypt': encrypt
			}
			self.RCR.header.update(
				{
					'Host': 'cn.airbusan.com',
					'Pragma': 'no-cache',
					'Cache-Control': 'no-cache',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Sec-Fetch-Dest': 'empty',
					'Upgrade-Insecure-Requests': '1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Origin': 'https://cn.airbusan.com',
					'Sec-Fetch-Site': 'same-origin',
					'Sec-Fetch-Mode': 'navigate',
					'Referer': 'https://cn.airbusan.com/web/common/popup/popupWindowBase/HXFZO92KXK10FGN5G7UZ',
				}
			)
			if not self.RCR.request_to_post():
				self.logger.info(f"支付失败, 支付页面获取失败 {self.RCR.url}")
				self.callback_msg = "支付失败"
				return False
			
			if "errorConts" in self.RCR.page_source:
				errorConts, temp_list = self.DPR.parse_to_attributes('text', 'css', 'div[class="errorConts"] p strong',
				                                                     self.RCR.page_source)
				
				self.logger.info(f"支付失败 > {errorConts}")
				self.callback_msg = f"支付失败 > {errorConts}"
				return False
			
			# 获取支付链接
			pay_url, temp_list = self.DPR.parse_to_attributes('action', 'css', 'form[name="formEximbayPurchase"]',
			                                                  self.RCR.page_source)
			if not pay_url:
				self.logger.info(f"支付失败, 支付链接获取失败 pay_url")
				self.callback_msg = "支付失败"
				return False
			
			# 获取支付参数
			ver, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="ver"]',
			                                              self.RCR.page_source)
			mid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="mid"]',
			                                              self.RCR.page_source)
			
			txntype, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="txntype"]',
			                                                  self.RCR.page_source)
			
			ref, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="ref"]',
			                                              self.RCR.page_source)
			
			cur, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="cur"]',
			                                              self.RCR.page_source)
			
			amt, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="amt"]',
			                                              self.RCR.page_source)
			
			paymethod, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paymethod"]',
			                                                    self.RCR.page_source)
			
			ostype, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="ostype"]',
			                                                 self.RCR.page_source)
			
			shop, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="shop"]',
			                                               self.RCR.page_source)
			
			buyer, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="buyer"]',
			                                                self.RCR.page_source)
			
			tel, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="tel"]',
			                                              self.RCR.page_source)
			
			email, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="email"]',
			                                                self.RCR.page_source)
			
			lang, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="lang"]',
			                                               self.RCR.page_source)
			
			returnurl, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="returnurl"]',
			                                                    self.RCR.page_source)
			
			statusurl, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="statusurl"]',
			                                                    self.RCR.page_source)
			
			fgkey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="fgkey"]',
			                                                self.RCR.page_source)
			charset, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="charset"]',
			                                                  self.RCR.page_source)
			item_1_product, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="item_1_product"]',
			                                                         self.RCR.page_source)
			item_1_quantity, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="item_1_quantity"]',
			                                                          self.RCR.page_source)
			item_1_unitPrice, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="item_1_unitPrice"]',
			                                                           self.RCR.page_source)
			
			travelData_completeRoute, temp_list = self.DPR.parse_to_attributes('value', 'css',
			                                                                   'input[name="travelData_completeRoute"]',
			                                                                   self.RCR.page_source)
			travelData_departureDateTime, temp_list = self.DPR.parse_to_attributes('value', 'css',
			                                                                       'input[name="travelData_departureDateTime"]',
			                                                                       self.RCR.page_source)
			
			displaytype, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="displaytype"]',
			                                                      self.RCR.page_source)
			travelData_leg_1_origin, temp_list = self.DPR.parse_to_attributes('value', 'css',
			                                                                  'input[name="travelData_leg_1_origin"]',
			                                                                  self.RCR.page_source)
			travelData_leg_1_destination, temp_list = self.DPR.parse_to_attributes('value', 'css',
			                                                                       'input[name="travelData_leg_1_destination"]',
			                                                                       self.RCR.page_source)
			param1, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="param1"]',
			                                                 self.RCR.page_source)
			param2, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="param2"]',
			                                                 self.RCR.page_source)
			param3, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="param3"]',
			                                                 self.RCR.page_source)
			surcharge_1_name, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="surcharge_1_name"]',
			                                                           self.RCR.page_source)
			partnercode, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="partnercode"]',
			                                                      self.RCR.page_source)
			surcharge_1_quantity, temp_list = self.DPR.parse_to_attributes('value', 'css',
			                                                               'input[name="surcharge_1_quantity"]',
			                                                               self.RCR.page_source)
			supplyvalue, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="supplyvalue"]',
			                                                      self.RCR.page_source)
			
			self.RCR.url = pay_url
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.post_data = {
				"ver": ver,
				"mid": mid,
				"txntype": txntype,
				"ref": ref,
				"cur": cur,
				"amt": amt,
				"paymethod": paymethod,
				"shop": shop,
				"buyer": buyer,
				"tel": tel,
				"email": email,
				"lang": lang,
				"returnurl": returnurl,
				"statusurl": statusurl,
				"param1": param1,
				"param2": param2,
				"param3": param3,
				"charset": charset,
				"fgkey": fgkey,
				"partnercode": partnercode,
				"item_1_product": item_1_product,
				"item_1_quantity": item_1_quantity,
				"item_1_unitPrice": item_1_unitPrice,
				"surcharge_1_name": surcharge_1_name,
				"surcharge_1_quantity": surcharge_1_quantity,
				"surcharge_1_unitPrice": "",
				"shipTo_city": "",
				"shipTo_country": "",
				"shipTo_firstName": "",
				"shipTo_lastName": "",
				"shipTo_phoneNumber": "",
				"shipTo_postalCode": "",
				"shipTo_state": "",
				"shipTo_street1": "",
				"billTo_city": "",
				"billTo_country": "",
				"billTo_firstName": "",
				"billTo_lastName": "",
				"billTo_phoneNumber": "",
				"billTo_postalCode": "",
				"billTo_state": "",
				"billTo_street1": "",
				"ostype": ostype,
				"autoclose": "",
				"displaytype": displaytype,
				"issuercountry": "",
				"siteforeigncur": "",
				"supplyvalue": supplyvalue,
				"taxamount": "0",
				"travelData_leg_1_origin": travelData_leg_1_origin,
				"travelData_leg_1_destination": travelData_leg_1_destination,
				"travelData_leg_2_origin": "",
				"travelData_leg_2_destination": "",
				"travelData_leg_3_origin": "",
				"travelData_leg_3_destination": "",
				"travelData_leg_4_origin": "",
				"travelData_leg_4_destination": "",
				"travelData_completeRoute": travelData_completeRoute,
				"travelData_departureDateTime": travelData_departureDateTime,
				"travelData_journeyType": "",
				"third_party_booking": "",
				"corporate_booking": "",
				"hours_until_departure": "",
				"age_of_profile": "",
				"number_of_passengers": "",
				"fare_class": "",
				"baggage_purchased": "",
				"payer_pessenger": "",
				"agent_code": "",
				"agent_name": "",
			}
			self.RCR.param_data = None
			self.RCR.header.update(
				{
					'Host': 'secureapi.eximbay.com',
					'Origin': 'https://cn.airbusan.com',
					'Upgrade-Insecure-Requests': '1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Sec-Fetch-Dest': 'document',
					'Sec-Fetch-Site': 'cross-site',
					'Sec-Fetch-Mode': 'navigate',
					'Referer': 'https://cn.airbusan.com/web/external/eximbayPaymentPrepare',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				}
			)
			
			if not self.RCR.request_to_post():
				self.logger.info(f"支付失败, 打开支付页面失败{self.RCR.url}")
				self.callback_msg = "支付失败"
				return False
			
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			url, temp_list = self.DPR.parse_to_attributes('action', 'css', 'form[id="frm"]', self.RCR.page_source)
			self.RCR.url = "https://secureapi.eximbay.com" + url
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.param_data = None
			self.RCR.post_data = {
				"paramKey": paramKey
			}
			self.RCR.header.update(
				{
					'Host': 'secureapi.eximbay.com',
					'Origin': 'https://secureapi.eximbay.com',
					'Upgrade-Insecure-Requests': '1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Sec-Fetch-Dest': 'document',
					'Sec-Fetch-Site': 'same-origin',
					'Sec-Fetch-Mode': 'navigate',
					'Referer': pay_url,
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				}
			)
			if not self.RCR.request_to_post():
				self.logger.info(f"支付失败, 打开支付页面失败{self.RCR.url}")
				self.callback_msg = "支付失败"
				return False
			
			self.RCR.url = 'https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/mstep_cur_proc.do'
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			umh_method, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[id="umh_method"]',
			                                                     self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			
			self.RCR.post_data = {
				"paramKey": paramKey,
				"rescode": "",
				"resmsg": "",
				"cardType": "C000",
				"channel": "",
				"dcctype": "",
				"apprvcurrency": "",
				"apprvamount": "",
				"mcpstatus": "",
				"quotecurrency": "",
				"quoteamount": "",
				"payto": "",
				"finalCurrencyChoice": "",
				"smsValue": "",
				"pCode": "",
				"cardno": "4539615572495619",  # self.CPR.card_num,
				"payment_method": "C000",
				"viewcardno1": "4539",  # card_num1,
				"viewcardno2": "6155",  # card_num2,
				"viewcardno3": "7249",  # card_num3,
				"viewcardno4": "5619",  # card_num4,
				"viewcardno": "",
				"month": "01",  # card_month,
				"year": "2021",  # card_year,
				"cvv": "918",  # card_code,
				"fname": "MARISSA",  # self.CPR.card_first,
				"lname": "STANLEY",  # self.CPR.card_last,
				"email": "zl158218@163.com",  # self.CPR.contact_email,
				"billTo_street1": "",
				"billTo_country": "",
				"billTo_city": "",
				"billTo_state": "",
				"billTo_postalCode": "",
				"billTo_phoneNumber": "",
				"umh_method": umh_method,
				"umhcardno": "",
				"phoneid": "",
				"phoneno": "",
				"smscode": "",
				"montht": "",
				"yeart": "",
				"cvvt": "",
				"cert_id": "",
				"monthtxx": "",
				"yeartxx": "",
				"cvvtxx": "",
				"chinapnrcardno": "",
				"chinapnrpayername": "",
				"chinapnrpayerid": "",
			}
			
			# self.RCR.post_data = {
			#     "paramKey":paramKey,
			#     "rescode":"",
			#     "resmsg":"",
			#     "cardType":"C000",
			#     "channel":"",
			#     "dcctype":"",
			#     "apprvcurrency":"",
			#     "apprvamount":"",
			#     "mcpstatus":"",
			#     "quotecurrency":"",
			#     "quoteamount":"",
			#     "payto":"",
			#     "finalCurrencyChoice":"",
			#     "smsValue":"",
			#     "pCode":"",
			#     "cardno":self.CPR.card_num,
			#     "payment_method":"C000",
			#     "viewcardno1":card_num1,
			#     "viewcardno2":card_num2,
			#     "viewcardno3":card_num3,
			#     "viewcardno4":card_num4,
			#     "viewcardno":"",
			#     "month":card_month,
			#     "year":card_year,
			#     "cvv":card_code,
			#     "fname":self.CPR.card_first,
			#     "lname":self.CPR.card_last,
			#     "email":self.CPR.contact_email,
			#     "billTo_street1":"",
			#     "billTo_country":"",
			#     "billTo_city":"",
			#     "billTo_state":"",
			#     "billTo_postalCode":"",
			#     "billTo_phoneNumber":"",
			#     "umh_method":umh_method,
			#     "umhcardno":"",
			#     "phoneid":"",
			#     "phoneno":"",
			#     "smscode":"",
			#     "montht":"",
			#     "yeart":"",
			#     "cvvt":"",
			#     "cert_id":"",
			#     "monthtxx":"",
			#     "yeartxx":"",
			#     "cvvtxx":"",
			#     "chinapnrcardno":"",
			#     "chinapnrpayername":"",
			#     "chinapnrpayerid":"",
			# }
			self.RCR.param_data = None
			self.RCR.header.update(
				{
					'Host': 'secureapi.eximbay.com',
					'Upgrade-Insecure-Requests': '1',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Sec-Fetch-User': '?1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Origin': 'https://secureapi.eximbay.com',
					'Sec-Fetch-Site': 'same-origin',
					'Sec-Fetch-Mode': 'navigate',
					'Referer': 'https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/step1_1.do',
				}
			)
			if not self.RCR.request_to_post():
				self.logger.info(f"支付失败 | 提交账号信息失败 {self.RCR.url}")
				self.callback_msg = "支付失败 | 提交账号信息失败"
				return False
			
			# 确认金额,  阅读并接受条款和条件
			url, temp_list = self.DPR.parse_to_attributes('action', 'css', 'form[name="regForm"]',
			                                              self.RCR.page_source)
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			rescode, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="rescode"]',
			                                                  self.RCR.page_source)
			resmsg, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="resmsg"]',
			                                                 self.RCR.page_source)
			dcctype, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="dcctype"]',
			                                                  self.RCR.page_source)
			apprvcurrency, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="apprvcurrency"]',
			                                                        self.RCR.page_source)
			apprvamount, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="apprvamount"]',
			                                                      self.RCR.page_source)
			mcpstatus, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="mcpstatus"]',
			                                                    self.RCR.page_source)
			quotecurrency, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="quotecurrency"]',
			                                                        self.RCR.page_source)
			quoteamount, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="quoteamount"]',
			                                                      self.RCR.page_source)
			payto, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="payto"]', self.RCR.page_source)
			
			# https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/step1_2.do
			self.RCR.url = 'https://secureapi.eximbay.com' + url
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.post_data = {
				"paramKey": paramKey,
				"rescode": rescode,
				"resmsg": resmsg,
				"dcctype": dcctype,
				"apprvcurrency": apprvcurrency,
				"apprvamount": apprvamount,
				"mcpstatus": mcpstatus,
				"quotecurrency": quotecurrency,
				"quoteamount": quoteamount,
				"payto": payto,
			}
			self.RCR.param_data = None
			self.RCR.header.update(
				{
					'Host': 'secureapi.eximbay.com',
					'Origin': 'https://secureapi.eximbay.com',
					'Upgrade-Insecure-Requests': '1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Sec-Fetch-Site': 'same-origin',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Sec-Fetch-Mode': 'navigate',
					'Referer': 'https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/mstep_cur_proc.do',
				}
			)
			if not self.RCR.request_to_post():
				self.logger.info(f"支付失败 | 确认金额同意条款失败 {self.RCR.url}")
				self.callback_msg = "支付失败 | 确认金额同意条款失败"
				return False
			
			paramKey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paramKey"]',
			                                                   self.RCR.page_source)
			year, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="year"]', self.RCR.page_source)
			month, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="month"]',
			                                                self.RCR.page_source)
			viewcardno3, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="viewcardno3"]',
			                                                      self.RCR.page_source)
			viewcardno4, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="viewcardno4"]',
			                                                      self.RCR.page_source)
			viewcardno2, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="viewcardno2"]',
			                                                      self.RCR.page_source)
			viewcardno1, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="viewcardno1"]',
			                                                      self.RCR.page_source)
			finalCurrencyChoice, temp_list = self.DPR.parse_to_attributes('value', 'css',
			                                                              'input[name="finalCurrencyChoice"]',
			                                                              self.RCR.page_source)
			lname, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="lname"]',
			                                                self.RCR.page_source)
			fname, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="fname"]',
			                                                self.RCR.page_source)
			resmsg, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="resmsg"]',
			                                                 self.RCR.page_source)
			rescode, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="rescode"]',
			                                                  self.RCR.page_source)
			holder, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="holder"]',
			                                                 self.RCR.page_source)
			cvc, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="cvc"]',
			                                              self.RCR.page_source)
			
			self.RCR.url = "https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/step_confirm.do"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.post_data = {
				"paramKey": paramKey,
				"holder": holder,
				"rescode": rescode,
				"resmsg": resmsg,
				"fname": fname,
				"lname": lname,
				"finalCurrencyChoice": finalCurrencyChoice,
				"viewcardno1": viewcardno1,
				"viewcardno2": viewcardno2,
				"viewcardno3": viewcardno3,
				"viewcardno4": viewcardno4,
				"month": month,
				"year": year,
				"cvc": cvc,
				"dcc_pament": "on",
				"agree": "on"
			}
			
			self.RCR.param_data = None
			self.RCR.header.update(
				{
					'Host': 'secureapi.eximbay.com',
					'Origin': 'https://secureapi.eximbay.com',
					'Upgrade-Insecure-Requests': '1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Sec-Fetch-Site': 'same-origin',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Sec-Fetch-Dest': 'iframe',
					'Sec-Fetch-Mode': 'navigate',
					'Sec-Fetch-User': '?1',
					'Referer': 'https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/step1_2.do',
				}
			)
			if not self.RCR.request_to_post(is_redirect=True):
				self.logger.info(f"支付失败 | 确认金额同意条款失败 {self.RCR.url}")
				self.callback_msg = "支付失败 | 确认金额同意条款失败"
				return False
			
			pay_url, temp_list = self.DPR.parse_to_attributes('action', 'css', 'form[name="Visa3d"]',
			                                                  self.RCR.page_source)
			returnUrl, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="returnUrl"]',
			                                                    self.RCR.page_source)
			userid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="userid"]',
			                                                 self.RCR.page_source)
			
			expiry, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="expiry"]',
			                                                 self.RCR.page_source)
			purchase_amount, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="purchase_amount"]',
			                                                          self.RCR.page_source)
			transID, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="transID"]',
			                                                  self.RCR.page_source)
			recurExpiry, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="recurExpiry"]',
			                                                      self.RCR.page_source)
			recurFrequency, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="recurFrequency"]',
			                                                         self.RCR.page_source)
			currency, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="currency"]',
			                                                   self.RCR.page_source)
			exponent, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="exponent"]',
			                                                   self.RCR.page_source)
			hostid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hostid"]',
			                                                 self.RCR.page_source)
			hostpwd, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hostpwd"]',
			                                                  self.RCR.page_source)
			name, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="name"]',
			                                               self.RCR.page_source)
			installment, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="installment"]',
			                                                      self.RCR.page_source)
			country, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="country"]',
			                                                  self.RCR.page_source)
			device_category, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="device_category"]',
			                                                          self.RCR.page_source)
			description, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="description"]',
			                                                      self.RCR.page_source)
			pan, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="pan"]',
			                                              self.RCR.page_source)
			useActiveX, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="useActiveX"]',
			                                                     self.RCR.page_source)
			
			url, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="url"]',
			                                              self.RCR.page_source)
			
			# 提交付款信息
			self.RCR.url = pay_url
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.post_data = {
				"returnUrl": returnUrl,
				"pan": pan,
				"expiry": expiry,
				"purchase_amount": purchase_amount,
				"exponent": 0,
				"currency": currency,
				"recurFrequency": recurFrequency,
				"recurExpiry": recurExpiry,
				"userid": userid,
				"transID": transID,
				"country": country,
				"installment": installment,
				"name": name,
				"url": url,
				"hostid": hostid,
				"hostpwd": hostpwd,
				"description": description,
				"device_category": device_category,
				"useActiveX": useActiveX
			}
			
			self.RCR.header.update(
				{
					'Host': 'secureapi.eximbay.com',
					'Origin': 'https://secureapi.eximbay.com',
					'Upgrade-Insecure-Requests': '1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Sec-Fetch-Site': 'same-origin',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Sec-Fetch-Dest': 'iframe',
					'Sec-Fetch-Mode': 'navigate',
					'Sec-Fetch-User': '?1',
					'Referer': self.RCR.response_url,
				}
			)
			if not self.RCR.request_to_post():
				self.logger.info(f"支付失败 | 确认金额同意条款失败 {self.RCR.url}")
				self.callback_msg = "支付失败 | 确认金额同意条款失败"
				return False
			
			PaReq, temp_list = self.BPR.parse_to_regex("input.*?PaReq.*?\=\"(.*?)\"",
			                                           self.RCR.page_source)
			TermUrl, temp_list = self.BPR.parse_to_regex("input.*?TermUrl.*?\=\"(.*?)\"",
			                                             self.RCR.page_source)
			MD, temp_list = self.BPR.parse_to_regex("input.*?MD.*?\=\"(.*?)\"",
			                                        self.RCR.page_source)
			paramKey, temp_list = self.BPR.parse_to_regex("input.*?paramKey.*?\=\"(.*?)\"",
			                                              self.RCR.page_source)
			
			self.RCR.url = "https://sas.redsys.es/sas/Secure"
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.post_data = {
				"PaReq": PaReq,
				"TermUrl": TermUrl,
				"MD": MD,
				"paramKey": paramKey,
			}
			self.RCR.header.update(
				{
					'Host': 'sas.redsys.es',
					'Origin': 'https://secureapi.eximbay.com',
					'Upgrade-Insecure-Requests': '1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Sec-Fetch-Site': 'cross-site',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Sec-Fetch-Dest': 'iframe',
					'Sec-Fetch-Mode': 'navigate',
					'Sec-Fetch-User': '?1',
					'Referer': self.RCR.response_url,
				}
			)
			if not self.RCR.request_to_post():
				self.logger.info(f"支付失败 | 确认金额同意条款失败 {self.RCR.url}")
				self.callback_msg = "支付失败 | 提交支付信息"
				return False
			
			url, temp_list = self.DPR.parse_to_attributes('action', 'css', 'form[name="respuesta"]',
			                                              self.RCR.page_source)
			MD, temp_list = self.BPR.parse_to_regex("name\=\"MD.*?\=\"(.*?)\"",
			                                        self.RCR.page_source)
			PaRes, temp_list = self.BPR.parse_to_regex("name\=\"PaRes.*?\=\"(.*?)\"",
			                                           self.RCR.page_source)
			self.logger.info(MD)
			
			self.RCR.url = url
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.post_data = {
				"MD": MD,
				"PaRes": PaRes,
			}
			self.RCR.header.update(
				{
					'Host': 'secureapi.eximbay.com',
					'Origin': 'https://sas.redsys.es',
					'Upgrade-Insecure-Requests': '1',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Sec-Fetch-Dest': 'iframe',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Sec-Fetch-Site': 'cross-site',
					'Sec-Fetch-Mode': 'navigate',
					'Referer': self.RCR.response_url,
				}
			)
			if not self.RCR.request_to_post():
				self.logger.info(f"支付失败 | 确认金额同意条款失败 {self.RCR.url}")
				self.callback_msg = "支付失败 | 提交支付信息"
				return False
			
			# 获取支付结果页面
			url, temp_list = self.BPR.parse_to_regex("parent.location.href\=\"(.*?)\"\;", self.RCR.page_source)
			self.logger.info(url)
			self.RCR.url = "https://secureapi.eximbay.com" + url
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.post_data = None
			self.RCR.param_data = None
			self.RCR.header.update(
				{
					'Host': 'secureapi.eximbay.com',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'Sec-Fetch-Site': 'same-origin',
					'Sec-Fetch-Mode': 'navigate',
					'Sec-Fetch-Dest': 'document',
					'Referer': self.RCR.response_url,
				}
			)
			if not self.RCR.request_to_get():
				self.logger.info(f"支付失败 | 支付结果信息获取失败 {self.RCR.url}")
				self.callback_msg = "支付失败 | 支付结果信息获取失败"
				return False
			
			# 提取支付结果
			pay_result, temp_list = self.DPR.parse_to_attributes('text', 'css', 'div[class="inp_wrap"] p',
			                                                     self.RCR.page_source)
			pay_result = self.BPR.parse_to_clear(pay_result)
			
			pay_msg, temp_list = self.DPR.parse_to_attributes('text', 'css', 'div[class="inp_wrap02 align_left"]',
			                                                  self.RCR.page_source.replace('br', ""))
			pay_msg = self.BPR.parse_to_clear(pay_msg)
			pay_msg = pay_msg.split('处理结果:')
			self.logger.info(pay_result)
			self.logger.info(pay_msg)
			if "失败" in pay_result:
				self.logger.info(f"支付失败 | 支付卡可能有问题 | 页面结果 {pay_msg} | {pay_msg}")
				self.callback_msg = f"支付失败 | 支付卡可能有问题 | 页面结果: {pay_result} | {pay_msg[-1]}"
				return False
			
			#  以上代码第一种支付链接, 如果真卡, 可能会支付成功
			time.sleep(100000)
			
			#  以下代码是第二种支付链接,
			total_price, temp_list = self.DPR.parse_to_attributes('text', 'css', 'strong span[class="nativePrice"]',
			                                                      self.RCR.page_source)
			
			self.total_price = self.BFR.format_to_float(2, total_price)  # 总价
			self.RCR.url = 'https://cn.airbusan.com/web/PurchaseApi/jpyPrepare'
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.post_data = {'ordAmount': f'{int(self.total_price)}'}
			self.RCR.param_data = None
			self.RCR.header.update(
				{
					'Host': 'cn.airbusan.com',
					'Accept': 'application/json, text/javascript, */*; q=0.01',
					'Sec-Fetch-Dest': 'empty',
					'X-Requested-With': 'XMLHttpRequest',
					'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					'Origin': 'https://cn.airbusan.com',
					'Sec-Fetch-Site': 'same-origin',
					'Sec-Fetch-Mode': 'navigate',
					'Pragma': 'no-cache',
					'Cache-Control': 'no-cache',
					'Referer': 'https://cn.airbusan.com/web/individual/booking/internationalPurchase',
				}
			)
			if self.RCR.request_to_post(page_type='json'):
				ecnToken, temp_list = self.BPR.parse_to_path('$.ecnToken', self.RCR.page_source)
				url, temp_list = self.BPR.parse_to_path('$.cardentryURL', self.RCR.page_source)
				self.logger.info(ecnToken)
				if not ecnToken:
					self.logger.info("ecnToken 获取失败 ,支付失败")
					self.callback_msg = "支付失败, 获取支付信息失败"
					return False
				
				# self.RCR.url= "https://cn.airbusan.com/web/common/popup/popupWindowBase/RF9GQ9CQ59LTD1QKA4FF"
				# self.RCR.header.update(
				#     {
				#         'Host': 'cn.airbusan.com',
				#         'Upgrade-Insecure-Requests': '1',
				#         'Sec-Fetch-Dest': 'document',
				#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				#         'Sec-Fetch-Site': 'same-origin',
				#         'Sec-Fetch-Mode': 'navigate',
				#         'Sec-Fetch-User': '?1'
				#     }
				# )
				# if not self.RCR.request_to_get():
				#     self.logger.info("支付失败, 打开弹窗失败")
				#     self.callback_msg = "支付失败"
				#     return False
				
				self.RCR.url = url
				
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.post_data = {'ecnToken': f'{ecnToken}'}
				self.RCR.param_data = None
				self.RCR.header.update(
					{
						'Host': 'www5.econ.ne.jp',
						'Origin': 'https://cn.airbusan.com',
						'Upgrade-Insecure-Requests': '1',
						'Content-Type': 'application/x-www-form-urlencoded',
						'Sec-Fetch-Dest': 'document',
						'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
						'Referer': 'https://cn.airbusan.com/web/common/popup/popupWindowBase/RF9GQ9CQ59LTD1QKA4FF',
						'Sec-Fetch-Site': 'cross-site',
						'Sec-Fetch-Mode': 'navigate',
					}
				)
				if self.RCR.request_to_post():
					self.RCR.url, temp_list = self.BPR.parse_to_regex("RedirectPCPage\(\'(.*?)\'\,",
					                                                  self.RCR.page_source)
					url = self.RCR.url
					if not self.RCR.url:
						self.logger.info("支付失败, 打开弹窗失败")
						self.callback_msg = "支付页面链接获取失败"
						return False
					
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.post_data = {'ecnToken': f'{ecnToken}'}
					self.RCR.param_data = None
					self.RCR.header.update(
						{
							'Host': 'www5.econ.ne.jp',
							'Origin': 'https://www5.econ.ne.jp',
							'Upgrade-Insecure-Requests': '1',
							'Content-Type': 'application/x-www-form-urlencoded',
							'Sec-Fetch-Dest': 'document',
							'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
							'Referer': self.RCR.url,
							'Sec-Fetch-Site': 'same-origin',
							'Sec-Fetch-Mode': 'navigate',
						}
					)
					if self.RCR.request_to_post():
						
						lng, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="lng"]',
						                                              self.RCR.page_source)
						cardentryData, temp_list = self.DPR.parse_to_attributes('value', 'css',
						                                                        'input[name="cardentryData"]',
						                                                        self.RCR.page_source)
						ecnToken, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="ecnToken"]',
						                                                   self.RCR.page_source)
						VIEWSTATE, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[id="__VIEWSTATE"]',
						                                                    self.RCR.page_source)
						# EVENTTARGET, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[id="__VIEWSTATE"]', self.RCR.page_source)
						EVENTVALIDATION, temp_list = self.DPR.parse_to_attributes('value', 'css',
						                                                          'input[id="__EVENTVALIDATION"]',
						                                                          self.RCR.page_source)
						
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
						
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.post_data = {
							'lng': lng,
							'cardentryData': cardentryData,
							'ecnToken': ecnToken,
							'__VIEWSTATE': VIEWSTATE,
							'__EVENTTARGET': 'ctl00$cphMain$btnMoveNext',
							'__EVENTARGUMENT': '',
							'__EVENTVALIDATION': EVENTVALIDATION,
							'ctl00$cphMain$txtNewCardNumber': self.CPR.card_num,
							'ctl00$cphMain$ddlNewAvailableMonth': card_month,
							'ctl00$cphMain$ddlNewAvailableYear': card_year,
							'ctl00$cphMain$txtNewCardOwner': f'{self.CPR.card_last} {self.CPR.card_first}',
							'ctl00$cphMain$txtNewCvv2Code': card_code
						}
						self.RCR.param_data = None
						self.RCR.header.update(
							{
								'Host': 'www5.econ.ne.jp',
								'Pragma': 'no-cache',
								'Cache-Control': 'no-cache',
								'Origin': 'https://www5.econ.ne.jp',
								'Upgrade-Insecure-Requests': '1',
								'Content-Type': 'application/x-www-form-urlencoded',
								'Sec-Fetch-Site': 'same-origin',
								'Sec-Fetch-Mode': 'navigate',
								'Sec-Fetch-User': '?1',
								'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
								'Referer': url,
							}
						)
						if not self.RCR.request_to_post():
							self.logger.info(f"支付失败 {self.RCR.url}")
							self.callback_msg = "支付失败"
							return False
						
						# Host: www5.econ.ne.jp
						# Pragma: no-cache
						# Cache-Control: no-cache
						# Origin: https://www5.econ.ne.jp
						# Upgrade-Insecure-Requests: 1
						# Content-Type: application/x-www-form-urlencoded
						# :
						# Accept:
						# Sec-Fetch-Site: same-origin
						# Sec-Fetch-Mode: navigate
						# Sec-Fetch-User: ?1
						# Referer: https://www5.econ.ne.jp/pay/CardOrder/index.aspx?cardentryData=NTI5MDAzOzBhMGQ0YmNhMzI0YzRhY2E4ZWQ5MDZlMmM1Yzg5OTQ5&lng=1
						# Accept-Encoding: gzip, deflate, br
						# Accept-Language: zh-CN,zh;q=0.9
						# lng=1&cardentryData=NTI5MDAzOzBhMGQ0YmNhMzI0YzRhY2E4ZWQ5MDZlMmM1Yzg5OTQ5&ecnToken=ZjcxNTJmZDItNzU3Yi00M2QwLTkzMGEtYTNkNTMyOThmN2IyOzIwMjAvMDIvMjYgMTE6MDg6MTU%3D&__VIEWSTATE=%2FwEPDwULLTExMDYzODI4MDYPFhweGFJlZ2lzdGVyZWRDYXJkU2VjdXJlQ29kZWUeDE5ld0NhcmRPd25lcgUPTUFSSVNTQSBTVEFOTEVZHhxSZWdpc3RlcmVkQ2FyZEF2YWlsYWJsZU1vbnRoZR4TUmVnaXN0ZXJlZENhcmRMYXN0NGUeFE5ld0NhcmRBdmFpbGFibGVZZWFyBQQyMDIxHhNJc1VzZVJlZ2lzdGVyZWRDYXJkaB4NTmV3Q2FyZE51bWJlcgUQNDUzOTYxNTU3MjQ5NTYxOR4VTmV3Q2FyZEF2YWlsYWJsZU1vbnRoBQIwMR4aUmVnaXN0ZXJlZENhcmREaXZpc2lvbktpbmQFAjAwHhFOZXdDYXJkU2VjdXJlQ29kZQUDOTE4HhtSZWdpc3RlcmVkQ2FyZEF2YWlsYWJsZVllYXJlHhNOZXdDYXJkRGl2aXNpb25LaW5kBQIwMB4VUmVnaXN0ZXJlZENhcmRCaW5Db2RlZR4QSXNSZWdpc3RlcmVkVXNlcmgWAmYPZBYGAgEPZBYEAgYPFgIeBGhyZWYFKC9wYXlfY29tbW9uL2Nzcy9jb2xvci1zY2hlbWVfYmx1ZV9lbi5jc3NkAgcPFgIfDgUbL3BheV9jb21tb24vY3NzL2JnX2JsdWUuY3NzZAIDD2QWDGYPDxYEHghTaXRlTmFtZQUP44Ko44Ki44OX44K144OzHghTaXRlTG9nb2VkZAIBD2QWBAIBD2QWAmYPDxYCHgRUZXh0BQRCYWNrZGQCAw9kFgJmDw8WAh8RBQZTdWJtaXRkZAICDw8WBB4LQmFubmVySW1hZ2VlHgpCYW5uZXJMaW5rZWRkAgMPDxYCHgVDbGFzcwUOQm9keSBCdG1Cb3JkZXJkZAIEDw8WBh4ISEVMUF9GTEcFATIeCUhFTFBfVEVYVGUeDUhFTFBfTElOS19VUkxlZGQCBQ8PFgIeCVRhZ1N0cmluZwXvAzxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0Ij52YXIgX2dhcSA9IF9nYXEgfHwgW107X2dhcS5wdXNoKFsnX3NldEFjY291bnQnLCAnVUEtMzQwODM1MjctMSddKTtfZ2FxLnB1c2goWydfc2V0RG9tYWluTmFtZScsICdlY29uLm5lLmpwJ10pO19nYXEucHVzaChbJ190cmFja1BhZ2V2aWV3JywgJ0NPUkQwMjAnXSk7KGZ1bmN0aW9uKCkge3ZhciBnYSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ3NjcmlwdCcpOyBnYS50eXBlID0gJ3RleHQvamF2YXNjcmlwdCc7IGdhLmFzeW5jID0gdHJ1ZTtnYS5zcmMgPSAoJ2h0dHBzOicgPT0gZG9jdW1lbnQubG9jYXRpb24ucHJvdG9jb2wgPyAnaHR0cHM6Ly9zc2wnIDogJ2h0dHA6Ly93d3cnKSArICcuZ29vZ2xlLWFuYWx5dGljcy5jb20vZ2EuanMnO3ZhciBzID0gZG9jdW1lbnQuZ2V0RWxlbWVudHNCeVRhZ05hbWUoJ3NjcmlwdCcpWzBdOyBzLnBhcmVudE5vZGUuaW5zZXJ0QmVmb3JlKGdhLCBzKTt9KSgpOzwvc2NyaXB0PmRkAgUPDxYEHgpLYWtha3VUb29sBQEwHghIb3N0TmFtZQUPd3d3NS5lY29uLm5lLmpwZGRk&__EVENTTARGET=ctl00%24cphMain%24btnMoveNext&__EVENTARGUMENT=
						
						self.RCR.url = "https://www5.econ.ne.jp/pay/CardOrder/credit-confirm.aspx?lng=1"
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update(
							{
								'Host': 'www5.econ.ne.jp',
								'Pragma': 'no-cache',
								'Cache-Control': 'no-cache',
								'Origin': 'https://www5.econ.ne.jp',
								'Upgrade-Insecure-Requests': '1',
								'Content-Type': 'application/x-www-form-urlencoded',
								'Sec-Fetch-Dest': 'document',
								'Sec-Fetch-Site': 'same-origin',
								'Sec-Fetch-Mode': 'navigate',
								'Sec-Fetch-User': '?1',
								'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
								'Referer': self.RCR.url,
							}
						)
						
						self.RCR.post_data = {
							'lng': lng,
							'cardentryData': cardentryData,
							'ecnToken': ecnToken,
							'__VIEWSTATE': VIEWSTATE,
							'__EVENTTARGET': 'ctl00$cphMain$btnMoveNext',
							'__EVENTARGUMENT': '',
							'__EVENTVALIDATION': EVENTVALIDATION,
							'ctl00$cphMain$txtNewCardNumber': self.CPR.card_num,
							'ctl00$cphMain$ddlNewAvailableMonth': card_month,
							'ctl00$cphMain$ddlNewAvailableYear': card_year,
							'ctl00$cphMain$txtNewCardOwner': f'{self.CPR.card_last} {self.CPR.card_first}',
							'ctl00$cphMain$txtNewCvv2Code': card_code
						}
						self.RCR.param_data = None
						
						if not self.RCR.request_to_post():
							time.sleep(10000)
			
			time.sleep(10000)
			
			# 支付参数
			bookingCategory, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="bookingCategory"]',
			                                                          self.RCR.page_source)
			hd_approve_no, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_approve_no"]',
			                                                        self.RCR.page_source)
			hd_ep_option, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_ep_option"]',
			                                                       self.RCR.page_source)
			hd_ep_type, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_ep_type"]',
			                                                     self.RCR.page_source)
			hd_firm_name, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_firm_name"]',
			                                                       self.RCR.page_source)
			hd_input_option, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_input_option"]',
			                                                          self.RCR.page_source)
			hd_msg_code, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_msg_code"]',
			                                                      self.RCR.page_source)
			
			hd_msg_type, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_msg_type"]',
			                                                      self.RCR.page_source)
			
			hd_pi, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_pi"]',
			                                                self.RCR.page_source)
			hd_pre_msg_type, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_pre_msg_type"]',
			                                                          self.RCR.page_source)
			hd_serial_no, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_serial_no"]',
			                                                       self.RCR.page_source)
			hd_timeout, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_timeout"]',
			                                                     self.RCR.page_source)
			hd_timeout_yn, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="hd_timeout_yn"]',
			                                                        self.RCR.page_source)
			jumun_no, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="jumun_no"]',
			                                                   self.RCR.page_source)
			tx_age_check, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="tx_age_check"]',
			                                                       self.RCR.page_source)
			tx_amount, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="tx_amount"]',
			                                                    self.RCR.page_source)
			tx_bill_deduction, temp_list = self.DPR.parse_to_attributes('value', 'css',
			                                                            'input[name="tx_bill_deduction"]',
			                                                            self.RCR.page_source)
			tx_bill_yn, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="tx_bill_yn"]',
			                                                     self.RCR.page_source)
			
			tx_email_addr, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="tx_email_addr"]',
			                                                        self.RCR.page_source)
			tx_receipt_acnt, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="tx_receipt_acnt"]',
			                                                          self.RCR.page_source)
			tx_user_define, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="tx_user_define"]',
			                                                         self.RCR.page_source)
			
			self.encryptPnr, temp_list = self.DPR.parse_to_attributes('value', 'xpath',
			                                                          '//input[@name="encryptPnr"]/@value',
			                                                          self.RCR.page_source)
			payType, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[id="acbeximbay"]',
			                                                  self.RCR.page_source)
			emailId, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[id="emailId"]',
			                                                  self.RCR.page_source)
			emailDomain, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[id="emailDomain"]',
			                                                      self.RCR.page_source)
			parameters = {
				"uri": "/web/bookingApi/internationalTicketing",
				"method": "post",
				"target": "XNVOQBDUPI5SQUDUMX5T",
				"mapBody": {
					"bookingCategory": [
						"Individual"
					],
					"encryptPnr": [
						self.encryptPnr
					],
					"ep_order_no": [
						""
					],
					"kp_order_no": [
						""
					],
					"bp_order_no": [
						""
					],
					"eb_order_no": [
						""
					],
					"orderId": [
						""
					],
					"hd_approve_no": [
						hd_approve_no
					],
					"hd_ep_option": [
						hd_ep_option
					],
					"hd_ep_type": [
						hd_ep_type
					],
					"hd_firm_name": [
						hd_firm_name
					],
					"hd_input_option": [
						hd_input_option
					],
					"hd_msg_code": [
						hd_msg_code
					],
					"hd_msg_type": [
						hd_msg_type
					],
					"hd_pi": [
						hd_pi
					],
					"hd_pre_msg_type": [
						hd_pre_msg_type
					],
					"hd_serial_no": [
						hd_serial_no
					],
					"hd_timeout": [
						hd_timeout
					],
					"hd_timeout_yn": [
						hd_timeout_yn
					],
					"jumun_no": [
						jumun_no
					],
					"tx_age_check": [
						tx_age_check
					],
					"tx_amount": [
						tx_amount
					],
					"tx_bill_deduction": [
						tx_bill_deduction
					],
					"tx_bill_yn": [
						tx_bill_yn
					],
					"tx_email_addr": [
						tx_email_addr
					],
					"tx_receipt_acnt": [
						tx_receipt_acnt
					],
					"tx_user_define": [
						tx_user_define
					],
					"payType": [
						payType
					],
					"cardList": [
						""
					],
					"quota": [
						"00"
					],
					"cardNo1": [
						""
					],
					"cardNo2": [
						""
					],
					"cardNo3": [
						""
					],
					"cardNo4": [
						""
					],
					"expireMonth": [
						""
					],
					"expireYear": [
						""
					],
					"email": [
						"",
						""
					],
					"emailId": [
						emailId,
						emailId
					],
					"emailDomain": [
						emailDomain,
						emailDomain
					]
				}
			}
			
			self.baggage_price, temp_list = self.DPR.parse_to_attributes('text', 'css',
			                                                             '[class="section"] tr td:nth-child(3) [class="nativePrice"]',
			                                                             self.RCR.page_source)
			self.baggage_price = self.BFR.format_to_float(2, self.baggage_price)  # 行李价格
			self.logger.info(f"货 币： {self.CPR.currency}")
			self.logger.info(f"总 价： {self.total_price}")
			self.logger.info(f"行李价格： {self.baggage_price}")
			
			# # # # 进行比价
			if self.process_to_compare() == False:
				return False
			
			self.return_price = self.total_price - self.baggage_price  # 返回的价格
			
			unit_price = self.baggage_price / self.kilogram
			
			# # # # # #  返回行李 # # # # # # # #
			for passenger in self.CPR.adult_list:
				for i in passenger.get('baggage'):
					i['price'] = i.get('weight') * unit_price
					self.CPR.return_baggage.append(i)
			
			for passenger in self.CPR.child_list:
				for i in passenger.get('baggage'):
					i['price'] = i.get('weight') * unit_price
					self.CPR.return_baggage.append(i)
					#
					# self.RCR.url = 'https://cn.airbusan.com/web/PurchaseApi/needToPurchase'
					# self.RCR.header.update(
					#     {
					#         'Host': 'cn.airbusan.com',
					#         'Accept': 'application/json, text/javascript, */*; q=0.01',
					#         'Origin': 'https://cn.airbusan.com',
					#         'X-Requested-With': 'XMLHttpRequest',
					#         'Sec-Fetch-Site': 'same-origin',
					#         'Sec-Fetch-Mode': 'cors',
					#         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					#         'Referer': 'https://cn.airbusan.com/web/individual/booking/internationalPurchase'
					#     }
					# )
					# self.RCR.post_data = {
					#     'purchaseFor':'InternationalBooking',
					#     'encrypt':self.encryptPnr
					# }
					# if self.RCR.request_to_post():
					
					# self.RCR.url = 'https://cn.airbusan.com/web/common/popup/popupWindowBase/EHO810U5X7I1AVI7X8SP'
					# self.RCR.header = self.BFR.format_to_same(self.init_header)
					# self.RCR.post_data = None
					# self.RCR.param_data = None
					# self.RCR.header.update(
					#     {
					#         'Host': 'cn.airbusan.com',
					#         'Sec-Fetch-User': '?1',
					#         'Upgrade-Insecure-Requests': '1',
					#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					#         'Sec-Fetch-Site': 'same-origin',
					#         'Sec-Fetch-Mode': 'navigate',
					#         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					#         'Referer': 'https://cn.airbusan.com/web/individual/booking/internationalPurchase'
					#     }
					# )
					# if self.RCR.request_to_get():
					#     self.RCR.url = 'https://cn.airbusan.com/web/external/eximbayPaymentPrepare'
					#     self.RCR.header = self.BFR.format_to_same(self.init_header)
					#     self.RCR.param_data = None
					#     self.RCR.header.update(
					#         {
					#             'Host': 'cn.airbusan.com',
					#             'Origin': 'https://cn.airbusan.com',
					#             'Upgrade-Insecure-Requests': '1',
					#             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					#             'Sec-Fetch-Site': 'same-origin',
					#             'Sec-Fetch-Mode': 'navigate',
					#             'Referer': 'https://cn.airbusan.com/web/common/popup/popupWindowBase/EHO810U5X7I1AVI7X8SP'
					#         }
					#     )
					#     self.RCR.post_data = '''purchaseFor=''' + bookingCategory + '''&encrypt=''' + self.encryptPnr + '''&jsonFormComplete=''' + str(parameters)
					#     if self.RCR.request_to_post():
					# mid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="mid"]',
					#                                                       self.RCR.page_source)
					# amt, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="amt"]',
					#                                               self.RCR.page_source)
					# ref, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="ref"]',
					#                                               self.RCR.page_source)
					# cur, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="cur"]',
					#                                               self.RCR.page_source)
					# paymethod, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="paymethod"]',
					#                                               self.RCR.page_source)
					# ver, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="ver"]',
					#                                               self.RCR.page_source)
					# fgkey, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="fgkey"]',
					#                                               self.RCR.page_source)
					# txntype, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="txntype"]',
					#                                               self.RCR.page_source)
					# mid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="mid"]',
					#                                               self.RCR.page_source)
					# mid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="mid"]',
					#                                               self.RCR.page_source)
					# mid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="mid"]',
					#                                               self.RCR.page_source)
					# mid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="mid"]',
					#                                               self.RCR.page_source)
					# mid, temp_list = self.DPR.parse_to_attributes('value', 'css', 'input[name="mid"]',
					#                                               self.RCR.page_source)
					
					# self.RCR.url = 'https://cn.airbusan.com/web/external/eximbayPaymentCallback'
					# self.RCR.header = self.BFR.format_to_same(self.init_header)
					# self.RCR.param_data = None
					# self.RCR.header.update(
					#     {
					#         'Host': 'cn.airbusan.com',
					#         'Origin': 'https://secureapi.eximbay.com',
					#         'Upgrade-Insecure-Requests': '1',
					#         'Content-Type': 'application/x-www-form-urlencoded',
					#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					#         'Sec-Fetch-Site': 'cross-site',
					#         'Sec-Fetch-Mode': 'navigate',
					#
					#         'Referer': 'https://secureapi.eximbay.com/Gateway/BasicProcessor/2.x/close_utf8.do'
					#     }
					# )
					# # self.card_num
					# self.RCR.post_data = '''baserate=1.000000&cur=KRW&dm_reject=&cardno1='''+ self.CPR.card_num[:4] +'''&resdt=20200122180236&cardno4='''+ self.CPR.card_num[4:] +'''&foreignrate=1.000000&mid=''' + mid + '''&amt=92800&accesscountry=CN&tid=6211865&memberno=701439184&ref=D8613855200122180147&paymethod=P102&dm_review=&expirydt=PT%2FTgcLf8IY51IR5KkoQpQ%3D%3D&email=168033518%40qq.com&payerauth=Y&ver=220&foreignamt=92800.0&basecur=KRW&dccrate=1.000000&transid=5977F76C6620200122000182&dm_decision=&cardholder=JIAN+WANG&param3=&resmsg=Successful+transaction&cardno=NxPSWL8I5oY4KeRqGG9F2hOcRrAYfkw6eA%2FmqdYbBp4%3D&rescode=0000&param1=&param2=&authcode=X87298&fgkey=9206B7E4C76AEEF0A5B74193B83C21F13C315897DED84E21B0DE6C049EAC3A45&txntype=PAYMENT&foreigncur=KRW&baseamt=92800.0&payto=AIR+BUSAN.+Co.%2C+Ltd'''
					# if self.RCR.request_to_post():
					
					return True
			
			return True
		
		self.logger.info("支付页面获取失败 (*>﹏<*)【process_to_payment】")
		self.callback_msg = "支付页面获取失败"
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
		               f"foreignCurrency={self.CPR.currency}&carrier=UO"
		self.RCR.param_data = None
		self.RCR.header = self.BFR.format_to_same(self.init_header)
		self.RCR.post_data = None
		if self.RCR.request_to_get("json"):
			# # # 解析汇率转换人民币价格。
			exchange = self.RCR.page_source.get(self.CPR.currency)
			exchange_price = self.BFR.format_to_float(2, self.total_price * exchange)  # 总价
			if not exchange or not exchange_price:
				self.logger.info(f"转换汇率价格失败(*>﹏<*)【{self.RCR.page_source}】")
				self.callback_msg = "转换汇率价格失败，请通知技术检查程序。"
				return False
			# # # 进行接口比价。
			target_price = self.BFR.format_to_float(2, self.CPR.target_price)  # 目标价格
			diff_price = self.BFR.format_to_float(2, self.CPR.diff_price)  # 差价
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