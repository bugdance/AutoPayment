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
"""The refactor is use for refactoring code."""
from accessor.request_crawler import RequestCrawler
from accessor.selenium_crawler import SeleniumCrawler
from booster.aes_formatter import AESFormatter
from booster.basic_formatter import BasicFormatter
from booster.basic_parser import BasicParser
from booster.callback_formatter import CallBackFormatter
from booster.callin_parser import CallInParser
from booster.date_formatter import DateFormatter
from booster.dom_parser import DomParser


class RCRefactor(RequestCrawler):
	"""重构爬行器。"""
	pass


class SCRefactor(SeleniumCrawler):
	"""重构爬行器。"""
	pass


class AFRefactor(AESFormatter):
	"""重构格式器。"""
	pass


class BFRefactor(BasicFormatter):
	"""重构格式器。"""
	pass


class BPRefactor(BasicParser):
	"""重构解析器。"""
	pass


class CFRefactor(CallBackFormatter):
	"""重构格式器。"""
	pass


class CPRefactor(CallInParser):
	"""重构解析器。"""
	pass


class DFRefactor(DateFormatter):
	"""重构格式器。"""
	pass


class DPRefactor(DomParser):
	"""重构解析器。"""
	pass