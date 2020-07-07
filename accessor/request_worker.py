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
"""The worker is use for making workflow."""
import logging


class RequestWorker:
	"""request工作器，用于制作工作流。"""
	
	def __init__(self):
		self.logger: any = None  # 日志记录器。
		self.handler: any = None  # 日志处理器。
		self.user_agent: str = ""  # 初始化UA。
		self.init_header: dict = {}  # 初始化请求头。
		self.callback_data: dict = {}  # 回调数据。
		self.callback_msg: str = "出票失败"  # 回调信息。
		self.retry_count: int = 1  # 重试计数。
	
	def init_to_logger(self, task_id: any = None, log_path: str = "") -> bool:
		"""Init to logger. 初始化日志。

		Args:
			task_id (any): Task id. 任务编号。
			log_path (str): Log Path. 日志地址。

		Returns:
			bool
		"""
		self.logger = logging.getLogger(str(task_id))
		self.logger.setLevel(level=logging.INFO)
		formatter = logging.Formatter("[%(asctime)s]%(message)s")
		self.handler = logging.FileHandler(log_path, encoding="utf-8")
		# self.handler = logging.StreamHandler()
		self.handler.setFormatter(formatter)
		self.logger.addHandler(self.handler)
		return True
	
	def init_to_assignment(self) -> bool:
		"""Assignment to logger. 赋值日志。

		Returns:
			bool
		"""
		pass
	
	def process_to_main(self, process_dict: dict = None) -> dict:
		"""Main process. 主程序入口。

		Args:
			process_dict (dict): Parameters. 传参。

		Returns:
			dict
		"""
		pass
	
	def process_to_proxy(self) -> bool:
		"""Proxy process. 代理过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_verify(self) -> bool:
		"""Verify process. 验证过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_login(self) -> bool:
		"""Login process. 登录过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_logout(self) -> bool:
		"""Logout process. 退出过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_index(self) -> bool:
		"""Index process. 首页过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_search(self) -> bool:
		"""Search process. 搜索过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_query(self) -> bool:
		"""Query process. 查询过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_passenger(self) -> bool:
		"""Passenger process. 乘客过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_service(self) -> bool:
		"""Service process. 辅营过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_payment(self) -> bool:
		"""Payment process. 支付过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_record(self) -> bool:
		"""Record process. 订单过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_segment(self) -> bool:
		"""Segment process. 航段过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_detail(self) -> bool:
		"""Detail process. 细节过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_compare(self) -> bool:
		"""Compare process. 对比过程。

		Returns:
			bool
		"""
		pass
	
	def process_to_return(self) -> bool:
		"""Return process. 返回过程。

		Returns:
			bool
		"""
		pass

