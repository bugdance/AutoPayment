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


class CallInParser:
    """接入解析器，解析接口结构数据。"""
    
    def __init__(self, enable_corp: bool = True):
        """Init.
        
        Args:
            enable_corp (bool): Whether it is a corporate account(True/False). 是否是企业账户。
        """
        self.logger: any = None  # 日志记录器。
        self.enable_corp: bool = enable_corp  # 是否是企业类型。
        # # # Interface data. 接口数据。
        self.task_id: any = None  # 任务编号。
        self.username: str = ""  # 最终用的用户名。
        self.password: str = ""  # 最终用的密码。
        self.departure_code: str = ""  # 始发三字码。
        self.arrival_code: str = ""  # 到达三字码。
        self.flight_num: str = ""  # 航班号，只支持直飞。
        self.segment_num: int = 0  # 航段数量。
        self.flight_date: str = ""  # 出发日期。
        self.promo: str = ""  # 优惠码。
        self.currency: str = ""  # 默认货币类型。
        self.pnr_code: str = ""  # 已经占完舱的PNR。
        self.target_price: float = 0.00  # 目标价格。
        self.diff_price: float = 0.00  # 价格差价。
        self.adult_list: list = []  # 成人列表明细。
        self.child_list: list = []  # 儿童列表明细。
        self.infant_list: list = []  # 婴儿列表明细。
        self.adult_num: int = 0  # 成人人数。
        self.child_num: int = 0  # 儿童人数。
        self.infant_num: int = 0  # 婴儿人数。
        # # # Card data. 接口支付卡数据。
        self.card_last: str = ""  # 支付卡联系人姓氏。
        self.card_first: str = ""  # 支付卡联系人名字。
        self.card_num: str = ""  # 支付卡联系人姓氏。
        self.card_code: str = ""  # 支付卡联系人姓氏。
        self.card_date: str = ""  # 支付卡联系人姓氏。
        # # # Manual value. 填死数据。
        self.contact_last: str = ""  # 联系人姓氏。
        self.contact_first: str = ""  # 联系人名字。
        self.contact_email: str = ""  # 联系邮箱。
        self.contact_mobile: str = ""  # 联系电话。
        # # # Return data. 返回数据。
        self.return_baggage: list = []  # 返回行李列表, 原样返回还要加每个人价格。
        
    def parse_to_interface(self, source_dict: dict = None) -> bool:
        """Parsing interface parameters. 解析接口数据。
        
        Args:
            source_dict (dict): The source dict. 来源字典。

        Returns:
            bool
        """
        if not source_dict or type(source_dict) is not dict:
            self.logger.info(f"解析接口参数有误(*>﹏<*)【{source_dict}】")
            return False
        # # # Parse the username and password. 解析账户名和密码，不区分企业个人。
        # account_agent = source_dict.get('carrierAccountAgent')
        account = source_dict.get('carrierAccount')
        if self.enable_corp:
            self.username = account
            # self.password = source_dict.get('carrierPasswordAgent')
            self.password = source_dict.get('carrierPassword')
        else:
            self.username = account
            self.password = source_dict.get('carrierPassword')
        # # # Parse the detail. 解析航班信息。
        self.task_id = source_dict.get('automaticGetTicketId')
        self.departure_code = source_dict.get('departureAirport')
        self.arrival_code = source_dict.get('arriveAirport')
        self.flight_date = source_dict.get('departureTime')
        self.promo = source_dict.get("promotionCode")
        self.currency = source_dict.get("currency")
        self.pnr_code = source_dict.get("pnrCode")
        self.target_price = source_dict.get('price')
        self.diff_price = source_dict.get('priceDifference')
        # # # Parse the contact. 解析联系人信息。
        self.contact_last = "Wang"
        self.contact_first = "XiaoDao"
        self.contact_email = "168033518@qq.com"
        self.contact_mobile = "16639168284"
        # # # Parse the flight number. 航班号单独解析。
        flight_num = source_dict.get('flightNumber')
        if not self.parse_to_flight(flight_num):
            return False
        # # # Parse the card. VCC卡解析。
        vcc = source_dict.get('VCC')
        self.parse_to_card(vcc)
        # # # Parse the passengers. 乘客信息解析。
        passengers_list = source_dict.get('passengerBaggages')
        if not self.parse_to_passenger(passengers_list):
            return False
        
        return True
    
    def parse_to_flight(self, flight_num: str = "") -> bool:
        """Parse the flight number. 解析航班号。
        
        Args:
            flight_num (str): Flight number. 航班号。

        Returns:
            bool
        """
        if not flight_num or type(flight_num) is not str or len(flight_num) < 3:
            self.logger.info(f"解析航班参数有误(*>﹏<*)【{flight_num}】")
            return False
        
        self.flight_num = flight_num
        self.segment_num = 1
        return True

    def parse_to_card(self, source_card: dict = None) -> bool:
        """Parse the card. 解析支付卡。
        
        Args:
            source_card (dict): The card dict. 支付卡信息。

        Returns:
            bool
        """
        if not source_card or type(source_card) is not dict:
            self.logger.info(f"解析卡的参数有误(*>﹏<*)【{source_card}】")
        else:
            self.card_num = source_card.get("cardNumber")
            name = source_card.get("cardName")
            self.card_code = source_card.get("cardSafetyCode")
            self.card_date = source_card.get("cardTermValidity")
    
            if not self.card_num or not name or not self.card_code \
                    or not self.card_date and len(self.card_date) != 4:
                self.logger.info(f"解析卡的参数有误(*>﹏<*)【{source_card}】")
            else:
                name = name.split("/")
                if len(name) < 2:
                    self.logger.info(f"解解析卡的参数有误(*>﹏<*)【{source_card}】")
                else:
                    self.card_last = name[0]
                    self.card_first = name[1]
        
        return True
    
    def parse_to_passenger(self, passengers_list: list = None) -> bool:
        """Parse the passengers. 乘客信息解析。
        
        Args:
            passengers_list (list): The passengers list. 乘客列表。

        Returns:
            bool
        """
        if not passengers_list or type(passengers_list) is not list:
            self.logger.info(f"解析乘客参数有误(*>﹏<*)【{passengers_list}】")
            return False
        
        for n, v in enumerate(passengers_list):
            full_name = v.get('passengerName')  # 姓名。
            age_type = v.get('type')  # 乘客类型（0成人/1儿童/2婴儿）。
            gender = v.get('gender')  # 性别（M/F）。
            birthday = v.get('birthday')  # 生日（19840727）。
            nationality = v.get('nationality')  # 国籍（CN）。
            card_num = v.get('cardNum')  # 护照。
            card_expired = v.get('cardExpired')  # 护照时间（20840727）。
            card_place = v.get('cardIssuePlace')  # 护照签发地（CN）。
            baggage = v.get('baggages')  # 行李。
            # # # Check the data. 检查数据。
            if not full_name or not birthday or not gender or type(age_type) is not int:
                self.logger.info(f"解析乘客参数有误(*>﹏<*)【{n}】【{v}】")
                return False
            
            name_list = full_name.split('/')
            if len(name_list) < 2:
                self.logger.info(f"解析乘客姓名有误(*>﹏<*)【{n}】【{full_name}】")
                return False
            # # # Compose onto the data. 组合数据。
            list_data = {
                "last_name": name_list[0], "first_name": name_list[1], "gender": gender,
                "birthday": birthday, "nationality": nationality, "card_num": card_num,
                "card_expired": card_expired, "card_place": card_place, "baggage": baggage
            }
            if age_type == 0:
                self.adult_list.append(list_data)
            elif age_type == 1:
                self.child_list.append(list_data)
            elif age_type == 2:
                self.infant_list.append(list_data)

        self.adult_num = len(self.adult_list)
        self.child_num = len(self.child_list)
        self.infant_num = len(self.infant_list)
        if not self.adult_num:
            self.logger.info(f"解析乘客成人有误(*>﹏<*)【{passengers_list}】")
            return False
        
        return True

