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
"""The formatter is use for format structure data."""
import ctypes
import copy


class BasicFormatter:
    """基础格式器，复制数据，格式化数字，整数溢出，无符号右移。"""

    def __init__(self):
        self.logger: any = None  # 日志记录器。

    def format_to_same(self, source_data: any = None) -> any:
        """Copy as data. 镜像一份数据。
        
        Args:
            source_data (any): The source data. 来源数据。
        
        Returns:
            any: Same as the source data. 同源数据。
        """
        if not source_data:
            self.logger.info(f"格式镜像参数有误(*>﹏<*)【same】")
        
        return_data = copy.deepcopy(source_data)
        return return_data

    def format_to_int(self, source_data: any = None) -> int:
        """Format to int. 格式化为整数。

        Args:
            source_data (any): The source data. 来源数据。

        Returns:
            int
        """
        if type(source_data) is str:
            source_data = source_data.replace(",", "")
            
        try:
            return_data = int(source_data)
        except Exception as ex:
            self.logger.info(f"格式整数程序失败(*>﹏<*)【{source_data}】")
            self.logger.info(f"格式整数失败原因(*>﹏<*)【{ex}】")
            return 0
        else:
            return return_data

    def format_to_float(self, decimal_num: int = 2, source_data: any = None) -> float:
        """Format to float. 格式化为浮点数。

        Args:
            decimal_num (int): Return the number of decimal place. 返回小数位数。
            source_data (any): The source data. 来源数据。

        Returns:
            float
        """
        if type(source_data) is str:
            source_data = source_data.replace(",", "")
            
        try:
            return_data = float(source_data).__round__(decimal_num)
        except Exception as ex:
            self.logger.info(f"格式浮点程序失败(*>﹏<*)【{source_data}】")
            self.logger.info(f"格式浮点失败原因(*>﹏<*)【{ex}】")
            return 0.0
        else:
            return return_data

    def format_to_cut(self, decimal_num: int = 2, source_data: any = None) -> str:
        """Intercepting floating-point strings. 截取浮点字符串。
    
        Args:
            decimal_num (int): Return the number of decimal place. 返回小数位数。
            source_data (any): The source data. 来源数据。

        Returns:
            str: Return a floating point string. 返回浮点字符串。
        """
        if type(source_data) is str:
            source_data = source_data.replace(",", "")
            
        try:
            source_data = float(source_data)
            return_data = f"{source_data:.{decimal_num}f}"
        except Exception as ex:
            self.logger.info(f"格式浮点字符失败(*>﹏<*)【{source_data}】")
            self.logger.info(f"浮点字符失败原因(*>﹏<*)【{ex}】")
            return "0.00"
        else:
            return return_data

    def format_to_overflow(self, source_int: int = 0) -> int:
        """Integer type overflow. 格式化为32位int类型溢出。

        Args:
            source_int (int): The source int. 来源数字。

        Returns:
            int
        """
        if type(source_int) is not int:
            self.logger.info(f"格式溢出参数有误(*>﹏<*)【{source_int}】")
            return 0
        # # # Maximum java int. java的int类型最大值。
        maxint = 2147483647
        if not -maxint - 1 <= source_int <= maxint:
            return_int = (source_int + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
        else:
            return_int = source_int
            
        return return_int

    def format_to_rightshift(self, source_int: int = 0, shift_num: int = 0) -> int:
        """Unsigned right shift. 格式化为无符号右移。

        Args:
            source_int (int): The source int. 来源数字。
            shift_num (int): The number of right shift. 右移位数。

        Returns:
            int
        """
        if type(source_int) is not int or type(shift_num) is not int:
            self.logger.info(f"格式右移参数有误(*>﹏<*)【{source_int}】")
            return 0
        # # # If the number is less than 0, convert to 32-bit unsigned uint. 如果数字小于0，则转为32位无符号uint。
        if source_int < 0:
            source_int = ctypes.c_uint32(source_int).value
        # # # In order to be compatible with js and things like, the negative number shifts to the left.
        # # # 为了兼容js之类的，负数就右移变成左移。
        if shift_num < 0:
            return_int = -self.format_to_overflow(source_int << abs(shift_num))
        else:
            return_int = self.format_to_overflow(source_int >> shift_num)
    
        return return_int
