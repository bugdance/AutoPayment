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
from datetime import datetime, timedelta
import calendar
import pytz
import re


class DateFormatter:
    """日期格式器，用于格式化时间。"""

    def __init__(self):
        self.logger: any = None  # 日志记录器。

    def format_to_last(self, source_year: int = 0, source_month: int = 0) -> int:
        """Format time to the last day. 格式月末日期。
        
        Args:
            source_year (int): The source year. 来源年份。
            source_month (int): The source month. 来源月份。

        Returns:
            int
        """
        try:
            last_day = calendar.monthrange(source_year, source_month)[1]
        except Exception as ex:
            self.logger.info(f"格式月末日期失败(*>﹏<*)【{source_year}】【{source_month}】")
            self.logger.info(f"格式月末失败原因(*>﹏<*)【{ex}】")
            return 31
        else:
            return last_day

    def format_to_transform(self, source_time: str = "", source_format: str = "") -> datetime:
        """Format to transform. 格式时间转换后的日期。

        Args:
            source_time (str): The source time. 来源时间。
            source_format (str): The format of source time. 来源时间的格式。

        Returns:
            datetime
        """
        try:
            return_date = datetime.strptime(source_time, source_format)
        except Exception as ex:
            self.logger.info(f"格式时间转换失败(*>﹏<*)【{source_time}】")
            self.logger.info(f"格式时间失败原因(*>﹏<*)【{ex}】")
            return datetime.now()
        else:
            return return_date

    def format_to_custom(self, source_time: datetime = None, custom_days: float = 0,
                         custom_hours: float = 0, custom_minutes: float = 0,
                         custom_seconds: float = 0) -> datetime:
        """The format is different than the custom time. 格式与自定义的时间差日期。

        Args:
            source_time (datetime): The source time. 来源时间。
            custom_days (float): The difference in days. 计算天数差。
            custom_hours (float): The difference in hours. 计算小时差。
            custom_minutes (float): The difference in minutes. 计算分钟差。
            custom_seconds (float): The difference in seconds. 计算秒差。

        Returns:
            datetime
        """
        try:
            return_date = source_time + timedelta(
                days=custom_days, hours=custom_hours, minutes=custom_minutes, seconds=custom_seconds)
        except Exception as ex:
            self.logger.info(f"格式指定时间失败(*>﹏<*)【{source_time}】")
            self.logger.info(f"格式指定失败原因(*>﹏<*)【{ex}】")
            return datetime.now()
        else:
            return return_date

    def format_to_now(self, is_utc: bool = False, custom_days: float = 0, custom_hours: float = 0,
                        custom_minutes: float = 0, custom_seconds: float = 0) -> datetime:
        """The format is different than the current time. 格式与现在的时间差日期。
        
        Args:
            is_utc (bool): Whether it is utc time. 是否是UTC时间。
            custom_days (float): The difference in days. 计算天数差。
            custom_hours (float): The difference in hours. 计算小时差。
            custom_minutes (float): The difference in minutes. 计算分钟差。
            custom_seconds (float): The difference in seconds. 计算秒差。

        Returns:
            datetime
        """
        try:
            if is_utc:
                return_date = datetime.utcnow() + timedelta(
                    days=custom_days, hours=custom_hours, minutes=custom_minutes, seconds=custom_seconds)
            else:
                return_date = datetime.now() + timedelta(
                    days=custom_days, hours=custom_hours, minutes=custom_minutes, seconds=custom_seconds)
        except Exception as ex:
            self.logger.info(f"格式现在时差失败(*>﹏<*)【now】")
            self.logger.info(f"格式现在失败原因(*>﹏<*)【{ex}】")
            if is_utc:
                return datetime.utcnow()
            else:
                return datetime.now()
        else:
            return return_date

    def format_to_timestamp(self, source_stamp: str = "", divided: int = 1000) -> datetime:
        """Format timestamp to datetime. 格式时间戳日期。
        
        Args:
            source_stamp (str): The source stamp. 来源时间戳。
            divided (int): The source stamp divided. 来源时间除以的比率。

        Returns:
            datetime
        """
        if type(source_stamp) is not str or divided <= 0:
            self.logger.info(f"格式时戳参数有误(*>﹏<*)【{source_stamp}】")
            return datetime.now()
        try:
            date_string = re.findall("-?\d+", source_stamp, re.S)
            date_seconds = int(date_string[0]) / divided
            return_date = datetime(1970, 1, 1) + timedelta(seconds=date_seconds)
        except Exception as ex:
            self.logger.info(f"格式时戳时间失败(*>﹏<*)【{source_stamp}】")
            self.logger.info(f"格式时戳失败原因(*>﹏<*)【{ex}】")
            return datetime.now()
        else:
            return return_date

    def format_to_timezone(self, source_stamp: str = "", timezone: str = "", divided: int = 1000) -> datetime:
        """Format timezone to datetime. 格式时区日期。
        
        Args:
            source_stamp (str): The source stamp. 来源时间戳。
            timezone (str): Timezone. 时区。
            divided (int): The source stamp divided. 来源时间除以的比率。

        Returns:
            datetime
        """
        if type(source_stamp) is not str or type(timezone) is not str or divided <= 0:
            self.logger.info(f"格式时区参数有误(*>﹏<*)【{source_stamp}】")
            return datetime.now()
        try:
            date_string = re.findall("-?\d+", source_stamp, re.S)
            date_seconds = int(date_string[0]) / divided
            tz = pytz.timezone(timezone)
            return_date = datetime.fromtimestamp(date_seconds, tz)
        except Exception as ex:
            self.logger.info(f"格式时区时间失败(*>﹏<*)【{source_stamp}】")
            self.logger.info(f"格式时区失败原因(*>﹏<*)【{ex}】")
            return datetime.now()
        else:
            return return_date

    def format_to_utc(self, source_time: str = "") -> datetime:
        """Format utc to datetime. 格式格林时间日期。
        
        Args:
            source_time (str): The source time. 来源时间，2019-09-30T14:00:00+08:00。

        Returns:
            datetime
        """
        try:
            base_time = source_time[:-6]
            add_time = source_time[-6:]
            base_time = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
            custom_hours = int(add_time[1:3])
            custom_minutes = int(add_time[4:])
            if "+" in add_time:
                return_date = base_time + timedelta(hours=custom_hours, minutes=custom_minutes)
            else:
                return_date = base_time - timedelta(hours=custom_hours, minutes=custom_minutes)
        except Exception as ex:
            self.logger.info(f"格式格林时间失败(*>﹏<*)【{source_time}】")
            self.logger.info(f"格式格林失败原因(*>﹏<*)【{ex}】")
            return datetime.now()
        else:
            return return_date
