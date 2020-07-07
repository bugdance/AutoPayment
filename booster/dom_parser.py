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
from lxml import etree


class DomParser:
    """文档解析器，用于解析DOM结构。"""

    def __init__(self):
        self.logger: any = None  # 日志记录器。

    def parse_to_attributes(self, attribute_name: str = "", selector: str = "",
                            selector_syntax: str = "", source_html: str = "") -> tuple:
        """Parse to attributes. 解析元素属性。

        Args:
            attribute_name (str): The name of the property to resolve(id/class/text). 要解析的属性名称。
            selector (str): Dom selector(css/xpath). 选择器。
            selector_syntax (str): Selector syntax. 选择器语法。
            source_html (str): The source html data. 来源网页数据。

        Returns:
            tuple: Return a tuple(a string, a list of strings).
        """
        
        try:
            html_dom = etree.HTML(source_html, parser=etree.HTMLPullParser(encoding="utf-8"))

            if selector == "css":
                elements = html_dom.cssselect(selector_syntax)
            elif selector == "xpath":
                elements = html_dom.xpath(selector_syntax)
            else:
                self.logger.info(f"解析属性参数有误(*>﹏<*)【{selector_syntax}】")
                return "", []
        except Exception as ex:
            self.logger.info(f"解析属性程序失败(*>﹏<*)【{selector_syntax}】")
            self.logger.info(f"解析属性失败原因(*>﹏<*)【{ex}】")
            return "", []
        else:
            if not elements:
                self.logger.info(f"解析属性非法元素(*>﹏<*)【{selector_syntax}】")
                return "", []

            if selector == "css":
                attr_values = []  # A list of attributes values. 属性返回值列表。
                
                for n, v in enumerate(elements):
                    if attribute_name == "text":
                        element_text = v.text
                        attr_values.append(element_text)
                    else:
                        attribute = v.attrib
                        if attribute_name not in attribute.keys():
                            self.logger.info(f"解析属性参数有误(*>﹏<*)【{selector_syntax}】【{attribute_name}】")
                            return "", []
                        else:
                            attribute_value = attribute.get(attribute_name)
                        attr_values.append(attribute_value)
                        
                if not attr_values:
                    self.logger.info(f"解析属性内容失败(*>﹏<*)【{selector_syntax}】")
                    return "", []
                    
                return attr_values[0], attr_values
            else:
                return_list = []
                for i in elements:
                    return_list.append(str(i))
                
                if not return_list:
                    self.logger.info(f"解析属性内容失败(*>﹏<*)【{selector_syntax}】")
                    return "", []
                    
                return return_list[0], return_list

    def parse_to_batch(self, attribute_name: str = "", selector: str = "css",
                       param_list: list = None, source_html: str = "") -> list:
        """解析批量元素

        Args:
            attribute_name (str): The name of the property to resolve(id/class/text). 要解析的属性名称。
            selector (str): Dom selector(css/xpath). 选择器。
            param_list (list): The list of params. 拼接请求参数的列表。
                Usage:
                    [("key", False, "value"), ("key", True, "#id"), ..]
                    name (str): Parameter name. 参数名称。
                    is_parse (bool): Whether need to parse. 是否需要解析。
                    value (str): Syntax/Value. 需要解析就是语法/不需解析就是值。

            source_html (str): The source html data. 来源网页数据。
        
        Returns:
            list
        """
        if type(attribute_name) is not str or type(selector) is not str or \
                type(param_list) is not list or type(source_html) is not str:
            self.logger.info(f"解析批量参数有误(*>﹏<*)【{param_list}】")
            return []
        
        return_list = []
        for n, v in enumerate(param_list):
            if len(v) != 3:
                self.logger.info(f"解析批量参数有误(*>﹏<*)【{v}】")
                return []
            
            is_name = str(v[0])
            is_parse = v[1]
            is_value = str(v[2])
            if type(is_name) is not str or type(is_parse) is not bool or type(is_value) is not str:
                self.logger.info(f"解析批量参数有误(*>﹏<*)【{is_name}】【{is_value}】")
                return []

            if is_parse is True:
                return_data, temp_list = self.parse_to_attributes(
                    attribute_name, selector, is_value, source_html)
                return_list.append((is_name, return_data), )
            else:
                return_list.append((is_name, is_value), )

        return return_list
