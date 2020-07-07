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
from base64 import b64encode, decodebytes
from Crypto.Cipher import AES
import hashlib


class AESFormatter:
    """AES格式器，AES加密，解密，sha1加密。"""

    def __init__(self):
        self.logger: any = None  # 日志记录器。
        self.password_key: str = "88ios99android66"  # 密码秘钥。
        self.vcc_key: str = "hgg7xtdQb7hJvzWD"  # vcc支付卡秘钥，目前没用。

    def encrypt_into_sha1(self, source_key: str = "") -> str:
        """SHA1 encryption. SHA1加密。

        Args:
            source_key (str): The source key. 来源关键值。

        Returns:
            str
        """
        if type(source_key) is not str:
            self.logger.info(f"加密字符参数有误(*>﹏<*)【SHA1】【{source_key}】")
            return ""
            
        key_bytes = source_key.encode('utf-8')
        signature = hashlib.sha1(key_bytes).digest()
        signature = hashlib.sha1(signature).digest()
        key_hex = signature.hex()
        key_hex = key_hex.upper()[:32]
        return key_hex

    def encrypt_into_aes(self, source_key: str = "", source_string: str = "") -> str:
        """AES encryption. AES加密。
        
        Args:
            source_key (str): The source key. 来源关键值。
            source_string (str): The source string. 来源数据。

        Returns:
            str
        """
        try:
            key_hex = bytes.fromhex(source_key)
            crypto = AES.new(key_hex, AES.MODE_ECB)
            padding_value = source_string + (AES.block_size - len(source_string) % AES.block_size) \
                            * chr(AES.block_size - len(source_string) % AES.block_size)
            padding_value = padding_value.encode("utf-8")
            cipher_text = crypto.encrypt(padding_value)
            cipher_text = b64encode(cipher_text)
            cipher_text = cipher_text.decode('utf-8')
        except Exception as ex:
            self.logger.info(f"加密字符程序失败(*>﹏<*)【AES】【{source_string}】")
            self.logger.info(f"加密字符失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return cipher_text

    def decrypt_into_aes(self, source_key: str = "", source_string: str = "") -> str:
        """AES decryption. AES解密。
        
        Args:
            source_key (str): The source key. 来源关键值。
            source_string (str): The source string. 来源数据。

        Returns:
            str
        """
        try:
            key_hex = bytes.fromhex(source_key)
            crypto = AES.new(key_hex, AES.MODE_ECB)
            base64_decrypted = decodebytes(source_string.encode(encoding='utf-8'))
            cipher_text = crypto.decrypt(base64_decrypted)
            padding_value = cipher_text[:-ord(cipher_text[len(cipher_text) - 1:])]
            padding_value = padding_value.decode('utf-8')
        except Exception as ex:
            self.logger.info(f"解密字符程序失败(*>﹏<*)【AES】【{source_string}】")
            self.logger.info(f"解密字符失败原因(*>﹏<*)【{ex}】")
            return ""
        else:
            return padding_value
