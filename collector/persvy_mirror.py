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


class PersVYMirror:
	"""VY镜像器，存储国籍对应编码。"""
	
	def __init__(self):
		self.logger: any = None  # 日志记录器。
	
	def select_to_name(self, station_code: str = "") -> str:
		"""选择机场名称。

		Args:
			station_code (str): 航站三字码。

		Returns:
			str
		"""
		stations = {
			"StationList": [{
				"macCode": "",
				"name": "A Coruña",
				"code": "LCG"
			}, {
				"macCode": "",
				"name": "Aalborg",
				"code": "AAL"
			}, {
				"macCode": "",
				"name": "Alghero",
				"code": "AHO"
			}, {
				"macCode": "",
				"name": "Algiers",
				"code": "ALG"
			}, {
				"macCode": "",
				"name": "Alicante",
				"code": "ALC"
			}, {
				"macCode": "",
				"name": "Almeria",
				"code": "LEI"
			}, {
				"macCode": "",
				"name": "Amsterdam",
				"code": "AMS"
			}, {
				"macCode": "",
				"name": "Asturias (Oviedo)",
				"code": "OVD"
			}, {
				"macCode": "",
				"name": "Athens",
				"code": "ATH"
			}, {
				"macCode": "",
				"name": "Banjul",
				"code": "BJL"
			}, {
				"macCode": "",
				"name": "Barcelona",
				"code": "BCN"
			}, {
				"macCode": "",
				"name": "Bari",
				"code": "BRI"
			}, {
				"macCode": "",
				"name": "Basel",
				"code": "BSL"
			}, {
				"macCode": "",
				"name": "Bastia (Corsica)",
				"code": "BIA"
			}, {
				"macCode": "",
				"name": "Beirut",
				"code": "BEY"
			}, {
				"macCode": "",
				"name": "Belgrade",
				"code": "BEG"
			}, {
				"macCode": "",
				"name": "Bergen",
				"code": "BGO"
			}, {
				"macCode": "",
				"name": "Berlin (Tegel)",
				"code": "TXL"
			}, {
				"macCode": "",
				"name": "Bilbao",
				"code": "BIO"
			}, {
				"macCode": "",
				"name": "Birmingham",
				"code": "BHX"
			}, {
				"macCode": "",
				"name": "Bologna",
				"code": "BLQ"
			}, {
				"macCode": "",
				"name": "Bordeaux",
				"code": "BOD"
			}, {
				"macCode": "",
				"name": "Brest",
				"code": "BES"
			}, {
				"macCode": "",
				"name": "Brindisi",
				"code": "BDS"
			}, {
				"macCode": "",
				"name": "Brussels",
				"code": "BRU"
			}, {
				"macCode": "",
				"name": "Bucharest",
				"code": "OTP"
			}, {
				"macCode": "",
				"name": "Budapest",
				"code": "BUD"
			}, {
				"macCode": "",
				"name": "Cagliari",
				"code": "CAG"
			}, {
				"macCode": "",
				"name": "Cardiff",
				"code": "CWL"
			}, {
				"macCode": "",
				"name": "Casablanca",
				"code": "CMN"
			}, {
				"macCode": "",
				"name": "Catania",
				"code": "CTA"
			}, {
				"macCode": "",
				"name": "Cluj-Napoca",
				"code": "CLJ"
			}, {
				"macCode": "",
				"name": "Copenhagen",
				"code": "CPH"
			}, {
				"macCode": "",
				"name": "Corfu",
				"code": "CFU"
			}, {
				"macCode": "",
				"name": "Crete",
				"code": "HER"
			}, {
				"macCode": "",
				"name": "Dakar",
				"code": "DKR"
			}, {
				"macCode": "",
				"name": "Dakar",
				"code": "DSS"
			}, {
				"macCode": "",
				"name": "Dresden",
				"code": "DRS"
			}, {
				"macCode": "",
				"name": "Dublin",
				"code": "DUB"
			}, {
				"macCode": "",
				"name": "Dubrovnik",
				"code": "DBV"
			}, {
				"macCode": "",
				"name": "Düsseldorf",
				"code": "DUS"
			}, {
				"macCode": "",
				"name": "Edinburgh",
				"code": "EDI"
			}, {
				"macCode": "",
				"name": "Eindhoven",
				"code": "EIN"
			}, {
				"macCode": "",
				"name": "Errachidia",
				"code": "ERH"
			}, {
				"macCode": "",
				"name": "Faro",
				"code": "FAO"
			}, {
				"macCode": "",
				"name": "Fez",
				"code": "FEZ"
			}, {
				"macCode": "",
				"name": "Florence",
				"code": "FLR"
			}, {
				"macCode": "",
				"name": "Fuerteventura",
				"code": "FUE"
			}, {
				"macCode": "",
				"name": "Geneva",
				"code": "GVA"
			}, {
				"macCode": "",
				"name": "Genoa",
				"code": "GOA"
			}, {
				"macCode": "",
				"name": "Gothenburg",
				"code": "GOT"
			}, {
				"macCode": "",
				"name": "Gran Canaria",
				"code": "LPA"
			}, {
				"macCode": "",
				"name": "Granada",
				"code": "GRX"
			}, {
				"macCode": "",
				"name": "Hamburg",
				"code": "HAM"
			}, {
				"macCode": "",
				"name": "Hanover",
				"code": "HAJ"
			}, {
				"macCode": "",
				"name": "Helsinki",
				"code": "HEL"
			}, {
				"macCode": "",
				"name": "Ibiza",
				"code": "IBZ"
			}, {
				"macCode": "",
				"name": "Jerez (Cádiz)",
				"code": "XRY"
			}, {
				"macCode": "",
				"name": "Kaliningrad",
				"code": "KGD"
			}, {
				"macCode": "",
				"name": "Karpathos",
				"code": "AOK"
			}, {
				"macCode": "",
				"name": "Kefalonia",
				"code": "EFL"
			}, {
				"macCode": "",
				"name": "Kiev",
				"code": "IEV"
			}, {
				"macCode": "",
				"name": "Kiev",
				"code": "KBP"
			}, {
				"macCode": "",
				"name": "Kos",
				"code": "KGS"
			}, {
				"macCode": "",
				"name": "Krakow",
				"code": "KRK"
			}, {
				"macCode": "",
				"name": "La Palma",
				"code": "SPC"
			}, {
				"macCode": "",
				"name": "Lampedusa",
				"code": "LMP"
			}, {
				"macCode": "",
				"name": "Lanzarote",
				"code": "ACE"
			}, {
				"macCode": "",
				"name": "Larnaca",
				"code": "LCA"
			}, {
				"macCode": "",
				"name": "Lille",
				"code": "LIL"
			}, {
				"macCode": "",
				"name": "Lisbon",
				"code": "LIS"
			}, {
				"macCode": "",
				"name": "Liverpool",
				"code": "LPL"
			}, {
				"macCode": "LON",
				"name": "London (Gatwick)",
				"code": "LGW"
			}, {
				"macCode": "LON",
				"name": "London (Heathrow)",
				"code": "LHR"
			}, {
				"macCode": "LON",
				"name": "London (Luton)",
				"code": "LTN"
			}, {
				"macCode": "",
				"name": "Luxembourg",
				"code": "LUX"
			}, {
				"macCode": "",
				"name": "Lyon",
				"code": "LYS"
			}, {
				"macCode": "",
				"name": "Madeira",
				"code": "FNC"
			}, {
				"macCode": "",
				"name": "Madrid",
				"code": "MAD"
			}, {
				"macCode": "",
				"name": "Majorca",
				"code": "PMI"
			}, {
				"macCode": "",
				"name": "Malaga",
				"code": "AGP"
			}, {
				"macCode": "",
				"name": "Malta",
				"code": "MLA"
			}, {
				"macCode": "",
				"name": "Manchester",
				"code": "MAN"
			}, {
				"macCode": "",
				"name": "Marrakech",
				"code": "RAK"
			}, {
				"macCode": "",
				"name": "Marseille",
				"code": "MRS"
			}, {
				"macCode": "",
				"name": "Menorca",
				"code": "MAH"
			}, {
				"macCode": "",
				"name": "Milan",
				"code": "MXP"
			}, {
				"macCode": "",
				"name": "Milan-Bergamo",
				"code": "BGY"
			}, {
				"macCode": "",
				"name": "Minsk",
				"code": "MSQ"
			}, {
				"macCode": "",
				"name": "Montpellier-Méditerranée",
				"code": "MPL"
			}, {
				"macCode": "MOW",
				"name": "Moscow (Domodedovo)",
				"code": "DME"
			}, {
				"macCode": "",
				"name": "Munich",
				"code": "MUC"
			}, {
				"macCode": "",
				"name": "Murcia",
				"code": "RMU"
			}, {
				"macCode": "",
				"name": "Mykonos",
				"code": "JMK"
			}, {
				"macCode": "",
				"name": "Nador",
				"code": "NDR"
			}, {
				"macCode": "",
				"name": "Nantes",
				"code": "NTE"
			}, {
				"macCode": "",
				"name": "Naples",
				"code": "NAP"
			}, {
				"macCode": "",
				"name": "Nice",
				"code": "NCE"
			}, {
				"macCode": "",
				"name": "Nuremberg",
				"code": "NUE"
			}, {
				"macCode": "",
				"name": "Olbia",
				"code": "OLB"
			}, {
				"macCode": "",
				"name": "Oran",
				"code": "ORN"
			}, {
				"macCode": "",
				"name": "Oslo",
				"code": "OSL"
			}, {
				"macCode": "",
				"name": "Palermo",
				"code": "PMO"
			}, {
				"macCode": "",
				"name": "Pamplona",
				"code": "PNA"
			}, {
				"macCode": "PAR",
				"name": "Paris (Charles de Gaulle)",
				"code": "CDG"
			}, {
				"macCode": "PAR",
				"name": "Paris (Orly)",
				"code": "ORY"
			}, {
				"macCode": "",
				"name": "Pisa (Tuscany)",
				"code": "PSA"
			}, {
				"macCode": "",
				"name": "Porto",
				"code": "OPO"
			}, {
				"macCode": "",
				"name": "Prague",
				"code": "PRG"
			}, {
				"macCode": "",
				"name": "Preveza",
				"code": "PVK"
			}, {
				"macCode": "",
				"name": "Rennes",
				"code": "RNS"
			}, {
				"macCode": "",
				"name": "Reykjavík",
				"code": "KEF"
			}, {
				"macCode": "",
				"name": "Rhodes",
				"code": "RHO"
			}, {
				"macCode": "",
				"name": "Rimini",
				"code": "RMI"
			}, {
				"macCode": "",
				"name": "Rome (Fiumicino)",
				"code": "FCO"
			}, {
				"macCode": "",
				"name": "Rotterdam",
				"code": "RTM"
			}, {
				"macCode": "",
				"name": "San Sebastian",
				"code": "EAS"
			}, {
				"macCode": "",
				"name": "Santander",
				"code": "SDR"
			}, {
				"macCode": "",
				"name": "Santiago",
				"code": "SCQ"
			}, {
				"macCode": "",
				"name": "Santorini",
				"code": "JTR"
			}, {
				"macCode": "",
				"name": "Seville",
				"code": "SVQ"
			}, {
				"macCode": "",
				"name": "Split",
				"code": "SPU"
			}, {
				"macCode": "",
				"name": "St. Petersburg",
				"code": "LED"
			}, {
				"macCode": "",
				"name": "Stockholm",
				"code": "ARN"
			}, {
				"macCode": "",
				"name": "Stuttgart",
				"code": "STR"
			}, {
				"macCode": "",
				"name": "Tallinn",
				"code": "TLL"
			}, {
				"macCode": "",
				"name": "Tangier",
				"code": "TNG"
			}, {
				"macCode": "",
				"name": "Tel Aviv",
				"code": "TLV"
			}, {
				"macCode": "TCI",
				"name": "Tenerife North",
				"code": "TFN"
			}, {
				"macCode": "TCI",
				"name": "Tenerife South",
				"code": "TFS"
			}, {
				"macCode": "",
				"name": "Thessaloniki",
				"code": "SKG"
			}, {
				"macCode": "",
				"name": "Toulouse",
				"code": "TLS"
			}, {
				"macCode": "",
				"name": "Tunis",
				"code": "TUN"
			}, {
				"macCode": "",
				"name": "Turin",
				"code": "TRN"
			}, {
				"macCode": "",
				"name": "Valencia",
				"code": "VLC"
			}, {
				"macCode": "",
				"name": "Valladolid",
				"code": "VLL"
			}, {
				"macCode": "",
				"name": "Venice",
				"code": "VCE"
			}, {
				"macCode": "",
				"name": "Verona",
				"code": "VRN"
			}, {
				"macCode": "",
				"name": "Vienna",
				"code": "VIE"
			}, {
				"macCode": "",
				"name": "Vigo",
				"code": "VGO"
			}, {
				"macCode": "",
				"name": "Warsaw",
				"code": "WAW"
			}, {
				"macCode": "",
				"name": "Zadar",
				"code": "ZAD"
			}, {
				"macCode": "",
				"name": "Zagreb",
				"code": "ZAG"
			}, {
				"macCode": "",
				"name": "Zakynthos",
				"code": "ZTH"
			}, {
				"macCode": "",
				"name": "Zaragoza",
				"code": "ZAZ"
			}, {
				"macCode": "",
				"name": "Zurich",
				"code": "ZRH"
			}, {
				"macCode": "",
				"name": "BRNO (BRQ)",
				"code": "BRQ"
			}, {
				"macCode": "",
				"name": "GRAZ (GRZ)",
				"code": "GRZ"
			}, {
				"macCode": "",
				"name": "Buenos Aires",
				"code": "EZE"
			}, {
				"macCode": "",
				"name": "Boston",
				"code": "BOS"
			}, {
				"macCode": "",
				"name": "Fort de France",
				"code": "FDF"
			}, {
				"macCode": "",
				"name": "Los Angeles",
				"code": "LAX"
			}, {
				"macCode": "NYC",
				"name": "New York (Newark)",
				"code": "EWR"
			}, {
				"macCode": "",
				"name": "Montreal",
				"code": "YUL"
			}, {
				"macCode": "",
				"name": "Oakland San Francisco Bay",
				"code": "OAK"
			}, {
				"macCode": "",
				"name": "Pointe-à-Pitre",
				"code": "PTP"
			}, {
				"macCode": "",
				"name": "San Francisco",
				"code": "SFO"
			}, {
				"macCode": "",
				"name": "LYON/GRENOBLE ST GEOIRS (GNB)",
				"code": "GNB"
			}, {
				"macCode": "",
				"name": "OUARZAZATE (OZZ)",
				"code": "OZZ"
			}, {
				"macCode": "LON",
				"name": "LONDON STANSTED (STN)",
				"code": "STN"
			}, {
				"macCode": "",
				"name": "STRASBOURG (SXB)",
				"code": "SXB"
			}, {
				"macCode": "",
				"name": "TRIESTE (TRS)",
				"code": "TRS"
			}, {
				"macCode": "",
				"name": "GRONINGEN (GRQ)",
				"code": "GRQ"
			}, {
				"macCode": "",
				"name": "NEWCASTLE (NCL)",
				"code": "NCL"
			}, {
				"macCode": "",
				"name": "ANTALYA (AYT)",
				"code": "AYT"
			}, {
				"macCode": "",
				"name": "FRANKFURT (FRA)",
				"code": "FRA"
			}, {
				"macCode": "",
				"name": "LEEDS BRADFORD (LBA)",
				"code": "LBA"
			}, {
				"macCode": "",
				"name": "COLOGNE/BONN (CGN)",
				"code": "CGN"
			}, {
				"macCode": "NYC",
				"name": "New York",
				"code": "JFK"
			}, {
				"macCode": "",
				"name": "LOURDES (LDE)",
				"code": "LDE"
			}, {
				"macCode": "",
				"name": "Santiago de Chile",
				"code": "SCL"
			}, {
				"macCode": "",
				"name": "BILLUND (BLL)",
				"code": "BLL"
			}, {
				"macCode": "",
				"name": "Calvi",
				"code": "CLY"
			}, {
				"macCode": "",
				"name": "Linz",
				"code": "LNZ"
			}, {
				"macCode": "",
				"name": "Salzburg",
				"code": "SZG"
			}, {
				"macCode": "",
				"name": "BANGKOK (BKK)",
				"code": "BKK"
			}, {
				"macCode": "",
				"name": "BRATISLAVA (BTS)",
				"code": "BTS"
			}, {
				"macCode": "",
				"name": "O.R. Tambo International Airport",
				"code": "JNB"
			}, {
				"macCode": "",
				"name": "Las Vegas",
				"code": "LAS"
			}, {
				"macCode": "",
				"name": "Punta Cana Airport",
				"code": "PUJ"
			}, {
				"macCode": "",
				"name": "Rostock",
				"code": "RLG"
			}, {
				"macCode": "",
				"name": "SKOPJE (SKP)",
				"code": "SKP"
			}, {
				"macCode": "",
				"name": "S Eufemia Airport",
				"code": "SUF"
			}, {
				"macCode": "",
				"name": "TIRANA (TIA)",
				"code": "TIA"
			}, {
				"macCode": "",
				"name": "Aulnat Airport",
				"code": "CFE"
			}, {
				"macCode": "",
				"name": "Allgaeu Airport",
				"code": "FMM"
			}, {
				"macCode": "",
				"name": "Hurghada Airport",
				"code": "HRG"
			}, {
				"macCode": "",
				"name": "Brnik Airport",
				"code": "LJU"
			}, {
				"macCode": "",
				"name": "RIGA (RIX)",
				"code": "RIX"
			}, {
				"macCode": "",
				"name": "Golubovci Airport",
				"code": "TGD"
			}, {
				"macCode": "",
				"name": "Tivat Airport",
				"code": "TIV"
			}]
		}
		
		if type(station_code) is not str:
			self.logger.info(f"选择名称参数有误(*>﹏<*)【{station_code}】")
			return ""
		
		for k, v in enumerate(stations['StationList']):
			if v['code'] == station_code:
				return v.get('name')
			
		self.logger.info(f"选择名称参数有误(*>﹏<*)【{station_code}】")
		return ""
