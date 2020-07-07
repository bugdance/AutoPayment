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
"""The crawler is use for crawl structure data."""
from requests import session
from requests.utils import dict_from_cookiejar
from requests_toolbelt import MultipartEncoder
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
import random

# # # Eliminate ssl alarm. 消除 ssl 报警。
disable_warnings(InsecureRequestWarning)


class RequestCrawler:
	"""request爬行器，爬行器用于交互数据。"""
	
	def __init__(self):
		self.logger: any = None  # 日志记录器。
		self.session: any = None  # 全局会话。
		self.url: str = ""  # 请求地址。
		self.header: dict = {}  # 请求头。
		self.param_data: tuple = ()  # 链接参数数据。
		self.post_data: list = []  # 请求主体数据。
		self.timeout: int = 25  # 请求超时时间。
		self.page_source: any = None  # 返回源页面数据。
		self.copy_source: any = None  # 镜像页面数据。
		self.response_url: str = ""  # 响应地址。
	
	def set_to_session(self) -> bool:
		"""Set to session. 设置为会话。

		Returns:
			bool
		"""
		# # # Start session. 启动会话。
		self.session = session()
		self.session.max_redirects = 3
		
		return True
	
	def set_to_proxy(self, enable_proxy: bool = False, address: str = "") -> bool:
		"""Set to session. 设置为代理。

		Args:
			enable_proxy (bool): Whether to use a proxy. 是否使用代理。
			address (str): Proxy address(http://1.1.1.1:22443 or http://yunku:123@1.1.1.1:3138). 代理地址。

		Returns:
			bool
		"""
		if type(enable_proxy) is not bool or type(address) is not str:
			self.logger.info(f"设置代理参数有误(*>﹏<*)【{enable_proxy}】【{address}】")
			return False
		# # # Determine whether to use a proxy. 判断是否使用代理。
		if enable_proxy:
			self.session.proxies = {"https": address, "http": address}
		else:
			self.session.proxies = {}
		
		self.logger.info(f"设置会话代理成功(*^__^*)【{enable_proxy}】【{address}】")
		return True
	
	def set_to_cookies(self, include_domain: bool = True, cookie_list: list = None) -> bool:
		"""Set user cookies. 设置用户缓存。

		Args:
			include_domain (bool): Whether to include a domain name. 是否包含域名。
			cookie_list (list): Cookies list(name/value/domain/path). 缓存字典。

		Returns:
			bool
		"""
		try:
			if include_domain:
				for i in cookie_list:
					cookie_name = i.get('name')
					cookie_value = i.get('value')
					cookie_domain = i.get('domain')
					cookie_path = i.get('path')
					self.session.cookies.set(
						name=cookie_name, value=cookie_value, domain=cookie_domain, path=cookie_path)
			else:
				for i in cookie_list:
					cookie_name = i.get('name')
					cookie_value = i.get('value')
					self.session.cookies.set(name=cookie_name, value=cookie_value)
		except Exception as ex:
			self.logger.info(f"设置缓存程序失败(*>﹏<*)【{include_domain}】")
			self.logger.info(f"设置缓存失败原因(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	def set_to_multi(self, source_dict: dict = None, separator: any = None, multi_encoding: str = "utf-8") -> any:
		"""Set to multipart encoder. 设置为多部分编码器。

		Args:
			source_dict (dict): The source dict. 来源字典。
			separator (any): Specifying a separator. 指定分隔符（还未知什么类型）。
			multi_encoding (str): Encoding of multipart data(utf-8/iso-8859-1). 多部分数据的编码。

		Returns:
			any: Multipart encoder class or None.
		"""
		if type(source_dict) is not dict:
			self.logger.info(f"多部分码参数有误(*>﹏<*)【{separator}】")
			return None
		
		try:
			multipart = MultipartEncoder(fields=source_dict, boundary=separator, encoding=multi_encoding)
		except Exception as ex:
			self.logger.info(f"设置多部分码失败(*>﹏<*)【{separator}】")
			self.logger.info(f"设置多部失败原因(*>﹏<*)【{ex}】")
			return None
		else:
			return multipart
	
	def get_from_cookies(self) -> dict:
		"""Get session cookies. 获取缓存。

		Returns:
			dict
		"""
		return dict_from_cookiejar(self.session.cookies)
	
	def request_to_options(
			self, page_type: str = "text", status_code: int = 200,
			is_redirect: bool = False, page_encoding: str = "utf-8") -> bool:
		"""Options type request. Options类型请求。

		Args:
			page_type (str): Specifying the response data type(text/content/json). 指定响应数据类型。
			status_code (int): Specify response encoding(200/302). 指定响应编码。
			is_redirect (bool): Whether to jump. 指定响应是否跳转。
			page_encoding (str): Encoding of response page data(utf-8/iso-8859-1). 响应页面数据的编码。

		Returns:
			bool
		"""
		try:
			response = self.session.options(
				url=self.url, headers=self.header, params=self.param_data,
				allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			response.encoding = page_encoding
		except Exception as ex:
			self.logger.info(f"请求超时或者失败(*>﹏<*)【OPTIONS】【{self.url}】")
			self.logger.info(f"超时或者失败原因(*>﹏<*)【{ex}】")
			return False
		else:
			if self.response_to_page(page_type, status_code, response):
				return True
			else:
				return False
	
	def request_to_get(
			self, page_type: str = "text", status_code: int = 200,
			is_redirect: bool = False, page_encoding: str = "utf-8") -> bool:
		"""Get type request. Get类型请求。

		Args:
			page_type (str): Specifying the response data type(text/content/json). 指定响应数据类型。
			status_code (int): Specify response encoding(200/302). 指定响应编码。
			is_redirect (bool): Whether to jump. 指定响应是否跳转。
			page_encoding (str): Encoding of response page data(utf-8/iso-8859-1). 响应页面数据的编码。

		Returns:
			bool
		"""
		try:
			response = self.session.get(
				url=self.url, headers=self.header, params=self.param_data,
				allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			response.encoding = page_encoding
		except Exception as ex:
			self.logger.info(f"请求超时或者失败(*>﹏<*)【GET】【{self.url}】")
			self.logger.info(f"超时或者失败原因(*>﹏<*)【{ex}】")
			return False
		else:
			if self.response_to_page(page_type, status_code, response):
				return True
			else:
				return False
	
	def request_to_post(
			self, data_type: str = "data", page_type: str = "text", status_code: int = 200,
			is_redirect: bool = False, page_encoding: str = "utf-8") -> bool:
		"""Post type request. Post类型请求。

		Args:
			data_type (str): Specifying the request data type(text/content/json). 指定请求数据类型。
			page_type (str): Specifying the response data type(text/content/json). 指定响应数据类型。
			status_code (int): Specify response encoding(200/302). 指定响应编码。
			is_redirect (bool): Whether to jump. 指定响应是否跳转。
			page_encoding (str): Encoding of response page data(utf-8/iso-8859-1). 响应页面数据的编码。

		Returns:
			bool
		"""
		try:
			if data_type == "data":
				response = self.session.post(
					url=self.url, headers=self.header, params=self.param_data,
					data=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			elif data_type == "json":
				response = self.session.post(
					url=self.url, headers=self.header, params=self.param_data,
					json=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			elif data_type == "files":
				response = self.session.post(
					url=self.url, headers=self.header, params=self.param_data,
					files=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			else:
				self.logger.info(f"请求类型参数有误(*>﹏<*)【{data_type}】【{self.url}】")
				return False
			response.encoding = page_encoding
		except Exception as ex:
			self.logger.info(f"请求超时或者失败(*>﹏<*)【POST】【{self.url}】")
			self.logger.info(f"超时或者失败原因(*>﹏<*)【{ex}】")
			return False
		else:
			if self.response_to_page(page_type, status_code, response):
				return True
			else:
				return False
	
	def request_to_delete(
			self, data_type: str = "data", page_type: str = "text", status_code: int = 200,
			is_redirect: bool = False, page_encoding: str = "utf-8") -> bool:
		"""Delete type request. Delete类型请求。

		Args:
			data_type (str): Specifying the request data type(text/content/json). 指定请求数据类型。
			page_type (str): Specifying the response data type(text/content/json). 指定响应数据类型。
			status_code (int): Specify response encoding(200/302). 指定响应编码。
			is_redirect (bool): Whether to jump. 指定响应是否跳转。
			page_encoding (str): Encoding of response page data(utf-8/iso-8859-1). 响应页面数据的编码。

		Returns:
			bool
		"""
		try:
			if data_type == "data":
				response = self.session.delete(
					url=self.url, headers=self.header, params=self.param_data,
					data=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			elif data_type == "json":
				response = self.session.delete(
					url=self.url, headers=self.header, params=self.param_data,
					json=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			elif data_type == "files":
				response = self.session.delete(
					url=self.url, headers=self.header, params=self.param_data,
					files=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			else:
				self.logger.info(f"请求类型参数有误(*>﹏<*)【{data_type}】【{self.url}】")
				return False
			response.encoding = page_encoding
		except Exception as ex:
			self.logger.info(f"请求超时或者失败(*>﹏<*)【Delete】【{self.url}】")
			self.logger.info(f"超时或者失败原因(*>﹏<*)【{ex}】")
			return False
		else:
			if self.response_to_page(page_type, status_code, response):
				return True
			else:
				return False
	
	def request_to_put(
			self, data_type: str = "data", page_type: str = "text", status_code: int = 200,
			is_redirect: bool = False, page_encoding: str = "utf-8") -> bool:
		"""Put type request. Put类型请求。

		Args:
			data_type (str): Specifying the request data type(text/content/json). 指定请求数据类型。
			page_type (str): Specifying the response data type(text/content/json). 指定响应数据类型。
			status_code (int): Specify response encoding(200/302). 指定响应编码。
			is_redirect (bool): Whether to jump. 指定响应是否跳转。
			page_encoding (str): Encoding of response page data(utf-8/iso-8859-1). 响应页面数据的编码。

		Returns:
			bool
		"""
		try:
			if data_type == "data":
				response = self.session.put(
					url=self.url, headers=self.header, params=self.param_data,
					data=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			elif data_type == "json":
				response = self.session.put(
					url=self.url, headers=self.header, params=self.param_data,
					json=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			elif data_type == "files":
				response = self.session.put(
					url=self.url, headers=self.header, params=self.param_data,
					files=self.post_data, allow_redirects=is_redirect, timeout=self.timeout, verify=False)
			else:
				self.logger.info(f"请求类型参数有误(*>﹏<*)【{data_type}】【{self.url}】")
				return False
			response.encoding = page_encoding
		except Exception as ex:
			self.logger.info(f"请求超时或者失败(*>﹏<*)【PUT】【{self.url}】")
			self.logger.info(f"超时或者失败原因(*>﹏<*)【{ex}】")
			return False
		else:
			if self.response_to_page(page_type, status_code, response):
				return True
			else:
				return False
	
	def response_to_page(self, page_type: str = "text", status_code: int = 200, response: any = None) -> bool:
		"""Specify the response to return data. 指定响应返回数据。

		Args:
			page_type (str): Specifying the response data type(text/content/json). 指定响应数据类型。
			status_code (int): Specify response encoding(200/302). 指定响应编码。
			response (any): Response body. 响应主体。

		Returns:
			bool
		"""
		if status_code != response.status_code:
			self.logger.info(f"返回编码参数有误(*>﹏<*)【{response.status_code}】【{self.url}】")
			self.logger.info(response.text)
		
		try:
			self.response_url = response.url
			if page_type == "content":
				self.page_source = response.content
			elif page_type == "text":
				self.page_source = response.text
			elif page_type == "json":
				self.page_source = response.json()
			else:
				response.close()
				self.logger.info(f"返回类型参数有误(*>﹏<*)【{page_type}】【{self.url}】")
				return False
		except Exception as ex:
			response.close()
			self.logger.info(f"返回页面程序失败(*>﹏<*)【{page_type}】【{self.url}】")
			self.logger.info(f"返回页面失败原因(*>﹏<*)【{ex}】")
			return False
		else:
			response.close()
			self.logger.info(f"返回页面程序成功(*^__^*)【{status_code}】【{self.url}】")
			return True
	
	def build_to_header(self, header_version: str = "Firefox") -> tuple:
		"""Build header, if none to random. 构建请求头（如果没有随机请求头）。

		Args:
			header_version (str): Header version. 请求头版本。

		Returns:
			tuple: Return a user agent/a header dict.
		"""
		# # # Version collection. 版本集合。
		default_version = {
			"Chrome": {
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
				              "(KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
				          "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
				"Accept-Language": "zh-CN,zh;q=0.9"
			},
			"UBrowser": {
				"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
				              "Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36",
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Language": "zh-CN,zh;q=0.8"
			},
			"QQBrowser": {
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
				              "(KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 "
				              "Core/1.70.3704.400 QQBrowser/10.4.3620.400",
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				"Accept-Language": "zh-CN,zh;q=0.9"
			},
			"Firefox": {
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
			},
			"Firefox32": {
				"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
				"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
			},
			"Opera": {
				"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
				              "Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.94",
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
				"Accept-Language": "zh-CN,zh;q=0.9",
			}
		}
		# # # Return header. 返回的请求头。
		return_header = {
			"Accept-Encoding": "gzip, deflate, br",
			"Connection": "keep-alive",
		}
		# # # Judge the request header. 判断请求头。
		if not header_version or type(header_version) is not str:
			header_version = "Firefox"
		version_dict = default_version.get(header_version)
		# # # If the corresponding version cannot be found, random one. 如果找不到对应版本随机一个。
		if version_dict:
			return_agent = version_dict.get("User-Agent")
			return_header.update(version_dict)
		else:
			key = random.sample(default_version.keys(), 1)
			version = key[0]
			version_dict = default_version.get(version)
			return_agent = version_dict.get("User-Agent")
			return_header.update(version_dict)
		# # # Return. 返回。
		self.logger.info(f"构建请求头部成功(*^__^*)【{return_agent}】")
		return return_agent, return_header
