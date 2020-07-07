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
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import ReadTimeoutError
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import os


class SeleniumCrawler:
    """selenium爬行器，爬行器用于交互数据。"""
    
    def __init__(self):
        self.logger: any = None  # 日志记录器。
        self.fox_prof = webdriver.FirefoxProfile()  # 火狐配置。
        self.fox_ops = webdriver.FirefoxOptions()  # 火狐选项。
        self.fox_caps = None  # 火狐技能。
        self.chrome_ops = webdriver.ChromeOptions()  # 谷歌选项。
        self.chrome_caps = None  # 谷歌技能。
        self.driver = None  # 浏览器驱动。
    
    def set_to_firefox(self, headless: bool = True) -> bool:
        """Set to Firefox. 启动火狐。
        
        Args:
            headless (bool): Whether to set headless mode. 是否设置无头模式。

        Returns:
            bool
        """
        self.fox_ops.headless = headless
        self.fox_prof.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0")
        # self.fox_ops.add_argument('--proxy-server=http://127.0.0.1:8888')
        self.fox_prof.set_preference('permissions.default.image', 2)
        self.fox_prof.accept_untrusted_certs = True
        self.fox_prof.update_preferences()
        self.fox_caps = self.fox_ops.to_capabilities()
        try:
            self.driver = webdriver.Firefox(
                desired_capabilities=self.fox_caps, firefox_profile=self.fox_prof, options=self.fox_ops)
        except WebDriverException:
            self.logger.info("启动无头框架失败(*>﹏<*)【Firefox】")
            return False
        except ReadTimeoutError:
            self.logger.info("启动无头响应超时(*>﹏<*)【Firefox】")
            return False
        except Exception as ex:
            self.logger.info(f"启动无头未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_chrome(self, headless: bool = True) -> bool:
        """Set to Chrome. 启动谷歌。
        
        Args:
            headless (bool): Whether to set headless mode. 是否设置无头模式。

        Returns:
            bool
        """
        self.chrome_ops.headless = headless
        self.chrome_ops.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                     "(KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36")
        # self.chrome_ops.add_argument('--proxy-server=http://127.0.0.1:8888')
        self.chrome_ops.add_argument('--no-sandbox')  # 无头下禁用沙盒。
        self.chrome_ops.add_argument('--disable-dev-tools')  # 无头下禁用dev。
        self.chrome_ops.add_argument('--disable-gpu')  # 禁用gpu加速。
        self.chrome_ops.add_argument('--disable-infobars')  # 禁用提示。
        self.chrome_ops.add_argument('--ignore-certificate-errors')  # 忽略证书错误。
        self.chrome_ops.add_argument('--allow-running-insecure-content')  # 与上同步使用。
        self.chrome_ops.add_argument('--disable-crash-reporter')  # 禁用汇报。
        # self.chrome_ops.add_argument('--incognito')  # 隐身模式。
        preferences = {'profile.default_content_setting_values':
                           {'images': 2, 'notifications': 2, }}
        self.chrome_ops.add_experimental_option('prefs', preferences)
        self.chrome_ops.add_experimental_option('excludeSwitches', ['enable-automation'])  # 开发者模式。
        self.chrome_ops.add_experimental_option('w3c', False)  # 禁用w3c才能抓包。
        self.chrome_caps = self.chrome_ops.to_capabilities()
        self.chrome_caps['loggingPrefs'] = {'performance': 'ALL'}
        try:
            self.driver = webdriver.Chrome(options=self.chrome_ops, desired_capabilities=self.chrome_caps)
        except WebDriverException:
            self.logger.info("启动无头框架失败(*>﹏<*)【Chrome】")
            return False
        except ReadTimeoutError:
            self.logger.info("启动无头响应超时(*>﹏<*)【Chrome】")
            return False
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
        self.driver.set_page_load_timeout(timeout)  # 全局页面加载超时。
        self.driver.set_script_timeout(timeout)  # 全局js加载超时。
        return True
    
    def set_to_url(self, source_url: str = "") -> bool:
        """Whether the page was opened successfully. 打开网页是否成功。
        
        Args:
            source_url (str): The source url. 来源地址。

        Returns:
            bool
        """
        try:
            self.driver.get(source_url)
        except WebDriverException:
            self.logger.info(f"打开网页框架失败(*>﹏<*)【{source_url}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"打开网页响应超时(*>﹏<*)【{source_url}】")
            return False
        except Exception as ex:
            self.logger.info(f"打开网页未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_quit(self) -> bool:
        """Set to quit. 设置退出。
        
        Returns:
            bool
        """
        try:
            self.driver.quit()
        except WebDriverException:
            self.logger.info("关闭无头框架失败(*>﹏<*)【quit】")
            return False
        except ReadTimeoutError:
            self.logger.info("关闭无头响应超时(*>﹏<*)【quit】")
            return False
        except Exception as ex:
            self.logger.info(f"关闭无头未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_close(self) -> bool:
        """Set to close tab. 设置关闭窗口。

        Returns:
            bool
        """
        try:
            self.driver.close()
        except WebDriverException:
            self.logger.info("关闭窗口框架失败(*>﹏<*)【close】")
            return False
        except ReadTimeoutError:
            self.logger.info("关闭窗口响应超时(*>﹏<*)【close】")
            return False
        except Exception as ex:
            self.logger.info(f"关闭窗口未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_refresh(self) -> bool:
        """Set to refresh. 设置刷新页面。

        Returns:
            bool
        """
        try:
            self.driver.refresh()
        except WebDriverException:
            self.logger.info("刷新页面框架失败(*>﹏<*)【refresh】")
            return False
        except ReadTimeoutError:
            self.logger.info("刷新页面响应超时(*>﹏<*)【refresh】")
            return False
        except Exception as ex:
            self.logger.info(f"刷新页面未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_script(self, source_js: str = "") -> bool:
        """Set to javascript. 设置js脚本。
        
        Args:
            source_js (str): The source js. 来源脚本。

        Returns:
            bool
        """
        try:
            self.driver.execute_script(source_js)
        except WebDriverException:
            self.logger.info("执行脚本框架失败(*>﹏<*)【script】")
            return False
        except ReadTimeoutError:
            self.logger.info("执行脚本响应超时(*>﹏<*)【script】")
            return False
        except Exception as ex:
            self.logger.info(f"执行脚本未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_delete(self) -> bool:
        """Set to delete cookies. 设置删除缓存。

        Returns:
            bool
        """
        try:
            self.driver.delete_all_cookies()
        except WebDriverException:
            self.logger.info("删除缓存框架失败(*>﹏<*)【delete】")
            return False
        except ReadTimeoutError:
            self.logger.info("删除缓存响应超时(*>﹏<*)【delete】")
            return False
        except Exception as ex:
            self.logger.info(f"删除缓存未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True

    def set_to_cookies(self, cookie_list: list = None) -> bool:
        """Set user cookies. 设置用户缓存。

        Args:
            cookie_list (list): Cookies list(name/value/domain/path). 缓存字典。

        Returns:
            bool
        """
        try:
            for i in cookie_list:
                cookie_name = i.get('name')
                cookie_value = i.get('value')
                cookie_domain = i.get("domain")
                cookie_path = i.get("path")
                self.driver.add_cookie(
                    {'name': cookie_name, 'value': cookie_value, 'domain': cookie_domain, 'path': cookie_path})
        except WebDriverException:
            self.logger.info("设置缓存框架失败(*>﹏<*)【cookies】")
            return False
        except ReadTimeoutError:
            self.logger.info("设置缓存响应超时(*>﹏<*)【cookies】")
            return False
        except Exception as ex:
            self.logger.info(f"设置缓存未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def get_to_cookies(self) -> list:
        """Get to cookies. 获取缓存。
        
        Returns:
            list
        """
        try:
            cookies = self.driver.get_cookies()
        except WebDriverException:
            self.logger.info("获取缓存框架失败(*>﹏<*)【cookies】")
            return []
        except ReadTimeoutError:
            self.logger.info("获取缓存响应超时(*>﹏<*)【cookies】")
            return []
        except Exception as ex:
            self.logger.info(f"获取缓存未知失败(*>﹏<*)【{ex}】")
            return []
        else:
            return cookies
    
    def get_to_package(self) -> list:
        """Get to package. 获取抓包。

        Returns:
            list
        """
        try:
            log = self.driver.get_log("performance")
        except WebDriverException:
            self.logger.info("获取抓包框架失败(*>﹏<*)【package】")
            return []
        except ReadTimeoutError:
            self.logger.info("获取抓包响应超时(*>﹏<*)【package】")
            return []
        except Exception as ex:
            self.logger.info(f"获取抓包未知失败(*>﹏<*)【{ex}】")
            return []
        else:
            return log
    
    def get_to_page(self) -> str:
        """Get to the page source. 获取源代码。
        
        Returns:
            str
        """
        try:
            page = self.driver.page_source
        except WebDriverException:
            self.logger.info("获取页面框架失败(*>﹏<*)【page】")
            return ""
        except ReadTimeoutError:
            self.logger.info("获取页面响应超时(*>﹏<*)【page】")
            return ""
        except Exception as ex:
            self.logger.info(f"获取页面未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            return page
    
    def get_to_tab(self) -> str:
        """Get to tab. 获取窗口ID。
        
        Returns:
            str
        """
        try:
            window = self.driver.current_window_handle
        except WebDriverException:
            self.logger.info("获取窗口框架失败(*>﹏<*)【tab】")
            return ""
        except ReadTimeoutError:
            self.logger.info("获取窗口响应超时(*>﹏<*)【tab】")
            return ""
        except Exception as ex:
            self.logger.info(f"获取窗口未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            return window

    def get_to_windows(self) -> list:
        """Get to windows. 获取窗口ID列表。

        Returns:
            list
        """
        try:
            handles = self.driver.window_handles
        except WebDriverException:
            self.logger.info("获取窗柄框架失败(*>﹏<*)【windows】")
            return []
        except ReadTimeoutError:
            self.logger.info("获取窗柄响应超时(*>﹏<*)【windows】")
            return []
        except Exception as ex:
            self.logger.info(f"获取窗柄未知失败(*>﹏<*)【{ex}】")
            return []
        else:
            return handles
    
    def set_to_switch(self, source_window: str = "") -> bool:
        """Switch to the window. 切换窗口。
        
        Args:
            source_window (str): The source window. 来源窗口ID。

        Returns:
            bool
        """
        try:
            self.driver.switch_to.window(source_window)
        except WebDriverException:
            self.logger.info("切换窗口框架失败(*>﹏<*)【switch】")
            return False
        except ReadTimeoutError:
            self.logger.info("切换窗口响应超时(*>﹏<*)【switch】")
            return False
        except Exception as ex:
            self.logger.info(f"切换窗口未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_new(self, *windows) -> bool:
        """Switch to the new window. 切换到新打开窗口。
        
        Args:
            *windows (str): The multi windows. 窗口ID，可多个参数。

        Returns:
            bool
        """
        handles = self.get_to_windows()
        if handles:
            for handle in windows:
                handles.remove(handle)
            if len(handles) == 1:
                return self.set_to_switch(handles[0])
            else:
                self.logger.info("没有新打开的窗口(*>﹏<*)【new】")
                return False
        else:
            return False
    
    def set_to_equal(self, source_url: str = "", timeout: float = 1) -> bool:
        """Whether it is equal to the address. 是否等于地址。
        
        Args:
            source_url (str): The source url. 来源地址。
            timeout (float): Timeout. 超时时间。

        Returns:
            bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=timeout, poll_frequency=0.1).until(
                EC.url_to_be(source_url))
        except WebDriverException:
            self.logger.info(f"判断地址框架失败(*>﹏<*)【{source_url}】【{timeout}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"判断地址响应超时(*>﹏<*)【{source_url}】【{timeout}】")
            return False
        except Exception as ex:
            self.logger.info(f"判断地址未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_find(self, syntax: str = "", timeout: float = 1) -> bool:
        """Find the element. 发现元素。
        
        Args:
            syntax (str): The css syntax. 语法。
            timeout (float): Timeout. 超时时间。

        Returns:
            bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=timeout, poll_frequency=0.1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, syntax)))
        except WebDriverException:
            self.logger.info(f"发现元素框架失败(*>﹏<*)【{syntax}】【{timeout}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"发现元素响应超时(*>﹏<*)【{syntax}】【{timeout}】")
            return False
        except Exception as ex:
            self.logger.info(f"发现元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True

    def set_to_wait(self, syntax: str = "", timeout: float = 1) -> bool:
        """Wait the element. 等待元素。

        Args:
            syntax (str): The css syntax. 语法。
            timeout (float): Timeout. 超时时间。

        Returns:
            bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=timeout, poll_frequency=0.1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, syntax)))
        except WebDriverException:
            self.logger.info(f"等待元素框架失败(*>﹏<*)【{syntax}】【{timeout}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"等待元素响应超时(*>﹏<*)【{syntax}】【{timeout}】")
            return False
        except Exception as ex:
            self.logger.info(f"等待元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_touch(self, syntax: str = "", timeout: float = 1) -> bool:
        """Touch the element. 触碰元素。

        Args:
            syntax (str): The css syntax. 语法。
            timeout (float): Timeout. 超时时间。

        Returns:
            bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=timeout, poll_frequency=0.1).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, syntax)))
        except WebDriverException:
            self.logger.info(f"触碰元素框架失败(*>﹏<*)【{syntax}】【{timeout}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"触碰元素响应超时(*>﹏<*)【{syntax}】【{timeout}】")
            return False
        except Exception as ex:
            self.logger.info(f"触碰元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_inside(self, source_text: str = "", syntax: str = "", timeout: float = 1) -> bool:
        """Touch the element. 包含文本。

        Args:
            source_text (str): The source text. 来源文本数据。
            syntax (str): The css syntax. 语法。
            timeout (float): Timeout. 超时时间。

        Returns:
            bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=timeout, poll_frequency=0.1).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, syntax), source_text))
        except WebDriverException:
            self.logger.info(f"包含文本框架失败(*>﹏<*)【{syntax}】【{timeout}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"包含文本响应超时(*>﹏<*)【{syntax}】【{timeout}】")
            return False
        except Exception as ex:
            self.logger.info(f"包含文本未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_text(self, syntax: str = "", source_text: str = "") -> bool:
        """Set to text. 设置文本。

        Args:
            syntax (str): The css syntax. 语法。
            source_text (str): The source text. 来源文本数据。

        Returns:
            bool
        """
        try:
            element = self.driver.find_element_by_css_selector(syntax)
            element.clear()
            element.send_keys(source_text)
        except WebDriverException:
            self.logger.info(f"设置文本框架失败(*>﹏<*)【{syntax}】【{source_text}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"设置文本响应超时(*>﹏<*)【{syntax}】【{source_text}】")
            return False
        except Exception as ex:
            self.logger.info(f"设置文本未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def get_to_text(self, syntax: str = "") -> str:
        """Set to text. 获取文本。

        Args:
            syntax (str): The css syntax. 语法。

        Returns:
            bool
        """
        try:
            element = self.driver.find_element_by_css_selector(syntax)
            css_text = element.text
        except WebDriverException:
            self.logger.info(f"获取文本框架失败(*>﹏<*)【{syntax}】")
            return ""
        except ReadTimeoutError:
            self.logger.info(f"获取文本响应超时(*>﹏<*)【{syntax}】")
            return ""
        except Exception as ex:
            self.logger.info(f"获取文本未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            return css_text
    
    def get_to_attrib(self, syntax: str = "", attr_value: str = "") -> str:
        """Set to text. 获取属性。

        Args:
            syntax (str): The css syntax. 语法。
            attr_value (str): The attribute value. 属性值。

        Returns:
            str
        """
        try:
            element = self.driver.find_element_by_css_selector(syntax)
            value = element.get_attribute(attr_value)
        except WebDriverException:
            self.logger.info(f"获取属性框架失败(*>﹏<*)【{syntax}】")
            return ""
        except ReadTimeoutError:
            self.logger.info(f"获取属性响应超时(*>﹏<*)【{syntax}】")
            return ""
        except Exception as ex:
            self.logger.info(f"获取属性未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            return value
    
    def set_to_click(self, syntax: str = "") -> bool:
        """Set to click. 点击元素。

        Args:
            syntax (str): The css syntax. 语法。

        Returns:
            bool
        """
        try:
            element = self.driver.find_element_by_css_selector(syntax)
            element.click()
        except WebDriverException:
            self.logger.info(f"点击元素框架失败(*>﹏<*)【{syntax}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"点击元素响应超时(*>﹏<*)【{syntax}】")
            return False
        except Exception as ex:
            self.logger.info(f"点击元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_select(self, syntax: str = "", source_value: str = "") -> bool:
        """Set to select the value. 下拉元素。

        Args:
            syntax (str): The css syntax. 语法。
            source_value (str): The source value. 来源数据。

        Returns:
            bool
        """
        try:
            element = self.driver.find_element_by_css_selector(syntax)
            Select(element).select_by_value(source_value)
        except WebDriverException:
            self.logger.info(f"下拉元素框架失败(*>﹏<*)【{syntax}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"下拉元素响应超时(*>﹏<*)【{syntax}】")
            return False
        except Exception as ex:
            self.logger.info(f"下拉元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def get_to_alert(self, timeout: float = 1) -> bool:
        """Get to alert. 获取弹框。
        
        Args:
            timeout (float): Timeout. 超时时间。

        Returns:
            bool
        """
        try:
            WebDriverWait(
                driver=self.driver, timeout=timeout, poll_frequency=0.1).until(EC.alert_is_present())
        except WebDriverException:
            self.logger.info(f"获取弹框框架失败(*>﹏<*)【{timeout}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"获取弹框响应超时(*>﹏<*)【{timeout}】")
            return False
        except Exception as ex:
            self.logger.info(f"获取弹框未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_alert(self) -> bool:
        """Set to alert. 确认弹框。
        
        Returns:
            bool
        """
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except WebDriverException:
            self.logger.info("确认弹框框架失败(*>﹏<*)【alert】")
            return False
        except ReadTimeoutError:
            self.logger.info("确认弹框响应超时(*>﹏<*)【alert】")
            return False
        except Exception as ex:
            self.logger.info(f"确认弹框未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            return True
    
    def set_to_enter(self, syntax: str = "") -> bool:
        """Set to enter. 回车元素。

        Args:
            syntax (str): The css syntax. 语法。

        Returns:
            bool
        """
        try:
            element = self.driver.find_element_by_css_selector(syntax)
            element.send_keys(Keys.ENTER)
        except WebDriverException:
            self.logger.info(f"回车元素框架失败(*>﹏<*)【{syntax}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"回车元素响应超时(*>﹏<*)【{syntax}】")
            return False
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
            self.set_to_command("./kill_proxy.sh")
            self.set_to_command(f'mitmdump -q -p 9000 --mode upstream:{proxy_server} '
                           f'--set upstream_auth={proxy_auth} > /dev/null 2>&1 &')
            # self.set_to_command("kill_proxy.bat")
            # self.set_to_command(f'start /b mitmdump -p 9000 --mode upstream:{proxy_server}'
            #                   f' --set upstream_auth={proxy_auth}')
            return True
        else:
            self.set_to_command("./kill_proxy.sh")
            # self.set_to_command("kill_proxy.bat")
            return False
