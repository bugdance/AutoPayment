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
from collector.corpsl_mirror import CorpSLMirror
from detector.corpsl_simulator import CorpSLSimulator


class CorpSLScraper(RequestWorker):
	"""SL采集器，SL网站流程交互，企业账号不支持并发，行李价格区分人不准。"""
	
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
		self.CMR = CorpSLMirror()  # SL镜像器。
		self.CSR = CorpSLSimulator()  # SL模拟器。
		# # # 过程中重要的参数。
		self.captcha_num: str = ""  # 打码数字
		self.login_target: str = ""  # 登录t
		self.user_hdn: str = ""  # 登录user hdn
		self.sid: str = ""
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
		self.CMR.logger = self.logger
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
		self.CPR.currency = "CNY"
		self.RCR.timeout = 40
		self.record = self.CPR.pnr_code
		# # # 主体流程。
		if not self.record:
			self.logger.info(f"SL必须传票号支付(*>﹏<*)【{self.record}】")
			self.callback_msg = "SL必须传票号支付。"
			self.callback_data['msg'] = self.callback_msg
			self.logger.info(self.callback_data)
			self.logger.removeHandler(self.handler)
			return self.callback_data
		else:
			if self.process_to_verify(max_count=self.retry_count):
				if self.process_to_detail(max_count=self.retry_count):
					if self.process_to_payment():
						self.process_to_return()
						self.process_to_logout(max_count=self.retry_count)
						self.logger.removeHandler(self.handler)
						return self.callback_data
		# # # 错误返回。
		self.callback_data['msg'] = self.callback_msg
		# self.callback_data['msg'] = "解决问题中，请手工支付。"
		self.logger.info(self.callback_data)
		self.process_to_logout(max_count=self.retry_count)
		self.logger.removeHandler(self.handler)
		return self.callback_data
	
	def process_to_verify(self, count: int = 0, max_count: int = 3) -> bool:
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
			# # # 爬取登录首页。
			self.RCR.url = "https://agent.lionairthai.com/b2badmin/login.aspx"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "agent.lionairthai.com",
				"Upgrade-Insecure-Requests": "1"
			})
			if self.RCR.request_to_get():
				# # # 解析首页获取打码地址，并保存首页源代码。
				self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
				captcha, temp_list = self.DPR.parse_to_attributes(
					"src", "css", "#ucAgentLogin_rdCapImage_CaptchaImageUP", self.RCR.page_source)
				if captcha:
					# # # 爬取打码图片
					self.RCR.url = captcha.replace("..", "https://agent.lionairthai.com")
					self.RCR.param_data = None
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
						"Host": "agent.lionairthai.com",
						"Referer": "https://agent.lionairthai.com/b2badmin/login.aspx"
					})
					if self.RCR.request_to_get("content"):
						captcha_page = self.BFR.format_to_same(self.RCR.page_source)
						# # # 先进行接口打码
						self.RCR.url = "http://45.81.129.1:33333/captcha/sl/"
						self.RCR.param_data = None
						self.RCR.header = None
						self.RCR.post_data = {"img": self.RCR.page_source}
						if self.RCR.request_to_post("files", "json"):
							self.captcha_num = self.RCR.page_source.get('result')
						else:
							# # # 失败则进行自定义打码
							code_string = self.CSR.recognize_to_captcha("img/cap.jpg", captcha_page)
							code_regex, code_list = self.BPR.parse_to_regex("\d+", code_string)
							if code_list:
								code_all = ""
								for i in code_list:
									code_all += i
								self.captcha_num = code_all
						# # # 判断打码准确性
						if len(self.captcha_num) != 6:
							self.logger.info(f"打码认证数字失败(*>﹏<*)【{self.captcha_num}】")
							self.callback_msg = f"请求认证第{count + 1}次超时，请重试"
							return self.process_to_verify(count + 1, max_count)
						else:
							# # # 判断是否需要重新打码
							self.logger.info(f"打码图片数字成功(*^__^*)【{self.captcha_num}】")
							if self.process_to_login():
								return True
							else:
								if "enter a valid verification code" not in self.callback_msg:
									return False
								else:
									self.logger.info(f"打码认证返回无效(*>﹏<*)【{self.captcha_num}】")
									self.callback_msg = f"请求认证第{count + 1}次超时，请重试"
									return self.process_to_verify(count + 1, max_count)
			# # # 错误重试。
			self.logger.info(f"请求认证第{count + 1}次超时(*>﹏<*)【verify】")
			self.callback_msg = f"请求认证第{count + 1}次超时，请重试"
			return self.process_to_verify(count + 1, max_count)
	
	def process_to_login(self, count: int = 0, max_count: int = 2) -> bool:
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
			self.RCR.url = "https://agent.lionairthai.com/b2badmin/login.aspx"
			self.RCR.param_data = None
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "*/*",
				"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
				"Host": "agent.lionairthai.com",
				"Origin": "https://agent.lionairthai.com",
				"Referer": "https://agent.lionairthai.com/b2badmin/login.aspx",
				"X-MicrosoftAjax": "Delta=true",
				"X-Requested-With": "XMLHttpRequest"
			})
			# # # 拼接请求参数
			login_rad, temp_list = self.BPR.parse_to_regex('%3b%3bSystem.Web.Extensions.*?"', self.RCR.copy_source)
			login_rad = login_rad.strip('"')
			self.user_hdn, temp_list = self.DPR.parse_to_attributes(
				"value", "css", "#hdnCustomerUserID", self.RCR.copy_source)
			password = self.AFR.decrypt_into_aes(self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.password)
			param_batch = [
				("ucAgentLogin$RadScrMgr", False, "ucAgentLogin$UpdatePanel1|ucAgentLogin$btnLogin"),
				("__LASTFOCUS", True, "#__LASTFOCUS"), ("ucAgentLogin_RadScrMgr_TSM", False, login_rad),
				("__EVENTTARGET", True, "#__EVENTTARGET"), ("__EVENTARGUMENT", True, "#__EVENTARGUMENT"),
				("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
				("__VIEWSTATEENCRYPTED", True, "#__VIEWSTATEENCRYPTED"),
				("__EVENTVALIDATION", True, "#__EVENTVALIDATION"), ("hdnCustomerUserID", False, self.user_hdn),
				("hdnLangCode", True, "#hdnLangCode"),
				("ucAgentLogin$hdfCustomerUserID", True, "#ucAgentLogin_hdfCustomerUserID"),
				("ucAgentLogin$txtUserName", False, self.CPR.username),
				("ucAgentLogin$txtPassword", False, password),
				("ucAgentLogin$rdCapImage$CaptchaTextBox", False, self.captcha_num),
				("ucAgentLogin_rdCapImage_ClientState", True, "#ucAgentLogin_rdCapImage_ClientState"),
				("ucAgentLogin$cssversion", True, "#ucAgentLogin_cssversion"), ("__ASYNCPOST", False, "true"),
				("ucAgentLogin$btnLogin", True, "#ucAgentLogin_btnLogin"),
			]
			self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
			if self.RCR.request_to_post():
				# # # 解析登录后状态，判断是否成功
				error_message, temp_list = self.DPR.parse_to_attributes(
					"text", "css", "#ucAgentLogin_lblMessage", self.RCR.page_source)
				if error_message:
					if "already in Use" in error_message:
						self.logger.info(f"账户已被他人占用(*>﹏<*)【{error_message}】")
						self.callback_msg = "账户已被他人占用"
						return False
					else:
						self.logger.info(f"用户请求登录失败(*>﹏<*)【{error_message}】")
						self.callback_msg = f"用户请求登录失败【{error_message}】"
						return False
				else:
					# # # 获取用户访问状态t=id
					b2b_admin, temp_list = self.BPR.parse_to_regex("B2BAdmin.*?\\|", self.RCR.page_source)
					login_target, temp_list = self.BPR.parse_to_regex("%3d.*", b2b_admin)
					if not login_target or len(login_target) <= 4:
						self.logger.info("匹配用户状态失败(*>﹏<*)【login】")
						self.callback_msg = "匹配用户状态失败"
						return self.process_to_login(count + 1, max_count)
					else:
						self.login_target = login_target[3:-1]
						# # # 爬取登录后控制面板页
						self.RCR.url = "https://agent.lionairthai.com/B2BAdmin/DashBoard.aspx"
						self.RCR.param_data = (("t", self.login_target),)
						self.RCR.header = self.BFR.format_to_same(self.init_header)
						self.RCR.header.update({
							"Host": "agent.lionairthai.com",
							"Referer": "https://agent.lionairthai.com/b2badmin/login.aspx",
							"Upgrade-Insecure-Requests": "1"
						})
						if self.RCR.request_to_get(is_redirect=True):
							self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
							return True
			# # # 错误重试。
			self.logger.info(f"请求登录第{count + 1}次超时(*>﹏<*)【login】")
			self.callback_msg = f"请求登录第{count + 1}次超时，请重试"
			return self.process_to_login(count + 1, max_count)
	
	def process_to_logout(self, count: int = 0, max_count: int = 2) -> bool:
		"""Logout process. 退出过程。

		Args:
			count (int): 累计计数。
			max_count (int): 最大计数。

		Returns:
			bool
		"""
		if count >= max_count:
			return False
		else:
			# # # 解析登录，认证
			if not self.process_to_verify():
				return False
			else:
				# # # 解析退出页面
				self.RCR.url = "https://agent.lionairthai.com/B2BAdmin/DashBoard.aspx"
				self.RCR.param_data = (("t", self.login_target),)
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Content-Type": "application/x-www-form-urlencoded",
					"Host": "agent.lionairthai.com",
					"Origin": "https://agent.lionairthai.com",
					"Referer": f"https://agent.lionairthai.com/B2BAdmin/DashBoard.aspx?t={self.login_target}"
				})
				# # # 拼接参数，解析退出
				logout_rad, temp_list = self.BPR.parse_to_regex(
					'%3b%3bSystem.Web.Extensions.*?"', self.RCR.copy_source)
				logout_rad = logout_rad.strip('"')
				param_batch = [
					("RadScriptManager1_TSM", False, logout_rad),
					("__EVENTTARGET", False, "ctl00$btnLogout"),
					("__EVENTARGUMENT", True, "#__EVENTARGUMENT"),
					("__VIEWSTATE", True, "#__VIEWSTATE"),
					("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
					("__VIEWSTATEENCRYPTED", True, "#__VIEWSTATEENCRYPTED"),
					("ctl00$bodycontent$txtSearch", False, ""),
					("ctl00$bodycontent$hdnphSearch", False, "Search+Here..."),
					("ctl00$bodycontent$hdnPopupShown", False, "True"),
				]
				# # # 拼接每个页面具体的参数id
				mnu_id, mnu_list = self.DPR.parse_to_attributes(
					"id", "css", "input[id*=lstmenudisplay_mnuId]", self.RCR.copy_source)
				if mnu_list:
					for i in range(len(mnu_list)):
						param_batch.extend([
							(f"ctl00$lstmenudisplay$ctrl{i}$mnuId", True, f"#lstmenudisplay_mnuId_{i}"),
							(f"ctl00$lstmenudisplay$ctrl{i}$hdfPageName", True, f"#lstmenudisplay_hdfPageName_{i}"),
						])
				self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
				if self.RCR.request_to_post(status_code=302):
					# # # 爬取退出后页面确认状态
					self.RCR.url = "https://agent.lionairthai.com/B2BAdmin/DashBoard.aspx"
					self.RCR.param_data = (("t", self.login_target),)
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Host": "agent.lionairthai.com",
						"Origin": "https://agent.lionairthai.com",
						"Referer": f"https://agent.lionairthai.com/B2BAdmin/DashBoard.aspx?t={self.login_target}"
					})
					if self.RCR.request_to_get(status_code=302):
						return True
			# # # 错误重试。
			self.logger.info(f"请求退出第{count + 1}次超时(*>﹏<*)【logout】")
			self.callback_msg = f"请求退出第{count + 1}次超时，请重试"
			return self.process_to_logout(count + 1, max_count)
	
	def process_to_detail(self, count: int = 0, max_count: int = 1) -> bool:
		"""Detail process. 细节过程。

		Returns:
			bool
		"""
		if count >= max_count:
			return False
		else:
			# # # 请求列表页面。
			self.RCR.url = "https://agent.lionairthai.com/B2BAdmin/TicketingQueue.aspx"
			self.RCR.param_data = (("t", self.login_target),)
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Host": "agent.lionairthai.com",
				"Referer": f"https://agent.lionairthai.com/B2BAdmin/DashBoard.aspx?t={self.login_target}",
				"Upgrade-Insecure-Requests": "1"
			})
			if self.RCR.request_to_get():
				# # # 请求具体某个订单。
				self.RCR.url = "https://agent.lionairthai.com/B2BAdmin/TicketingQueue.aspx"
				self.RCR.param_data = (("t", self.login_target),)
				self.RCR.header = self.BFR.format_to_same(self.init_header)
				self.RCR.header.update({
					"Accept": "*/*",
					"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
					"Host": "agent.lionairthai.com",
					"Origin": "https://agent.lionairthai.com",
					"X-MicrosoftAjax": "delta=true",
					"X-Requested-With": "XMLHttpRequest",
					"Referer": f"https://agent.lionairthai.com/B2BAdmin/TicketingQueue.aspx?t={self.login_target}"
				})
				# # # 拼接请求参数。
				to_date = self.DFR.format_to_now()
				to_single = f"{to_date.year},{to_date.month},{to_date.day}"
				search_rad, temp_list = self.BPR.parse_to_regex(
					'%3b%3bSystem.Web.Extensions.*?"', self.RCR.page_source)
				search_rad = search_rad.strip('"')
				param_batch = [
					("ctl00$RadScriptManager1", False,
					 "ctl00$bodycontent$upRequest|ctl00$bodycontent$RGUserList$ctl00$ctl08$lnkBtnEdit"),
					("RadScriptManager1_TSM", False, search_rad),
					("__EVENTTARGET", True, "#__EVENTTARGET"), ("__EVENTARGUMENT", True, "#__EVENTARGUMENT"),
					("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
					("__VIEWSTATEENCRYPTED", True, "#__VIEWSTATEENCRYPTED"),
					("__EVENTVALIDATION", True, "#__EVENTVALIDATION"),
					("ctl00$bodycontent$txtReservationID", False, self.record),
					("ctl00$bodycontent$txtPaxName", False, ""),
					("ctl00$bodycontent$dpReservationFrom", True, "#ctl00_bodycontent_dpReservationFrom"),
					("ctl00$bodycontent$dpReservationFrom$dateInput", True,
					 "#ctl00_bodycontent_dpReservationFrom_dateInput"),
					("ctl00_bodycontent_dpReservationFrom_dateInput_ClientState", False,
					 '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"",'
					 '"minDateStr":"1980-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":""}'
					 ),
					("ctl00_bodycontent_dpReservationFrom_calendar_SD", False, "[]"),
					("ctl00_bodycontent_dpReservationFrom_calendar_AD", False,
					 f"[[1980,1,1],[2099,12,30],[{to_single}]]"),
					("ctl00_bodycontent_dpReservationFrom_ClientState", True,
					 "#ctl00_bodycontent_dpReservationFrom_ClientState"),
					("ctl00$bodycontent$RGUserList$ctl00$ctl02$ctl02$FilterTextBox_ReservationID",
					 True, "#ctl00_bodycontent_RGUserList_ctl00_ctl02_ctl02_FilterTextBox_ReservationID"),
					("ctl00$bodycontent$RGUserList$ctl00$ctl02$ctl02$FilterTextBox_PNRNo",
					 True, "#ctl00_bodycontent_RGUserList_ctl00_ctl02_ctl02_FilterTextBox_PNRNo"),
					("ctl00$bodycontent$RGUserList$ctl00$ctl02$ctl02$FilterTextBox_PassengerName",
					 True, "#ctl00_bodycontent_RGUserList_ctl00_ctl02_ctl02_FilterTextBox_PassengerName"),
					("ctl00$bodycontent$RGUserList$ctl00$ctl02$ctl02$RDIPFTicketingDeadline",
					 True, "#ctl00_bodycontent_RGUserList_ctl00_ctl02_ctl02_RDIPFTicketingDeadline"),
					("ctl00$bodycontent$RGUserList$ctl00$ctl02$ctl02$RDIPFTicketingDeadline$dateInput",
					 True, "#ctl00_bodycontent_RGUserList_ctl00_ctl02_ctl02_RDIPFTicketingDeadline_dateInput"),
					("ctl00_bodycontent_RGUserList_ctl00_ctl02_ctl02_RDIPFTicketingDeadline_dateInput_ClientState",
					 False,
					 '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"",'
					 '"minDateStr":"1900-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":""}'),
					("ctl00_bodycontent_RGUserList_ctl00_ctl02_ctl02_RDIPFTicketingDeadline_ClientState", False,
					 '{"minDateStr":"1900-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00"}'),
					("ctl00_bodycontent_RGUserList_rfltMenu_ClientState", True,
					 "#ctl00_bodycontent_RGUserList_rfltMenu_ClientState"),
					("ctl00_bodycontent_RGUserList_gdtcSharedCalendar_SD", False, "[]"),
					("ctl00_bodycontent_RGUserList_gdtcSharedCalendar_AD", False,
					 f'[[1900,1,1],[2099,12,31],[{to_single}]]'),
					("ctl00_bodycontent_RGUserList_ClientState", True, "#ctl00_bodycontent_RGUserList_ClientState"),
					("__ASYNCPOST", False, "true"), ("ctl00$bodycontent$btnSearch", False, "Search"),
				]
				# # # 拼接每个页面具体的参数id。
				mnu_id, mnu_list = self.DPR.parse_to_attributes(
					"id", "css", "input[id*=lstmenudisplay_mnuId]", self.RCR.page_source)
				if mnu_list:
					for i in range(len(mnu_list)):
						param_batch.extend([
							(f"ctl00$lstmenudisplay$ctrl{i}$mnuId", True, f"#lstmenudisplay_mnuId_{i}"),
							(f"ctl00$lstmenudisplay$ctrl{i}$hdfPageName", True, f"#lstmenudisplay_hdfPageName_{i}"),
						])
				self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.page_source)
				if self.RCR.request_to_post():
					# # # 查询错误信息
					error_message, temp_list = self.DPR.parse_to_attributes(
						"text", "css", "#bodycontent_lblErrorMsgs", self.RCR.page_source)
					if error_message:
						self.logger.info(error_message)
						self.callback_msg = error_message
						return False
					# # # 查询订单具体sid
					self.sid, temp_list = self.DPR.parse_to_attributes(
						"text", "css", "#ctl00_bodycontent_RGUserList_ctl00__0 td:first-child", self.RCR.page_source)
					if not self.sid:
						self.logger.info(f"查询不到具体订单(*>﹏<*)【{self.record}】")
						self.callback_msg = f"查询不到具体订单。【{self.record}】"
						return False
					# # # 请求详细页面。
					self.RCR.url = "https://agent.lionairthai.com/B2BAdmin/TicketingQueueDetails.aspx"
					self.RCR.param_data = (("sid", self.sid), ("t", self.login_target),)
					self.RCR.header = self.BFR.format_to_same(self.init_header)
					self.RCR.header.update({
						"Host": "agent.lionairthai.com",
						"Referer": f"https://agent.lionairthai.com/B2BAdmin/TicketingQueue.aspx?t={self.login_target}",
						"Upgrade-Insecure-Requests": "1"
					})
					if self.RCR.request_to_get():
						# # #
						self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
						# # #
						self.CPR.currency, temp_list = self.DPR.parse_to_attributes(
							"value", "css", "#bodycontent_hdfSellCurrency", self.RCR.page_source)
						self.CPR.currency = self.BPR.parse_to_clear(self.CPR.currency)
						self.total_price, temp_list = self.DPR.parse_to_attributes(
							"value", "css", "#bodycontent_hdfNetAmount", self.RCR.page_source)
						self.total_price = self.BFR.format_to_float(2, self.total_price)
						# # # 比价格是否要继续支付。
						if self.process_to_compare(max_count=self.retry_count):
							return True
						else:
							return False
			# # # 错误重试。
			self.logger.info(f"请求查询第{count + 1}次超时(*>﹏<*)【detail】")
			self.callback_msg = f"请求查询第{count + 1}次超时，请重试"
			return self.process_to_detail(count + 1, max_count)
	
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
		               f"foreignCurrency={self.CPR.currency}&carrier=SL"
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
			# # # 计算最终返回价格，含行李价格。
			self.return_price = self.total_price
			# # #
			self.RCR.url = "https://agent.lionairthai.com/B2BAdmin/TicketingQueueDetails.aspx"
			self.RCR.param_data = (("sid", self.sid), ("t", self.login_target),)
			self.RCR.header = self.BFR.format_to_same(self.init_header)
			self.RCR.header.update({
				"Accept": "*/*",
				"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
				"Host": "agent.lionairthai.com",
				"Origin": "https://agent.lionairthai.com",
				"X-MicrosoftAjax": "delta=true",
				"X-Requested-With": "XMLHttpRequest",
				"Referer": f"https://agent.lionairthai.com/B2BAdmin/TicketingQueue.aspx?t={self.login_target}",
			})
			# # # 拼接请求参数。
			pay_rad, temp_list = self.BPR.parse_to_regex(
				'%3b%3bSystem.Web.Extensions.*?"', self.RCR.copy_source)
			pay_rad = pay_rad.strip('"')
			param_batch = [
				("ctl00$RadScriptManager1", False,
				 "ctl00$bodycontent$upRequest|ctl00$bodycontent$btnTicketNow"),
				("RadScriptManager1_TSM", False, pay_rad),
				("__EVENTTARGET", True, "#__EVENTTARGET"), ("__EVENTARGUMENT", True, "#__EVENTARGUMENT"),
				("__VIEWSTATE", True, "#__VIEWSTATE"), ("__VIEWSTATEGENERATOR", True, "#__VIEWSTATEGENERATOR"),
				("__VIEWSTATEENCRYPTED", True, "#__VIEWSTATEENCRYPTED"),
				("__EVENTVALIDATION", True, "#__EVENTVALIDATION"),
				("ctl00$bodycontent$hdfSellCurrency", True, "#bodycontent_hdfSellCurrency"),
				("ctl00$bodycontent$hdfNetAmount", True, "#bodycontent_hdfNetAmount"),
				("ctl00$bodycontent$hdfIsCallCenter", True, "#bodycontent_hdfIsCallCenter"),
				("ctl00$bodycontent$hdnIsPostpaid", True, "#bodycontent_hdnIsPostpaid"),
				("ctl00$bodycontent$hdnIsFromMB", True, "#bodycontent_hdnIsFromMB"),
				("ctl00_bodycontent_RGPassengerDetails_ClientState", True,
				 "#ctl00_bodycontent_RGPassengerDetails_ClientState"),
				("ctl00_bodycontent_RGFlightDetails_ClientState", True,
				 "#ctl00_bodycontent_RGFlightDetails_ClientState"),
				("ctl00_bodycontent_RGAddonBaggage_ClientState", True,
				 "#ctl00_bodycontent_RGAddonBaggage_ClientState"),
				("ctl00_bodycontent_RGFareDetails_ClientState",
				 True, "#ctl00_bodycontent_RGFareDetails_ClientState"),
				("__ASYNCPOST", False, "true"), ("ctl00$bodycontent$btnTicketNow", False, "Ticket Now"),
			]
			# # # 拼接每个页面具体的参数id。
			mnu_id, mnu_list = self.DPR.parse_to_attributes(
				"id", "css", "input[id*=lstmenudisplay_mnuId]", self.RCR.copy_source)
			if mnu_list:
				for i in range(len(mnu_list)):
					param_batch.extend([
						(f"ctl00$lstmenudisplay$ctrl{i}$mnuId", True, f"#lstmenudisplay_mnuId_{i}"),
						(f"ctl00$lstmenudisplay$ctrl{i}$hdfPageName", True, f"#lstmenudisplay_hdfPageName_{i}"),
					])
			self.RCR.post_data = self.DPR.parse_to_batch("value", "css", param_batch, self.RCR.copy_source)
			if self.RCR.request_to_post():
				self.logger.info(self.RCR.page_source)
				if "updatePanel|bodycontent_upRequest" not in self.RCR.page_source:
					self.logger.info(f"支付页面跳转失败(*>﹏<*)【payment】")
					self.callback_msg = f"请求账号支付失败。"
					self.callback_data["orderIdentification"] = 2
					return False
				if "E-Ticket is generated for this PNR No" not in self.RCR.page_source:
					self.logger.info(f"更新支付票号失败(*>﹏<*)【payment】")
					self.callback_msg = f"请求账号支付失败。"
					self.callback_data["orderIdentification"] = 2
					return False
				
				return True
			# # # 错误重试。
			self.logger.info(f"请求支付第{count + 1}次超时(*>﹏<*)【payment】")
			self.callback_msg = f"请求支付第{count + 1}次超时，请重试。"
			self.callback_data["orderIdentification"] = 2
			return self.process_to_payment(count + 1, max_count)
	
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

