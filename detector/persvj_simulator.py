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
"""The simulator is use for verify some process."""
import ctypes


class PersVJSimulator:
    """VJ模拟器，模拟js生成cookie验证。"""
    
    def __init__(self):
        self.logger: any = None  # 日志记录器。
        # # # cookie74基础数据。
        self.cookie74_base: str = "24b03a780000000021280000000000000000000000000000000000c1c66d0c27000000" \
                                  "c94e8828b628d72a00000000ee08527a7ea9ac1a0323470477e9797078060000000000" \
                                  "000db0601a8f194e2937346a280000000011700d379601361600000000000000000000" \
                                  "00002243c2410000000087090c20db88236635ef3e3ed91ba208862d2151db06000000" \
                                  "0000000000000000000000000000000000000000000000000000000000000028000000" \
                                  "0000000000000000000000000100000000000000010000000000000000000000000000000000"
        # # # cookie75基础数据。
        self.cookie75_base: str = "000001010001000000000000000000000000057a682d434e734d6f7a696c6c612f352e3" \
                                  "0202857696e646f7773204e542031302e303b2057696e36343b2078363429204170706c" \
                                  "655765624b69742f3533372e333620284b48544d4c2c206c696b65204765636b6f29204" \
                                  "368726f6d652f37322e302e333632362e313231205361666172692f3533372e333610ff" \
                                  "bfdefffff6f9ffffbef7ffffffffff"
        self.poiuytre_list = [183, 217, 32, 13, 61, 198, 108, 73]  # 波伊特尔列表，未知参数。
        self.seal_ctx = ""  # 未知参数。
        self.key = ""  # 加解密秘钥。

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

    def string_to_hex(self, source_string: str = "") -> str:
        """字符串转16进制字符串。
        
        Args:
            source_string (str): 来源字符串。

        Returns:
            str: 返回一个16进制字符串。
        """
        if type(source_string) is not str:
            self.logger.info(f"串转十六参数有误(*>﹏<*)【{source_string}】")
            return ""
        
        return_hex = source_string.encode(encoding="iso-8859-1")
        return_hex = return_hex.hex()
        return return_hex

    def hex_to_string(self, hex_string: str = "") -> str:
        """16进制字符串转字符串。

        Args:
            hex_string (str): 16进制字符串。

        Returns:
            str: 返回普通字符串。
        """
        try:
            return_string = bytes.fromhex(hex_string)
            return_string = return_string.decode(encoding="iso-8859-1")
        except Exception as ex:
            self.logger.info(f"十六转串程序失败(*>﹏<*)【{hex_string}】")
            self.logger.info(f"十六转串失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return return_string

    def break_into_int(self, source_char: str = "", source_signed: bool = True) -> int:
        """分解字符为流数字。
        
        Args:
            source_char (str): 来源字符。
            source_signed (bool): 是否有符号。

        Returns:
            int
        """
        if type(source_char) is not str or type(source_signed) is not bool:
            self.logger.info(f"分解数字参数有误(*>﹏<*)【{source_char}】")
            return 0

        return_int = source_char.encode(encoding="iso-8859-1")
        return_int = int.from_bytes(return_int, byteorder='big', signed=source_signed)
        return return_int

    def break_into_stream(self, source_string: str = "", source_signed: bool = True) -> any:
        """分解字符串为流数字串。
        
        Args:
            source_string (str): 来源字符串。
            source_signed (bool): 是否有符号。

        Returns:
            any
        """
        for s in source_string:
            yield_int = self.break_into_int(s, source_signed)
            yield yield_int

    def break_into_list(self, source_string: str = "", source_signed: bool = True) -> list:
        """分解字符串为流数字列表。

        Args:
            source_string (str): 来源字符串。
            source_signed (bool): 是否有符号。

        Returns:
            list
        """
        return_list = self.break_into_stream(source_string, source_signed)
        return_list = list(return_list)
        return return_list

    def compose_onto_character(self, source_int: int = 0, int_length: int = 1, source_signed=True) -> str:
        """整数组合成字符。
        
        Args:
            source_int (int): 来源数字。
            int_length (int): 组合长度。
            source_signed (bool): 是否有符号。

        Returns:
            str
        """
        try:
            return_string = source_int.to_bytes(length=int_length, byteorder="big", signed=source_signed)
            return_string = return_string.decode(encoding="iso-8859-1")
        except Exception as ex:
            self.logger.info(f"组合字符程序失败(*>﹏<*)【{source_int}】")
            self.logger.info(f"组合字符失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return return_string

    def compose_onto_stream(self, source_list: list = None, int_length: int = 1, source_signed=True) -> str:
        """流数字串组成为流字符串。
        
        Args:
            source_list (list): 来源数字列表。
            int_length (int): 组合长度。
            source_signed (bool): 是否有符号。

        Returns:
            str
        """
        for s in source_list:
            yield_string = self.compose_onto_character(s, int_length, source_signed)
            yield yield_string

    def compose_onto_string(self, source_list: list = None, int_length: int = 1, source_signed=True) -> str:
        """流数字列表组成为字符串。

        Args:
            source_list (list): 来源数字列表。
            int_length (int): 组合长度。
            source_signed (bool): 是否有符号。

        Returns:
            str
        """
        return_list = self.compose_onto_stream(source_list, int_length, source_signed)
        return_list = list(return_list)
        return_string = "".join(return_list)
        return return_string

    def xor_of_int(self, fist_list: list = None, second_list: list = None) -> list:
        """字节数组异或。

        Args:
            fist_list (list): 第一数字列表。
            second_list (list): 第二数字列表。

        Returns:
            list
        """
        if type(fist_list) is not list or type(second_list) is not list or len(fist_list) != len(second_list):
            self.logger.info(f"字节异或参数有误(*>﹏<*)【{fist_list}】")
            return []
    
        return_list = []
        for i in range(len(fist_list)):
            return_list.append(0)
    
        for i in range(len(return_list)):
            return_list[i] = fist_list[i] ^ second_list[i]
    
        return return_list

    def xor_of_string(self, first_string: str = "", second_string: str = "") -> str:
        """字符串异或。

        Args:
            first_string (str): 第一字符串。
            second_string (str): 第二字符串。

        Returns:
            str
        """
        if type(first_string) is not str or type(second_string) is not str \
                or len(first_string) != len(second_string):
            self.logger.info(f"字串异或参数有误(*>﹏<*)【{first_string}】")
            return ""
    
        return_string = ""
        for s in range(len(first_string)):
            first_int = self.break_into_int(first_string[s], source_signed=False)
            second_int = self.break_into_int(second_string[s], source_signed=False)
            return_int = first_int ^ second_int
            s_string = self.compose_onto_character(return_int, source_signed=False)
            return_string += s_string
    
        return return_string

    def read_as_int(self, source_string: str = "") -> any:
        """读取倒置字符串转数字流。
        
        Args:
            source_string (str): 来源字符串。

        Returns:
            any
        """
        if type(source_string) is not str or len(source_string) % 4 != 0:
            self.logger.info(f"倒置字符参数有误(*>﹏<*)【{source_string}】")
            return 0
        
        for s in range(0, len(source_string), 4):
            first_s = source_string[s]
            second_s = source_string[s + 1]
            third_s = source_string[s + 2]
            fourth_s = source_string[s + 3]
            return_string = fourth_s + third_s + second_s + first_s
            return_int = self.break_into_int(return_string)
            yield return_int
            
    def read_as_list(self, source_string: str = "") -> list:
        """读取倒置字符串转数字列表。
        
        Args:
            source_string (str): 来源字符串。

        Returns:
            list
        """
        return_list = self.read_as_int(source_string)
        return_list = list(return_list)
        return return_list
    
    def write_as_list(self, source_int: int = 0) -> list:
        """数字列表倒序。
        
        Args:
            source_int (int): 来源数字。

        Returns:
            list
        """
        if type(source_int) is not int:
            self.logger.info(f"倒序数表参数有误(*>﹏<*)【{source_int}】")
            return []
        
        return_string = self.compose_onto_character(source_int, 4)
        return_list = self.break_into_list(return_string)
        return_list.reverse()
        return return_list
    
    def write_as_short(self, source_int: int = 0) -> list:
        """数字短表。
        
        Args:
            source_int (int): 来源数字。

        Returns:
            list
        """
        if type(source_int) is not int:
            self.logger.info(f"数字短表参数有误(*>﹏<*)【{source_int}】")
            return []
        
        first_int = 255 & source_int
        second_int = 255 & (source_int >> 8)
        first_int = self.compose_onto_character(first_int, source_signed=False)
        first_int = self.break_into_int(first_int)
        second_int = self.compose_onto_character(second_int, source_signed=False)
        second_int = self.break_into_int(second_int)
        return_list = [first_int, second_int]
        return return_list

    def padding_as_string(self, source_string: str = "", mod_length: int = 0, char_int: int = 0) -> str:
        """字符串填充。
        
        Args:
            source_string (str): 来源数据。
            mod_length (int): 分段长度。
            char_int (int): 补位数字。

        Returns:
            str
        """
        if type(source_string) is not str or type(mod_length) is not int or type(char_int) is not int:
            self.logger.info(f"字串填充参数有误(*>﹏<*)【{source_string}】")
            return ""
        
        pad_length = 7 - len(source_string) % mod_length
        pad_string = self.compose_onto_character(pad_length, source_signed=False)
        chr_string = self.compose_onto_character(char_int, source_signed=False)
        
        for i in range(pad_length):
            source_string += chr_string
        source_string += pad_string
    
        return source_string

    def check_the_sign(self, source_string: str = "") -> list:
        """校验数据。

        Args:
            source_string (str): 来源数据。

        Returns:
            list
        """
        if type(source_string) is not str:
            self.logger.info(f"校验数据参数有误(*>﹏<*)【{source_string}】")
            return []
        
        first_key = self.xor_of_string(self.key, "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
        second_key = self.xor_of_string(self.key, "6666666666666666")
        return_data = self.check_the_poiuytre(second_key + source_string)
        return_data = self.check_the_poiuytre(first_key + return_data)
        return_list = self.break_into_list(return_data)
        return return_list

    def check_the_poiuytre(self, source_string: str = "") -> str:
        """校验波伊特尔。
        
        Args:
            source_string (str): 来源数据。

        Returns:
            str
        """
        if type(source_string) is not str:
            self.logger.info(f"校验波伊参数有误(*>﹏<*)【{source_string}】")
            return ""
        
        p_string = "poiuytre"
        source_string = self.padding_as_string(source_string, 8, 121)
        
        for i in range(0, len(source_string), 8):
            key_data = source_string[i:i + 8]
            p_data = self.compose_onto_string(self.poiuytre_list, source_signed=False)
            key_data += self.xor_of_string(key_data, p_data)
            key_arr = self.read_as_list(key_data)
        
            return_list = self.encrypt_into_tea(p_string, key_arr, False)
            return_data = self.compose_onto_string(return_list)
            p_string = self.xor_of_string(p_string, return_data)

        return p_string

    def encrypt_into_tea(self, source_string: str = "", key_array: list = None, is_secured: bool = True) -> list:
        """TEA加密。

        Args:
            source_string (str): 来源数据。
            key_array (list): 切分后的密钥数组。
            is_secured (bool): 是否加密。

        Returns:
            list
        """
        if type(source_string) is not str or type(key_array) is not list or type(is_secured) is not bool:
            self.logger.info("数据加密参数有误(*>﹏<*)【TEA】")
            return []
        
        delta = -478700656 if is_secured else 0
        # # # 声明data high。
        data_high = source_string[:4]
        d_string = data_high[3] + data_high[2] + data_high[1] + data_high[0]
        data_high = self.break_into_int(d_string)
        # # # 声明data low。
        data_low = source_string[4:]
        d_string = data_low[3] + data_low[2] + data_low[1] + data_low[0]
        data_low = self.break_into_int(d_string)
        # # # 加密算法，都进行了Int溢出操作。
        for i in range(16):
            if is_secured:
                first_int = self.format_to_overflow(data_high << 4) ^ self.format_to_rightshift(data_high, 5)
                first_int = self.format_to_overflow(first_int)
                first_int += data_high
                first_int = self.format_to_overflow(first_int)
                second_int = delta + key_array[self.format_to_rightshift(delta, 11) & 3]
                second_int = self.format_to_overflow(second_int)

                final_int = first_int ^ second_int
                final_int = self.format_to_overflow(final_int)
                data_low -= final_int
                data_low = self.format_to_overflow(data_low)

                delta -= -1640531527
                delta = self.format_to_overflow(delta)

                first_int = self.format_to_overflow(data_low << 4) ^ self.format_to_rightshift(data_low, 5)
                first_int = self.format_to_overflow(first_int)
                first_int += data_low
                first_int = self.format_to_overflow(first_int)
                second_int = delta + key_array[delta & 3]
                second_int = self.format_to_overflow(second_int)

                final_int = first_int ^ second_int
                final_int = self.format_to_overflow(final_int)
                data_high -= final_int
                data_high = self.format_to_overflow(data_high)
            else:

                first_int = self.format_to_overflow(data_low << 4) ^ self.format_to_rightshift(data_low, 5)
                first_int = self.format_to_overflow(first_int)
                first_int += data_low
                first_int = self.format_to_overflow(first_int)
                second_int = delta + key_array[delta & 3]
                second_int = self.format_to_overflow(second_int)

                final_int = first_int ^ second_int
                final_int = self.format_to_overflow(final_int)
                data_high += final_int
                data_high = self.format_to_overflow(data_high)

                delta += -1640531527
                delta = self.format_to_overflow(delta)

                first_int = self.format_to_overflow(data_high << 4) ^ self.format_to_rightshift(data_high, 5)
                first_int = self.format_to_overflow(first_int)
                first_int += data_high
                first_int = self.format_to_overflow(first_int)
                second_int = delta + key_array[self.format_to_rightshift(delta, 11) & 3]
                second_int = self.format_to_overflow(second_int)

                final_int = first_int ^ second_int
                final_int = self.format_to_overflow(final_int)
                data_low += final_int
                data_low = self.format_to_overflow(data_low)
        
        high_list = self.write_as_list(data_high)
        low_list = self.write_as_list(data_low)
        high_list.extend(low_list)
    
        return high_list
    
    def secure_the_data(self, source_string: str = "", key_string: str = "", is_secured: bool = True) -> str:
        """数据加密。

        Args:
            source_string (str): 来源数据。
            key_string (str): 秘钥数据。
            is_secured (bool): 是否加密。

        Returns:
            string
        """
        if type(source_string) is not str or type(key_string) is not str or type(is_secured) is not bool:
            self.logger.info("数据加密参数有误(*>﹏<*)【secure】")
            return ""
        
        key_arr = self.read_as_list(key_string)
        iv = [0, 0, 0, 0, 0, 0, 0, 0]
        return_list = []
        if not is_secured:
            source_string = self.padding_as_string(source_string, 8, 255)
        
        for i in range(0, len(source_string), 8):
            if is_secured:
                data_i = source_string[i:i + 8]
                data_list = self.encrypt_into_tea(data_i, key_arr, is_secured)
                data_list = self.xor_of_int(iv, data_list)
                return_list.extend(data_list)
                
                for j in range(len(iv)):
                    single_data = source_string[i + j]
                    single_int = self.break_into_int(single_data)
                    iv[j] = single_int
            else:
                data_i = source_string[i:i + 8]
                data_list = self.break_into_list(data_i)
                data_list = self.xor_of_int(iv, data_list)
                single_data = self.compose_onto_string(data_list)
                
                iv = self.encrypt_into_tea(single_data, key_arr, is_secured)
                return_list.extend(iv)
        
        return_data = self.compose_onto_string(return_list)
        
        return return_data

    def unblock_to_message(self, message: str = "", is_secured: bool = True) -> str:
        """解封消息。

        Args:
            message (str): 消息。
            is_secured (bool): 是否加密。

        Returns:
            str
        """
        if type(message) is not str or type(is_secured) is not bool:
            self.logger.info("解封消息参数有误(*>﹏<*)【unblock】")
            return ""
        
        message_list = self.break_into_list(message)
        hdr_len = abs(message_list[0])
        self.seal_ctx = message[1:5]
        data_len = abs(message_list[6])
        data = message[hdr_len + 8:data_len + hdr_len]
        
        if is_secured:
            data = self.secure_the_data(data, self.key, True)
            
        data_list = self.break_into_list(data)
        n = data_list[-1]
        return_data = data[:len(data) - n - 1]
    
        return return_data

    def block_to_message(self, message: str = "", scope: int = 0) -> str:
        """密封消息。

        Args:
            message (str): 待密封数据。
            scope (str): 数据类型表示。

        Returns:
            str
        """
        if type(message) is not str or type(scope) is not int:
            self.logger.info("密封消息参数有误(*>﹏<*)【block】")
            return ""
        
        return_list = [8]
        seal_list = self.break_into_list(self.seal_ctx)
        return_list.extend(seal_list)
        return_list.append(scope)
        
        encrypt_data = self.secure_the_data(message, self.key, False)
        scope_string = self.compose_onto_character(scope, source_signed=False)
        sign_data = self.check_the_sign(encrypt_data + self.seal_ctx + scope_string)
        short_list = self.write_as_short(len(encrypt_data) + len(sign_data))
        
        return_list.extend(short_list)
        return_list.extend(sign_data)
        encrypt_list = self.break_into_list(encrypt_data)
        return_list.extend(encrypt_list)
        ret_data = self.compose_onto_string(return_list)
        
        return ret_data

