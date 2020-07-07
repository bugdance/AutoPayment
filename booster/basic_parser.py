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
"""The parser is use for parse the data."""
from urllib.parse import urlencode, parse_qs, urlparse
from urllib.parse import quote_plus, unquote_plus
import re
import json
import jsonpath


class BasicParser:
    """基础解析器，用于解析数据结构。"""

    def __init__(self):
        self.logger: any = None  # 日志记录器。
        
    def parse_to_eval(self, source_data: any = None) -> any:
        """Parse to eval. 解析数据源码格式。
        
        Args:
            source_data (any): The source data. 来源数据。

        Returns:
            any
        """
        if type(source_data) is str or type(source_data) is bytes:
            return_data = eval(source_data)
            return return_data
        else:
            self.logger.info("解析源码非法传参(*>﹏<*)【eval】")
            return None

    def parse_to_url(self, source_tuple: tuple = None, source_encoding: str = "utf-8") -> str:
        """Parse to url. 解析链接地址。

        Args:
            source_tuple (tuple): The source tuple. 来源数据。
            source_encoding (str): The source encoding. 解析编码。

        Returns:
            str
        """
        try:
            return_data = urlencode(source_tuple, encoding=source_encoding)
        except Exception as ex:
            self.logger.info("解析链接地址失败(*>﹏<*)【url】")
            self.logger.info(f"解析链接失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return return_data

    def parse_to_params(self, source_url: str = "", source_encoding: str = "utf-8") -> tuple:
        """Parse to parameters. 解析参数。
        
        Args:
            source_url (str): The source url. 来源地址。
            source_encoding (str): The source encoding. 解析编码。

        Returns:
            tuple: Return a tuple(a string, a list of strings).
        """
        try:
            return_list = []
            url_query = urlparse(source_url).query
            url_dict = parse_qs(url_query, encoding=source_encoding)
            for k, v in url_dict.items():
                for i in v:
                    return_list.append((k, i))
            return_tuple = tuple(return_list)
        except Exception as ex:
            self.logger.info("解析参数程序失败(*>﹏<*)【params】")
            self.logger.info(f"解析参数失败原因(*>﹏<*)【{ex}】")
            return ()
        else:
            return return_tuple

    def parse_to_quote(self, source_string: str = "", source_encoding: str = "utf-8") -> str:
        """Parse to quote. 解析引用。
        
        Args:
            source_string (str): The source string. 来源数据。
            source_encoding (str): The source encoding. 解析编码。

        Returns:
            str
        """
        try:
            return_data = quote_plus(source_string, encoding=source_encoding)
        except Exception as ex:
            self.logger.info("解析引用程序失败(*>﹏<*)【quote】")
            self.logger.info(f"解析引用失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return return_data

    def parse_to_unquote(self, source_string: str = "", source_encoding: str = "utf-8") -> str:
        """Parse to unquote. 解析反引。
        
        Args:
            source_string (str): The source string. 来源数据。
            source_encoding (str): The source encoding. 解析编码。

        Returns:
            str
        """
        try:
            return_data = unquote_plus(source_string, encoding=source_encoding)
        except Exception as ex:
            self.logger.info("解析反引程序失败(*>﹏<*)【unquote】")
            self.logger.info(f"解析反引失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return return_data

    def parse_to_list(self, source_data: any = None, source_encoding: str = "utf-8") -> list:
        """Parse to list. 解析列表。
        
        Args:
            source_data (any): The source data(str/bytes). 来源数据。
            source_encoding (str): The source encoding. 解析编码。

        Returns:
            list
        """
        try:
            return_data = json.loads(source_data, encoding=source_encoding)
        except Exception as ex:
            self.logger.info("解析列表程序失败(*>﹏<*)【list】")
            self.logger.info(f"解析列表失败原因(*>﹏<*)【{ex}】")
            return []
        else:
            if type(return_data) is not list:
                self.logger.info("解析列表非法返回(*>﹏<*)【list】")
                return []
            
            return return_data

    def parse_to_dict(self, source_data: any = None, source_encoding: str = "utf-8") -> dict:
        """Parse to dict. 解析字典。

        Args:
            source_data (any): The source data(str/bytes). 来源数据。
            source_encoding (str): The source encoding. 解析编码。

        Returns:
            dict
        """
        try:
            return_data = json.loads(source_data, encoding=source_encoding)
        except Exception as ex:
            self.logger.info("解析字典程序失败(*>﹏<*)【dict】")
            self.logger.info(f"解析字典失败原因(*>﹏<*)【{ex}】")
            return {}
        else:
            if type(return_data) is not dict:
                self.logger.info("解析字典非法返回(*>﹏<*)【dict】")
                return {}

            return return_data

    def parse_to_json(self, source_data: any = None) -> str:
        """Parse to json string. 解析json串。

        Args:
            source_data (any): The source data. 来源数据。

        Returns:
            str
        """
        try:
            return_data = json.dumps(source_data, ensure_ascii=False)
        except Exception as ex:
            self.logger.info("解析数据程序失败(*>﹏<*)【json string】")
            self.logger.info(f"解析数据失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return return_data

    def parse_to_replace(self, replaced_syntax: str = "",
                         replaced_string: str = "", source_string: str = "") -> str:
        """Parse to replace. 解析替换。
        
        Args:
            replaced_syntax (str): The replaced syntax. 替换语法。
            replaced_string (str): The replaced string. 替换后字符串。
            source_string (str): The source string. 来源数据。

        Returns:
            str
        """
        try:
            return_data = re.sub(replaced_syntax, replaced_string, source_string)
        except Exception as ex:
            self.logger.info("解析替换程序失败(*>﹏<*)【replace】")
            self.logger.info(f"解析替换失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return return_data

    def parse_to_clear(self, source_string: str = "") -> str:
        """Parse to clear. 解析清空。
        
        Args:
            source_string (str): The source string. 来源数据。

        Returns:
            str
        """
        if type(source_string) is not str:
            self.logger.info("解析清空非法传参(*>﹏<*)【clear】")
            return ""

        return_data = re.sub("\r|\n|\t|\s+", "", source_string)
        
        return return_data

    def parse_to_separate(self, source_string: str = "") -> str:
        """Parse to separate. 解析分割。

        Args:
            source_string (str): The source string. 来源数据。

        Returns:
            str
        """
        if type(source_string) is not str:
            self.logger.info("解析分割非法传参(*>﹏<*)【separate】")
            return ""

        return_data = re.sub("\r|\n|\t", "", source_string)
        return_data = re.sub("\s+", " ", return_data)
        return_data = return_data.strip(" ")

        return return_data

    def parse_to_regex(self, regex_syntax: str = "", source_string: str = "") -> tuple:
        """Parse to regex. 解析匹配。
        
        Args:
            regex_syntax (str): The regex syntax. 正则语法。
            source_string (str): The source string. 来源数据。

        Returns:
            tuple: Return a tuple(a string, a list of strings).
        """
        try:
            return_data = re.findall(regex_syntax, source_string, re.S)
        except Exception as ex:
            self.logger.info(f"解析匹配程序失败(*>﹏<*)【{regex_syntax}】")
            self.logger.info(f"解析匹配失败原因(*>﹏<*)【{ex}】")
            return "", []
        else:
            if not return_data:
                self.logger.info(f"解析匹配内容失败(*>﹏<*)【{regex_syntax}】")
                return "", []

            return return_data[0], return_data

    def parse_to_path(self, path_syntax: str = "", source_data: any = None) -> tuple:
        """Parse to path. 解析路径。
        
        Args:
            path_syntax (str): The path syntax. 路径语法。
            source_data (any): The source data. 来源数据。

        Returns:
            tuple: Return a tuple(a string, a list of strings).
        """
        if type(path_syntax) is not str or not source_data:
            self.logger.info(f"解析路径非法传参(*>﹏<*)【{path_syntax}】")
            return "", []

        return_data = jsonpath.jsonpath(source_data, path_syntax)

        if not return_data:
            self.logger.info(f"解析路径内容失败(*>﹏<*)【{path_syntax}】")
            return "", []

        return return_data[0], return_data
