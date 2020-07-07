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
from pyppeteer import launcher
from pyppeteer import launch

launcher.AUTOMATION_ARGS.remove("--enable-automation")
import os


class PpeteerCrawler:
	"""ppeteer爬行器，爬行器用于交互数据。"""
	
	def __init__(self):
		self.logger: any = None  # 日志记录器。
		self.browser = None  # 谷歌技能。
		self.page = None  # 浏览器驱动。
	
	async def set_to_chrome(self, headless: bool = True) -> bool:
		"""Set to Chrome. 启动谷歌。

		Args:
			headless (bool): Whether to set headless mode. 是否设置无头模式。

		Returns:
			bool
		"""
		try:
			self.browser = await launch({
				"ignoreHTTPSErrors": True, 'headless': headless, 'autoClose': False, 'dumpio': True,
				'args': [
					# '--proxy-server=http://122.94.44.245:3138'
					'--disable-dev-tools',
					# '--disable-gpu',
					'--disable-infobars',
					'--allow-running-insecure-content',
					'--disable-crash-reporter',
					# '--incognito',
				
				]
			})
			self.page = await self.browser.newPage()
			# await self.page.authenticate({
			# 	'username': 'yunku',
			# 	'password': '123',
			# })
			
			await self.page.setUserAgent(
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
				"(KHTML, like Gecko) Chrome/79.0.3494.0 Safari/537.36"
			)
			
			await self.page.setViewport({'width': 1366, 'height': 768})
		except Exception as ex:
			self.logger.info(f"启动无头未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	def set_to_timeout(self, timeout: int = 20) -> bool:
		"""Set to timeout. 设置超时时间。

		Args:
			timeout (int): The timeout of network. 交互超时时间。

		Returns:
			bool
		"""
		try:
			self.page.setDefaultNavigationTimeout(1000 * timeout)
		except Exception as ex:
			self.logger.info(f"回车元素未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	async def set_to_intercept(self, is_intercept: bool) -> bool:
		"""Set to intercept. 设置是否拦截。

		Args:
			is_intercept (bool): Whether to set intercept. 是否拦截。
			
		Returns:
			bool
		"""
		try:
			await self.page.setRequestInterception(is_intercept)
		except Exception as ex:
			self.logger.info(f"设置拦截未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	async def set_to_url(self, source_url: str = "") -> bool:
		"""Whether the page was opened successfully. 打开网页是否成功。

		Args:
			source_url (str): The source url. 来源地址。

		Returns:
			bool
		"""
		try:
			await self.page.goto(source_url)
		except Exception as ex:
			self.logger.info(f"打开网页未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	async def set_to_quit(self) -> bool:
		"""Set to quit. 设置退出。

		Returns:
			bool
		"""
		try:
			await self.browser.close()
		except Exception as ex:
			self.logger.info(f"关闭无头未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	async def set_to_close(self) -> bool:
		"""Set to close tab. 设置关闭窗口。

		Returns:
			bool
		"""
		try:
			await self.page.close()
		except Exception as ex:
			self.logger.info(f"关闭窗口未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	async def set_to_refresh(self) -> bool:
		"""Set to refresh. 设置刷新页面。

		Returns:
			bool
		"""
		pass
	
	async def set_to_script(self, source_js: str = "") -> bool:
		"""Set to javascript. 设置js脚本。

		Args:
			source_js (str): The source js. 来源脚本。

		Returns:
			bool
		"""
		pass
	
	async def set_to_delete(self) -> bool:
		"""Set to delete cookies. 设置删除缓存。

		Returns:
			bool
		"""
		try:
			await self.page.deleteCookie()
		except Exception as ex:
			self.logger.info(f"删除缓存未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	async def set_to_cookies(self, cookie_list: list = None) -> bool:
		"""Set user cookies. 设置用户缓存。

		Args:
			cookie_list (list): Cookies list(name/value/domain/path). 缓存字典。

		Returns:
			bool
		"""
		pass
	
	async def get_to_cookies(self) -> list:
		"""Get to cookies. 获取缓存。

		Returns:
			list
		"""
		try:
			cookies = await self.page.cookies()
		except Exception as ex:
			self.logger.info(f"获取缓存未知失败(*>﹏<*)【{ex}】")
			return []
		else:
			return cookies
	
	async def get_to_page(self) -> str:
		"""Get to the page source. 获取源代码。

		Returns:
			str
		"""
		pass
	
	async def get_to_tab(self) -> str:
		"""Get to tab. 获取窗口ID。

		Returns:
			str
		"""
		pass
	
	async def get_to_windows(self) -> list:
		"""Get to windows. 获取窗口ID列表。

		Returns:
			list
		"""
		pass
	
	async def set_to_switch(self, source_window: str = "") -> bool:
		"""Switch to the window. 切换窗口。

		Args:
			source_window (str): The source window. 来源窗口ID。

		Returns:
			bool
		"""
		pass
	
	async def set_to_new(self, *windows) -> bool:
		"""Switch to the new window. 切换到新打开窗口。

		Args:
			*windows (str): The multi windows. 窗口ID，可多个参数。

		Returns:
			bool
		"""
		pass
	
	async def set_to_equal(self, source_url: str = "", timeout: float = 1) -> bool:
		"""Whether it is equal to the address. 是否等于地址。

		Args:
			source_url (str): The source url. 来源地址。
			timeout (float): Timeout. 超时时间。

		Returns:
			bool
		"""
		pass
	
	async def set_to_find(self, syntax: str = "", timeout: float = 1) -> bool:
		"""Find the element. 发现元素。

		Args:
			syntax (str): The css syntax. 语法。
			timeout (float): Timeout. 超时时间。

		Returns:
			bool
		"""
		pass
	
	async def set_to_wait(self, syntax: str = "", timeout: float = 1) -> bool:
		"""Wait the element. 等待元素。

		Args:
			syntax (str): The css syntax. 语法。
			timeout (float): Timeout. 超时时间。

		Returns:
			bool
		"""
		pass
	
	async def set_to_touch(self, syntax: str = "", timeout: float = 1) -> bool:
		"""Touch the element. 触碰元素。

		Args:
			syntax (str): The css syntax. 语法。
			timeout (float): Timeout. 超时时间。

		Returns:
			bool
		"""
		pass
	
	async def set_to_inside(self, source_text: str = "", syntax: str = "", timeout: float = 1) -> bool:
		"""Touch the element. 包含文本。

		Args:
			source_text (str): The source text. 来源文本数据。
			syntax (str): The css syntax. 语法。
			timeout (float): Timeout. 超时时间。

		Returns:
			bool
		"""
		pass
	
	async def set_to_text(self, syntax: str = "", source_text: str = "") -> bool:
		"""Set to text. 设置文本。

		Args:
			syntax (str): The css syntax. 语法。
			source_text (str): The source text. 来源文本数据。

		Returns:
			bool
		"""
		try:
			await self.page.type(syntax, source_text, {"delay": 1000 * 0.1})
		except Exception as ex:
			self.logger.info(f"设置文本未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	async def get_to_text(self, syntax: str = "") -> str:
		"""Set to text. 获取文本。

		Args:
			syntax (str): The css syntax. 语法。

		Returns:
			bool
		"""
		pass
	
	async def get_to_attrib(self, syntax: str = "", attr_value: str = "") -> str:
		"""Set to text. 获取属性。

		Args:
			syntax (str): The css syntax. 语法。
			attr_value (str): The attribute value. 属性值。

		Returns:
			str
		"""
		pass
	
	async def set_to_click(self, syntax: str = "") -> bool:
		"""Set to click. 点击元素。

		Args:
			syntax (str): The css syntax. 语法。

		Returns:
			bool
		"""
		try:
			await self.page.click(syntax)
		# self.page.mouse  # 模拟真实点击
		except Exception as ex:
			self.logger.info(f"点击元素未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	async def set_to_select(self, syntax: str = "", source_value: str = "") -> bool:
		"""Set to select the value. 下拉元素。

		Args:
			syntax (str): The css syntax. 语法。
			source_value (str): The source value. 来源数据。

		Returns:
			bool
		"""
		pass
	
	async def get_to_alert(self, timeout: float = 1) -> bool:
		"""Get to alert. 获取弹框。

		Args:
			timeout (float): Timeout. 超时时间。

		Returns:
			bool
		"""
		pass
	
	async def set_to_alert(self) -> bool:
		"""Set to alert. 确认弹框。

		Returns:
			bool
		"""
		pass
	
	async def set_to_enter(self, syntax: str = "") -> bool:
		"""Set to enter. 回车元素。

		Args:
			syntax (str): The css syntax. 语法。

		Returns:
			bool
		"""
		try:
			await self.page.keyboard.press("Enter", {"delay": 1000 * 0.1})
		except Exception as ex:
			self.logger.info(f"回车元素未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			return True
	
	def set_to_command(self, source_command: str = "") -> bool:
		"""Set to execute the command. 执行命令。

		Args:
			source_command (str): The source command. 来源命令。

		Returns:
			bool
		"""
		try:
			code = os.system(source_command)
		except Exception as ex:
			self.logger.info(f"执行命令未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			if code:
				self.logger.info(f"执行脚本程序失败(*>﹏<*)【{code}】")
				return False
			else:
				return True
	
	def set_to_proxy(self, proxy_server: str = "", proxy_auth: str = "") -> bool:
		"""Set to proxy. 设置代理。

		Args:
			proxy_server (str): The proxy address. 代理地址。列：1.1.1.1:3138。
			proxy_auth (str): The proxy auth. 代理认证。列：yunku:123。

		Returns:
			bool
		"""
		if proxy_server and proxy_auth:
			# self.set_to_command("./kill_proxy.sh")
			# self.set_to_command(f'mitmdump -q -p 9000 --mode upstream:{proxy_server} '
			#                     f'--set upstream_auth={proxy_auth} > /dev/null 2>&1 &')
			self.set_to_command("kill_proxy.bat")
			self.set_to_command(f'start /b mitmdump -p 9000 --mode upstream:{proxy_server}'
			                    f' --set upstream_auth={proxy_auth}')
			return True
		else:
			# self.set_to_command("./kill_proxy.sh")
			self.set_to_command("kill_proxy.bat")
			return False
