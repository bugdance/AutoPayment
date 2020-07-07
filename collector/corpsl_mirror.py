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
"""The mirror is use for store the data."""


class CorpSLMirror:
	"""SL镜像器，存储国籍对应编码。"""
	
	def __init__(self):
		self.logger: any = None  # 日志记录器。
		# # # 国家三字码
		self._country_code: dict = {
			"AND": "Andorra",
			"ATG": "Antigua",
			"ARG": "Argentina",
			"ARM": "Armenia",
			"ABW": "Aruba",
			"AUS": "Australia",
			"AUT": "Austria",
			"AZE": "Azerbaijan",
			"BHS": "Bahamas",
			"BHR": "Bahrain",
			"BGD": "Bangladesh",
			"BRB": "Barbados",
			"BLR": "Belarus",
			"BEL": "Belgium",
			"BMU": "Bermuda",
			"BOL": "Bolivia",
			"BIH": "Bosnia Herzegovina",
			"BWA": "Botswana",
			"BRA": "Brazil",
			"BRN": "Brunei",
			"BGR": "Bulgaria",
			"KHM": "Cambodia",
			"CMR": "Cameroon",
			"CAN": "Canada",
			"CYM": "Cayman Islands",
			"CHL": "Chile",
			"CHN": "China",
			"COL": "Colombia",
			"CRI": "Costa Rica",
			"HRV": "Croatia",
			"CUB": "Cuba",
			"CYP": "Cyprus",
			"CZE": "Czech Republic",
			"DNK": "Denmark",
			"DOM": "Dominican Republic",
			"ECU": "Ecuador",
			"EGY": "Egypt",
			"EST": "Estonia",
			"ETH": "Ethiopia",
			"FJI": "Fiji",
			"FIN": "Finland",
			"FRA": "France",
			"PYF": "French Polynesia",
			"GAB": "Gabon",
			"GEO": "Georgia",
			"DEU": "Germany",
			"GIB": "Gibraltar",
			"GRC": "Greece",
			"GRL": "Greenland",
			"GRD": "Grenada",
			"GLP": "Guadeloupe",
			"GUM": "Guam",
			"GTM": "Guatemala",
			"HND": "Honduras",
			"HKG": "Hong Kong",
			"HUN": "Hungary",
			"ISL": "Iceland",
			"IND": "India",
			"IDN": "Indonesia",
			"IRN": "Iran",
			"IRL": "Ireland(Republic of)",
			"ISR": "Israel",
			"ITA": "Italy",
			"JAM": "Jamaica",
			"JPN": "Japan",
			"JOR": "Jordan",
			"KAZ": "Kazakhstan",
			"KEN": "Kenya",
			"KWT": "Kuwait",
			"LAO": "Laos",
			"LVA": "Latvia",
			"LBN": "Lebanon",
			"LBY": "Libya",
			"LIE": "Liechtenstein",
			"LTU": "Lithuania",
			"LUX": "Luxembourg",
			"MAC": "Macau",
			"MKD": "Macedonia",
			"MYS": "Malaysia",
			"MDV": "Maldives",
			"MLT": "Malta",
			"MUS": "Mauritius",
			"MEX": "Mexico",
			"FSM": "Micronesia",
			"MDA": "Moldova",
			"MCO": "Monaco",
			"MNE": "Montenegro",
			"MAR": "Morocco",
			"MOZ": "Mozambique",
			"MMR": "Myanmar",
			"NAM": "Namibia",
			"NPL": "Nepal",
			"NLD": "Netherlands",
			"ANT": "Netherlands Antilles",
			"NCL": "New Caledonia",
			"NZL": "New Zealand",
			"NIC": "Nicaragua",
			"NGA": "Nigeria",
			"NFK": "Norfolk Island",
			"MNP": "Northern Mariana Island",
			"NOR": "Norway",
			"OMN": "Oman",
			"PAK": "Pakistan",
			"PLW": "Palau",
			"PAN": "Panama",
			"PRY": "Paraguay",
			"PER": "Peru",
			"PHL": "Philippines",
			"POL": "Poland",
			"PRT": "Portugal",
			"PRI": "Puerto Rico",
			"QAT": "Qatar",
			"ROU": "Romania",
			"RUS": "Russia",
			"WSM": "Samoa",
			"SMR": "San Marino (Republic of)",
			"MAF": "San Martin (F)",
			"SAU": "Saudi Arabia",
			"SEN": "Senegal",
			"SRB": "Serbia",
			"SYC": "Seychelles",
			"SGP": "Singapore",
			"SVK": "Slovakia",
			"SVN": "Slovenia",
			"ZAF": "South Africa",
			"KOR": "South Korea",
			"ESP": "Spain",
			"LKA": "Sri Lanka",
			"KNA": "St Kitts and Nevis",
			"LCA": "St Lucia",
			"VCT": "St Vincent & Grenadines",
			"SWZ": "Swaziland",
			"SWE": "Sweden",
			"CHE": "Switzerland",
			"SYR": "Syria",
			"TWN": "Taiwan",
			"TZA": "Tanzania",
			"THA": "Thailand",
			"TLS": "Timor-Leste (East Timor)",
			"TGO": "Togo",
			"TON": "Tonga",
			"TTO": "Trinidad & Tobago",
			"TUN": "Tunisia",
			"TUR": "Turkey",
			"TCA": "Turks & Caicos Island",
			"UKR": "Ukraine",
			"ARE": "United Arab Emirates",
			"GBR": "United Kingdom",
			"USA": "United States of America",
			"URY": "Uruguay",
			"UZB": "Uzbekistan",
			"VUT": "Vanuatu",
			"VEN": "Venezuela",
			"VNM": "Vietnam",
			"YEM": "Yemen Republic",
			"ZMB": "Zambia",
			"ZWE": "Zimbabwe",
		}
	
	def select_to_nationality(self, country_id: str = "") -> str:
		"""选择国籍
		:param country_id:  国家三字码
		:return:  str
		"""
		if not country_id or type(country_id) is not str:
			self.logger.info(f"选择国籍非法传参(*>﹏<*)【{country_id}】")
			return ""
		
		for k, v in self._country_code.items():
			if k == country_id:
				return k
		return "CHN"
	
	def select_to_country(self, country_name: str = "") -> str:
		"""选择国家
		:param country_name:  国家三字码
		:return:  str
		"""
		if not country_name or type(country_name) is not str:
			self.logger.info(f"选择国家非法传参(*>﹏<*)【{country_name}】")
			return ""
		
		for k, v in self._country_code.items():
			if v == country_name:
				return k
		return ""
