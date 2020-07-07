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
"""The scraper is use for website process interaction."""
from accessor.request_worker import RequestWorker
from accessor.request_crawler import RequestCrawler
from booster.aes_formatter import AESFormatter
from booster.basic_formatter import BasicFormatter
from booster.basic_parser import BasicParser
from booster.callback_formatter import CallBackFormatter
from booster.callin_parser import CallInParser
from booster.date_formatter import DateFormatter
from booster.dom_parser import DomParser


class PersWNScraper(RequestWorker):
    """WN采集器，WN网站流程交互，WN无行李，4小时刷header，1天失效。"""
    
    def __init__(self) -> None:
        RequestWorker.__init__(self)
        self.RCR = RequestCrawler()  # 请求爬行器。
        self.AFR = AESFormatter()  # AES格式器。
        self.BFR = BasicFormatter()  # 基础格式器。
        self.BPR = BasicParser()  # 基础解析器。
        self.CFR = CallBackFormatter()  # 回调格式器。
        self.CPR = CallInParser(False)  # 接入解析器。
        self.DFR = DateFormatter()  # 日期格式器。
        self.DPR = DomParser()  # 文档解析器。
        # # # 过程中重要的参数。
        self.base_header: dict = {}
        self.air_data: dict = {}
        # # # 返回中用到的变量。
        self.total_price: float = 0.0  # 总价。
        self.return_price: float = 0.0  # 返回价格。
        self.baggage_price: float = 0.0  # 行李总价。
        self.record: str = ""  # 票号。

    def init_to_assignment(self) -> bool:
        """Assignment to logger. 赋值日志。

		Returns:
			bool
		"""
        self.RCR.logger = self.logger
        self.AFR.logger = self.logger
        self.BFR.logger = self.logger
        self.BPR.logger = self.logger
        self.CFR.logger = self.logger
        self.CPR.logger = self.logger
        self.DFR.logger = self.logger
        self.DPR.logger = self.logger
        return True

    def process_to_main(self, process_dict: dict = None) -> dict:
        """Main process. 主程序入口。

		Args:
			process_dict (dict): Parameters. 传参。

		Returns:
			dict
		"""
        task_id = process_dict.get("task_id")
        log_path = process_dict.get("log_path")
        source_dict = process_dict.get("source_dict")
        enable_proxy = process_dict.get("enable_proxy")
        address = process_dict.get("address")
        self.retry_count = process_dict.get("retry_count")
        if not self.retry_count:
            self.retry_count = 1
        # # # 初始化日志。
        self.init_to_logger(task_id, log_path)
        self.init_to_assignment()
        # # # 同步返回参数。
        self.callback_data = self.CFR.format_to_sync()
        # # # 解析接口参数。
        if not self.CPR.parse_to_interface(source_dict):
            self.callback_data['msg'] = "请通知技术检查接口数据参数。"
            return self.callback_data
        self.logger.info(source_dict)
        # # # 启动爬虫，建立header。
        self.RCR.set_to_session()
        self.RCR.set_to_proxy(enable_proxy, address)
        self.user_agent, self.init_header = self.RCR.build_to_header("none")
        self.CPR.currency = "USD"
        # # # 主体流程。
        if self.process_to_index(max_count=self.retry_count):
            if self.process_to_query(max_count=self.retry_count):
                if self.process_to_service(max_count=self.retry_count):
                    if self.process_to_payment(max_count=self.retry_count):
                        self.process_to_return()
                        self.logger.removeHandler(self.handler)
                        return self.callback_data
        # # # 错误返回。
        self.callback_data['msg'] = self.callback_msg
        # self.callback_data['msg'] = "解决问题中，请手工支付。"
        self.logger.info(self.callback_data)
        self.logger.removeHandler(self.handler)
        return self.callback_data

    def process_to_index(self, count: int = 0, max_count: int = 1) -> bool:
        """Index process. 首页过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 更新超时时间。
            self.RCR.timeout = 10
            # # # 请求接口服务。
            self.RCR.url = 'http://45.81.129.1:33334/produce/wn/'
            self.RCR.param_data = None
            self.RCR.header = None
            self.RCR.post_data = {"wn": "header"}
            if not self.RCR.request_to_post("json", "json"):
                self.logger.info(f"请求刷值地址失败(*>﹏<*)【45.81.129.1:33334】")
                self.callback_msg = "请求刷值地址失败，请通知技术检查程序。"
                return self.process_to_index(count + 1, max_count)
            # # # 获取abck。
            value = self.RCR.page_source.get("value")
            if not value:
                self.logger.info(f"刷值数量不够用(*>﹏<*)【45.81.129.1:33334】")
                self.callback_msg = "刷值数量不够用，请通知技术检查程序。"
                return self.process_to_index(count + 1, max_count)
            # # # 重新整理header
            # value = """{'origin': 'https://www.southwest.com', 'x-user-experience-id': 'b9bba821-03bc-42eb-88c6-3f2219f9612c', 'ee30zvqlwf-z': 'p', 'authorization': 'null null', 'ee30zvqlwf-b': '-a85t6z', 'x-api-idtoken': 'null', 'ee30zvqlwf-d': 'o_0', 'ee30zvqlwf-c': 'A9U5PmdwAQAAV7ZI2B6meSA3lJWxBINCT7-SX12Lwuhl-eaTX7EHn5McL-v_AUkiz9qcwlFBwH99t4LqosJ9tw==', 'ee30zvqlwf-f': 'A9trPmdwAQAAa33T5JjKoSQDZ0fEHd1rLoOI9a0D6Ss6nCbUqNsx_qvjoHgQAWUWO1CuctuUwH8AAEB3AAAAAA==', 'x-channel-id': 'southwest', 'ee30zvqlwf-a': 'QwphA2bE9H4NILxi=t5q_dLda6hUxwwG6X2ue00mObGn-B1lO58AxB8_kNZ4zh_nbUnOV_cjcb0uMrCjsc-MeChx2=nE1rA16G78i8hBz4XwlkZ=2GpAlmoPBykR5F4IQeVrPA_7ONrvexLOm_sGcHUhtEK3fSO=ilLSFeqhHHVlyJ4u3Kdaxkg9r4799iiPSfqR=HAsuS3QwDv0CE-U49-EVhKotXY1gqO4uAzrNolD_dAuHGLH3PO9EKUgTmDM-eXNSI55LFeazzvPRsbrc6C-Q72Il3=oMndgZBQCq5Y5AAm_9NZDyf6IG=w=AXgo=TXGFjf-K0h-P-JvlwA_HvaoC08gvKsRLfVRM0Cvjo-AdC4IE-vde69D296U18mMISsR=r_Qp-EEqODkoO3ZwZTlf5SXtb8djaCusKqwPNwGiDApOqBNxpoEHCCJOqbGs0pszv4omKwKJHQMP=Dsgi215_BoAH8r-g6zaNcsrYjdGLuodG7S_2_O-Aw94hLVAzjFgD3t4wAx0fb1CFQ9N9mg=Iq-iQbFAbotTGki=4vF9ndJ2P=360d_lkmVB2RIK=zJnL7rF=MTp_n_6eVKpyYBfUrhhBIUGblavTK9srnKZ9E3qODPjimL5NQjfpYVb96Ch7Dz53cSC9Hn=FkIINq7QaseU5EP49kj=5ceobHQ2lySuCdxes99UP8C2En6vVO2mpI-iHfz0jUOjXSfMysQzKwJAnzdeMEMUMC=qom6rFAQ9=6at9jOepeomtFrRKeOjc0emFT0=qQ-9A=M1OUy7AY02smNgUHBwoH8o_4lrYfjOcDGsi2ztpyA317LQ5SEpIqg_a7_1e0KUPPSX8n9N67KqvYcnqk0__4Rn4k6Ms4r4=JeqBntnI5_6m7VH4J0ZHRrXvbu9a0YPILZZjuuhOGirthHsUa4PZjk5seybqQc73UqDQRVn5hcrry7=n6hReFccR7CjejZhNBNGp6lydGvYSg9JonlGmVe=k1qnbn6nCf07jDL-OGCVhquSZS5o5Vjt3-ZNdTd7jzbdJ-gZxIcoH7RzqiZv0ieoj8iL-06yAsqHRlrZTPJwwtYtIor6yJiXPqfYF3K7wrSaEtHelKTkR63I7OvJDCVTyExeo8NQ7D9Y7TkNV7HigEkDtR12g0NhLDy=REPa4fVTV5MtSTeQHHOzbg4pkXUE53_QojShO0RSCF7kFtHl6trGBH935HHn9MHZaPAYnbELsI5SlVXLHdcd_NopbgsDSO5V-c9qcMIQygrndhTe0ei6AC==R53rsk3cj3hr5wigYhFYgd2=spItCysTn6fw1SV=Kp5GNDKwJLIbpirTYjtqJy6jfgqrrlP2liO7RpE88k-VvXOXQtD5ZKMi8P7w2fLu6wSBJcQGxooruL-9PrnQzaitGX_1LlPh1ll=MzV20j6zSzwroZTYbFV4aRz=5ci95mjmsAlgQNkZiXpGsx=LHDjpIiAu2AG2vyZN_2iXKdTB2y9J3Lh75JkCkKF6YPZzp6DKg8wPTDO9=T2CmUM0ZhYC_B_v_8-d0i0lEIu4-8vzQKG-Hwr9h2vqwydPVuwlRzIT88NCV2kSQf-9vlRchkaa=T0J-Hlh-RcPR0wBmGj9yhSftdM2Sy04bJzFJOvukizOOPcFEhxKqwGsER5PpKHhqIJ9agFvKdjD8whkEk_XHHmrZYqJCX7RxCM0p1VK30a9VXloB4MX7clkCaAqegGJnZOH5Lmca6gVTilxHa4JMrl2_7-eSp_1jwf-71fiyZKbwpFwMIe=YE2-n8UmLv7GbrCg3TJrduXDvea4H7D6SHtbfLjwdXqXw1jPydiAjyku9SdlR=msteKpt-ptb8nwDIJeCcQVchBa7UjkLZJyJcc9KCr=NGYiFtKBkl7wCo54=cuAnpRQITAnGxV2C6UT1Gf3shdqQgzirHTZozGarSvR5RbCxDrvfVtobfa_3OzAMLd2oJKnmGiKvY8Op8IlScAH=Tde0y9R6jITcI1=_bicIYZS9AC_sTvXldRDJYX=pU3Y5pfErhiDtvth_VSyBR0Gl-ufN8m9stzNSy2dAcACOwbsdjnPGBevn0hxxQKdj-GDQLiS6RnPXPZizArDd=xCN-VMfK_yV_m3N3l67hJAnN3yHB977QwJt4-iHxdppDKZ6km1hRLFqJ176b6VafLj3XpV3OyTyBpqgNYbiMUgu4BNLGPcOU1YHQIhKRzG3YM7fhe7cKbdbFyKwZ-0CQiINKClb2uSsJuaoSoSq9Nue42gij5XLD6jq7_t=yO8a4HAnh2anVKewJ4Z-s4KEpU1jj1wOnNfcjPeoJI9pett_84wu2UyhMwRDnQR0FSDsSCCeefvoctuZlwzbGobjsK1=5hKwG6F55TvZ_D3BD4ZtYpIyoH48J_x7oA2lwzNmqM2YnC9sbGJnBDSoA7k9orN5A-NMabAmV1GQTaPxS7mf_ShMLRVsPZFvuw=ZgjM6jxPZ3Vi1k6686qlHfEJKvaPJxqjlQxMVhcDpN_80ZqOYGfrZF4cypTOhPUHVlZdJLujpPGe60TNmIrmBgUrT4vMyUC_kqCNKtArkeMKDAuD-9NYXAJGj2iie_N2yC3KwId8su_Si5gembQY=-8Lf-R20Q9mTdQJyABqMMZiha9RtJkrmyRKLRBMaelbuiKID_-KTa8hMR_-Mx2aSFKHnIDULg7c82L6s84P0kTd6LwOYE5nuFv_ngAKmbNfyy8H-tKj6M2bz=PXTx_YjbMHvkUANKCB3c25GNgvJb4RbefHioSGn3JEhQtvm3_2FGEnxaRXFTi6uLi06hQ-SUyeLmZGSdcj-Ce2O04Hq6NzUnKA-GejK3P4afOYqp1KITYV2fI-A7N25DrendNUnHpbyNOMx7ngwa-7SXpDTbee577NryUp1bpFdOSIxgpdOaK1==a=TP9cJ_SnMiiK2Dj-V=Eivg49hJkVijo03ok7Q-u9CsEpS2TjgyrJCwMSFPQriwpB0=ukbuhhvo6q8Bj5eqfli7mzTXYyFQPJ_myhwlSH-E82uxI0SijCLF67s7AEvDTOt4_HTEH5JSD74RyPNmaJhQPUzx=RlcTqj23pZgmYsab1OkZCDvdF_71j6yEXiVjYun=0Mmz3YvI0svUiC2R62evB1rDsjhma4Un0SUP3KOc8ZaJVr5OimBMLwQID0tKEBVGCONAEvbP7Qd=yvmT23LzgrgK3Gdc3VNxxN-BE37gi0qaxgRhxiUOU07u5dgYu2dXiAkEp-VHzAJ3k8dZU9EObVKj86YxIV8cI4xkL72Gqs6mBgeT6M2PB8-0TLET148D4PQF59TU0-=0tQpnD-CtbiKz9=3CCzludu6hPBxzyAJQhhvEBf2agb2rzrRR_ps8wAMtNgXOE=9mEO=Sb1R1_nlYi2ifDYxCrw26OXRSYGSg3zh_m8vKhmTYnH9vztucvF6ghoz3pqt9bTUh3U6Oeyxs4xr0tQETs22nm7SuUYnFD4Od=BDER100CKQDSzCi3sLI-_B0yXqTZhucdNuvU6DpEgmqooXYOEB9IgqNd0xRTX9A_bBXys67htoDjxs9NQdRLN=GbOevrDdTH=iimkRMLIdR9Mh9eUMSZ2JHGnaV2K0GLSQMN=kE8MHyjp5xl0qo9co7O7Vu1jS9cKHyPLEUBn-s5zL0m6Xs09dzxfrjzU8xotfQFKIQ0TCHO5ionJkeFB4Fr6hDHiOSo--lkNVZxUOQjgOse9IeckhBuQjCelpXOw6fz5NxFMQx=n9ERH0RYZMUsDf6_O5VnJPk=VZ897bD5Y7wcLxowZV3-8LUnTQ9yb8FZQjHuJItmZRrHMTlqLDruUs9UT=lsHheCOT17xEy73dHoqqXlwn0Y=5i7GVUPBUiIByj2OT=3Ojb2pOVDFXlkB_zF7PZ0lB-xirBJ=cSMeEMB04912xm2Pv=s_-ioAqMoee1w0i04pfSGVE2q6z8conQsG2NbVLU68BChaN16LNxCM6_xqTtQ1RoQCnbh-72s6bdDP2nNgXLLf9GCltZNot1uvAEkmszq=cGM1dosoUAY_F-noi=CNjQJLyPnvc1tygGZlm=bE9X=Y_ZUCBUemJRkXq=Xgg5PjyuZuO9e-cIQFQ4VEoLJJjc2EpgOr5eszpOoqHEahvNMgoKtqEiqzYHynS19N=5CQAVPVnEtLERu-f1X=6org8_l_g_B7zHumu4iB85-TSO1C_upyf83lnpYEK7R9=CNPEH2w4Gs4zaPGP27k7mkzVcOM-tUxLlFB6oKNbqBfi6Obx=O7-g6fVjXz8OsdMnKYXXO5nBgrY4EJKj=XQAitqoVBj3aDbjAV2kJ84tDh59Z0oo0pQR63N_MdRruQ5Ddi=6fF16euFBAzCNKEOusu=CZTY-6dIpoHfNmIZoq5dNmPjyH8wGJYxKeFrxuie8BxU1GwSbNTv4r79k4oZTRsSKRuifemJdCEkHuZpTnvjrxBZUrbmcr6Py8rgjGUxsXQoF6OKD87Qu5bzy8u9qgpI4rKr5Xz07N5c1c1MSFRDNgmMOhjp8UCIQU9gg5nNB=veFghYi_c-BLeNFNbfKQsOPmaKwnDjhX8sNcYHER1gQ1Ru0HVG7Cshi=mT4uVPQju2CXHQz-zaY3PiEy_-uYyz3r5rlqSwheLu8bvYcv-XONnY-ocNZ4hOI9HPz2AcwTVgdlHLgm4avbDoD5k=phBkZ5SaG3FoBRCmuPDbJsV1uCqr3mGDBsraY13A5tB0VNA48Sly8Ky3f=23Ero26ISc24cKqsAaoy5k5VQcN2PmNvd4-3LvGkFHiEZcFo3QmNnclVN3udopAHk-mSmNbI2usRfazo6277K1lmYsVkUZlDker0y36A6wgbuPdir3nd9FRz30fnlAMCQpmvULnn46TTYwEGut-9bfQHIltHFtLcdYjbc7T6JEZ_C=TU-LEN=Md65VNcUi9cXt8LNQPlt8lFYgGGCFrjEKYKdq5sxQjM2-', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3494.0 Safari/537.36', 'content-type': 'application/json', 'accept': 'application/json, text/javascript, */*; q=0.01', 'x-api-key': 'l7xx944d175ea25f4b9c903a583ea82a1c4c', 'cookie': 'sRpK8nqm_sc=At9rPmdwAQAA9RNQsLB6K26Qpo-4yegyh3B0aLYKc_BMedaFqwAAAXBnPmveAUrFyK0|1|0|8d6c1c596ea459773908d4da1b7eca8dec565c0d; check=true; sRpK8nqm_dc=%7B%22c%22%3A%20%22STRzNXNzV3JnZ0VWc05Idg%3D%3D858dXftyV_PtukQLyulHWbxlXsuCBWNGtFxUT1QxVUGfcR-EwH7SAISR1f9MXGFXB5Ex4yEKb-_-H263-Ax7oggTzDYPtXLwGF7ckcdF_frWsEQ%3D%22%2C%20%22dc%22%3A%20%22000%22%2C%20%22mf%22%3A%200%7D; mbox=session#07b1eda23218493e902117ca558700a9#1582281975|PC#07b1eda23218493e902117ca558700a9.22_0#1645524915; RT="z=1&dm=southwest.com&si=e466c953-62dc-427a-84c6-b4a6b0cf4351&ss=k6w0q0p6&sl=1&tt=5gn&bcn=%2F%2F684d0d3f.akstat.io%2F&ld=6be"; AMCVS_65D316D751E563EC0A490D4C%40AdobeOrg=1; s_gpv_pn=BOOK%3AAIR%3APlan%20Trip%20Page; akavpau_prod_fullsite=1582280164~id=e4fea15068b71a1f3278db644aa03565; s_cc=true; AMCV_65D316D751E563EC0A490D4C%40AdobeOrg=1075005958%7CMCIDTS%7C18314%7CMCMID%7C90443555500049589776449803505604604114%7CMCAID%7CNONE%7CMCOPTOUT-1582287316s%7CNONE%7CMCAAMLH-1582884936%7C11%7CMCAAMB-1582884936%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CvVersion%7C4.4.1', 'referer': 'https://www.southwest.com/air/booking/index.html'}"""
            self.base_header = self.BPR.parse_to_eval(value)
            if self.base_header:
                self.base_header['referer'] = ""
                self.base_header['user-agent'] = ""
                self.base_header['cookie'] = ""
                self.base_header.pop("referer")
                self.base_header.pop("user-agent")
                self.base_header.pop("cookie")
            self.RCR.timeout = 25
            # # # 爬取首页
            self.RCR.url = 'https://www.southwest.com/'
            self.RCR.param_data = None
            self.RCR.header = self.BFR.format_to_same(self.init_header)
            self.RCR.header.update({
                "Host": "www.southwest.com",
                "Upgrade-Insecure-Requests": "1",
            })
            self.RCR.post_data = None
            if self.RCR.request_to_get():
                flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
                flight_date = flight_date.strftime("%Y-%m-%d")
                query = (
                    ("int", "HOMEQBOMAIR"), ("adultPassengersCount", self.CPR.adult_num + self.CPR.child_num),
                    ("departureDate", flight_date), ("destinationAirportCode", self.CPR.arrival_code),
                    ("fareType", "USD"),
                    ("originationAirportCode", self.CPR.departure_code), ("passengerType", "ADULT"),
                    ("returnDate", ""), ("seniorPassengersCount", "0"),
                    ("tripType", "oneway"), ("departureTimeOfDay", "ALL_DAY"), ("reset", "true"),
                    ("returnTimeOfDay", "ALL_DAY"),
                )
                query_url = self.BPR.parse_to_url(query)

                # # # 解析查询页
                self.RCR.url = "https://www.southwest.com/air/booking/select.html"
                self.RCR.param_data = query
                self.RCR.header = self.BFR.format_to_same(self.init_header)
                self.RCR.header.update({
                    "Host": "www.southwest.com",
                    "Referer": "https://www.southwest.com/",
                    "Upgrade-Insecure-Requests": "1",
                })
                self.RCR.post_data = None
                if self.RCR.request_to_get():
                    self.RCR.url = 'https://www.southwest.com/api/air-booking/v1/air-booking/page/air/booking/shopping'
                    self.RCR.param_data = None
                    self.RCR.header = self.BFR.format_to_same(self.init_header)
                    self.RCR.header.pop("Accept")
                    self.RCR.header.update(self.base_header)
                    print(self.RCR.header)
                    self.RCR.header.update({
                        "host": "www.southwest.com",
                        "origin": "https://www.southwest.com",
                        "referer": "https://www.southwest.com/air/booking/select.html?" + query_url
                    })
                    print(self.RCR.header)
                    self.base_header = self.BFR.format_to_same(self.RCR.header)
                    self.RCR.post_data = dict(query)
                    self.RCR.post_data.update({
                        "application": "air-booking", "site": "southwest"
                    })
                    if self.RCR.request_to_post("json", "json"):
                        success = self.RCR.page_source.get("success")
                        data = self.RCR.page_source.get("data")
                        if success and data:
                            # # # 安全通过。
                            self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                            return True
                        else:
                            error, temp_list = self.BPR.parse_to_path("$.notifications.formErrors[0].code",
                                                                      self.RCR.page_source)
                            if not error:
                                error, temp_list = self.BPR.parse_to_path("$.notifications.fieldErrors[0].code",
                                                                          self.RCR.page_source)
                                if not error:
                                    self.logger.info("查询航线未知错误(*>﹏<*)【query】")
                                    self.callback_msg = "请求查询未知错误"
                                    return False
            
                            self.logger.info(f"查询航线返回错误(*>﹏<*)【{error}】")
                            self.callback_msg = f"查询航线返回错误【{error}】"
                            return False
            # # # 错误重试。
            self.logger.info(f"首页查询第{count + 1}次超时(*>﹏<*)【index】")
            self.callback_msg = f"首页查询第{count + 1}次超时，请重试。"
            return self.process_to_index(count + 1, max_count)
    
    def process_to_query(self, count: int = 0, max_count: int = 1) -> bool:
        """Query process. 查询过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            details, temp_list = self.BPR.parse_to_path(
                "$.data.searchResults.airProducts[0].details", self.RCR.copy_source)
            if not details and type(details) is not list:
                self.logger.info(f"获取不到航线数据(*>﹏<*)【{self.CPR.departure_code}】【{self.CPR.arrival_code}】")
                self.callback_msg = "该航线航班已售完"
                return False
            
            is_flight = False               # 是否匹配到航班
            single_price = ""           # 单人价格
            flight_numbers = ""
            stops_details = []
            departure_time = ""
            arrival_time = ""
            product_id = ""
            select_type = ""
            fare_data = {}
            upgrade_type = ""
            upgrade_fare = {}
            sum_dict = {}

            for i in details:
                stops_details = i.get('stopsDetails')
                if not stops_details or len(stops_details) != self.CPR.segment_num:
                    continue

                # # # 解析网页航班号
                source_num = i.get("flightNumbers")
                if len(source_num) > 1:
                    continue
                    
                source_no = source_num[0]
                source_no = self.BFR.format_to_int(source_no)
                # # # 解析接口航班号
                # interface_carrier = self.CPR.flight_num[:2]
                interface_no = self.CPR.flight_num[2:]
                interface_no = self.BFR.format_to_int(interface_no)
                # # # 匹配航班号
                if interface_no == source_no:
                    is_flight = True
                
                    flight_numbers = i.get('flightNumbers')
                    stops_details = i.get('stopsDetails')
                    departure_time = i.get('departureTime')
                    arrival_time = i.get('arrivalTime')
                    
                    adult, temp_list = self.BPR.parse_to_path("$.fareProducts.ADULT", i)
                    if not adult:
                        self.logger.info(f"获取不到成人数据(*>﹏<*)【{self.CPR.flight_num}】")
                        self.callback_msg = "该航线航班已售完"
                        return False
                    
                    price_dict = {}
                    for k, v in adult.items():
                        price, temp_list = self.BPR.parse_to_path("$.fare.totalFare.value", v)
                        status, temp_list = self.BPR.parse_to_path("$.availabilityStatus", v)
                        if price:
                            sum_dict[k] = price
                            price_dict[k] = self.BFR.format_to_float(2, price)
                        else:
                            sum_dict[k] = status
                    
                    if not price_dict:
                        self.logger.info(f"获取不到价格数据(*>﹏<*)【{self.CPR.flight_num}】")
                        self.callback_msg = "该航班座位已售完"
                        return False
    
                    price_list = sorted(price_dict.values())
                    select_price = price_list[0]
                    upgrade_price = price_list[-1]
                    
                    for k, v in price_dict.items():
                        if v == select_price:
                            select_type = k
                        elif v == upgrade_price:
                            upgrade_type = k
    
                    self.logger.info(f"{select_type}, {upgrade_type}")
                    product_id, temp_list = self.BPR.parse_to_path(
                        f"$.fareProducts.ADULT.{select_type}.productId", i)
                    fare_data, temp_list = self.BPR.parse_to_path(f"$.fareProducts.ADULT.{select_type}", i)
                    single_price, temp_list = self.BPR.parse_to_path(
                        f"$.fareProducts.ADULT.{select_type}.fare.totalFare.value", i)
                    upgrade_fare, temp_list = self.BPR.parse_to_path(f"$.fareProducts.ADULT.{upgrade_type}", i)
                    break
            
            if not is_flight:
                self.logger.info(f"匹配不到航班信息(*>﹏<*)【{self.CPR.flight_num}】")
                self.callback_msg = "该航线航班已售完"
                return False
    
            single_price = self.BFR.format_to_float(2, single_price)
            self.total_price = single_price * (self.CPR.adult_num + self.CPR.child_num)
            self.total_price = self.BFR.format_to_float(2, self.total_price)

            # # # 比价格是否要继续支付。
            if self.process_to_compare(max_count=self.retry_count):
                pass
            else:
                return False
               
            self.RCR.url = 'https://www.southwest.com/api/air-booking/v1/air-booking/page/air/booking/price'
            self.RCR.param_data = None
            self.RCR.header = self.base_header
            self.RCR.post_data = {
                "adultPassengersCount": self.CPR.adult_num + self.CPR.child_num, "currencyCode": "USD",
                "currencyType": "REVENUE", "requiredPricingInfo": True, "segmentProducts": [{"ADULT": product_id}],
                "seniorPassengersCount": "0", "application": "air-booking", "site": "southwest"
            }
            if self.RCR.request_to_post("json", "json"):
                success = self.RCR.page_source.get("success")
                data = self.RCR.page_source.get("data")
                if success and data:
                    # # # 安全通过。
                    self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                
                    change_price, temp_list = self.BPR.parse_to_path(
                        f"$.data.priceFlightsResults.segmentProducts[0].ADULT.fare.totalFare.value",
                        self.RCR.page_source)
                    change_price = self.BFR.format_to_float(2, change_price)
                    if single_price != change_price:
                        self.logger.info(f"航班发生变价{single_price},{change_price}")

                    self.total_price = change_price * (self.CPR.adult_num + self.CPR.child_num)
                    self.total_price = self.BFR.format_to_float(2, self.total_price)

                    # # # 比价格是否要继续支付。
                    if self.process_to_compare(max_count=self.retry_count):
                        pass
                    else:
                        return False
                    
                    # # # 计算最终返回价格，不含行李价格。
                    self.return_price = self.total_price
                    
                    itinerary_pricings, temp_list = self.BPR.parse_to_path(
                        "$.data.priceFlightsResults.itineraryPricings", self.RCR.copy_source)
                    now = self.DFR.format_to_now()
                    flight_date = self.DFR.format_to_transform(self.CPR.flight_date, "%Y%m%d")
                    flight_date = flight_date.strftime("%Y-%m-%d")
                    self.air_data = {
                        "air": {
                            "fares": {
                                "0": {
                                    "departureDate": flight_date, "destinationAirportCode": self.CPR.arrival_code,
                                    "international": False, "nextDay": False,
                                    "originationAirportCode": self.CPR.departure_code, "stopsDetails": stops_details,
                                    "ADULT": {
                                        "arrivalTime": arrival_time, "departureTime": departure_time,
                                        "fareData": fare_data, "fareType": select_type,
                                        "flightNumbers": flight_numbers, "hasUpgradeData": False,
                                        "nextDay": False, "rowSummary": sum_dict, "stopsDetails": stops_details,
                                        "upgradeFare": upgrade_fare, "drawerUpgradeAccepted": False,
                                        "drawerUpgradeOffered": False,
                                        "modalUpgradeAccepted": False, "modalUpgradeOffered": False
                                    }
                                }
                            },
                            "id": "air",
                            "query": {
                                "int": "HOMEQBOMAIR", "adultPassengersCount": self.CPR.adult_num + self.CPR.child_num,
                                "departureDate": flight_date, "destinationAirportCode": self.CPR.arrival_code,
                                "fareType": "USD", "originationAirportCode": self.CPR.departure_code,
                                "passengerType": "ADULT",
                                "returnDate": "", "seniorPassengersCount": "0", "tripType": "oneway",
                                "departureTimeOfDay": "ALL_DAY", "reset": "true", "returnTimeOfDay": "ALL_DAY"
                            },
                            "earlyBirdProduct": None, "funds": None, "unaccompaniedMinorFee": None,
                            "itineraryPricings": itinerary_pricings,
                            "lastPriceUpdate": now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
                        }
                    }
                    return True
                else:
                    error, temp_list = self.BPR.parse_to_path(
                        "$.notifications.formErrors[0].code", self.RCR.page_source)
                    if not error:
                        error, temp_list = self.BPR.parse_to_path(
                            "$.notifications.fieldErrors[0].code", self.RCR.page_source)
                        if not error:
                            self.logger.info("提交查询未知错误(*>﹏<*)【detail】")
                            self.callback_msg = "提交查询未知错误"
                            return False
        
                    self.logger.info(f"提交查询返回错误(*>﹏<*)【{error}】")
                    self.callback_msg = f"提交查询返回错误【{error}】"
                    return False
    
            self.logger.info(f"提交查询第{count + 1}次超时或者错误(*>﹏<*)【detail】")
            self.callback_msg = f"提交查询第{count + 1}次超时"
            return self.process_to_query(count + 1, max_count)

    def process_to_compare(self, count: int = 0, max_count: int = 1) -> bool:
        """Compare process. 对比过程。

		Args:
			count (int): 累计计数。
			max_count (int): 最大计数。

		Returns:
			bool
		"""
        # # # 生成header, 查询货币汇率。
        self.RCR.url = f"http://flight.yeebooking.com/yfa/tool/interface/convert_conversion_result?" \
                       f"foreignCurrency={self.CPR.currency}&carrier=WN"
        self.RCR.param_data = None
        self.RCR.header = self.BFR.format_to_same(self.init_header)
        self.RCR.post_data = None
        if self.RCR.request_to_get("json"):
            # # # 解析汇率转换人民币价格。
            exchange = self.RCR.page_source.get(self.CPR.currency)
            if not exchange:
                self.logger.info(f"转换汇率价格失败(*>﹏<*)【{self.RCR.page_source}】")
                self.callback_msg = "转换汇率价格失败，请通知技术检查程序。"
                return False
            exchange_price = self.BFR.format_to_float(2, self.total_price * exchange)
            # # # 进行接口比价。
            target_price = self.BFR.format_to_float(2, self.CPR.target_price)
            diff_price = self.BFR.format_to_float(2, self.CPR.diff_price)
            target_total = self.BFR.format_to_float(2, target_price + diff_price)
            if exchange_price > target_total:
                self.logger.info(f"出票价格过高(*>﹏<*)【{target_total}】【{exchange_price}】")
                self.callback_msg = f"出票价格上限为{target_total}元。出票失败，出票价格过高，{exchange_price}元。"
                return False
        
            return True
        # # # 错误重试。
        self.logger.info(f"查询汇率接口第{count + 1}次超时(*>﹏<*)【compare】")
        self.callback_msg = f"查询汇率接口第{count + 1}次超时，请重试。"
        return self.process_to_compare(count + 1, max_count)
    
    def process_to_service(self, count: int = 0, max_count: int = 1) -> bool:
        """Service process. 辅营过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            self.RCR.url = 'https://www.southwest.com/api/air-booking/v1/air-booking/page/air/booking/purchase'
            self.RCR.param_data = None
            self.RCR.header = self.base_header
            self.RCR.header.update({
                "referer": "https://www.southwest.com/air/booking/price.html"
            })
            self.RCR.post_data = self.BFR.format_to_same(self.air_data)
            self.RCR.post_data['ancillaryType'] = ["EARLY_BIRD", "UNACCOMPANIED_MINOR"]
            self.RCR.post_data['chaseApplied'] = False
            self.RCR.post_data['application'] = "air-booking"
            self.RCR.post_data['site'] = "southwest"
            if self.RCR.request_to_post("json", "json"):
                success = self.RCR.page_source.get("success")
                data = self.RCR.page_source.get("data")
                if success and data:
                    # # # 安全通过。
                    self.RCR.copy_source = self.BFR.format_to_same(self.RCR.page_source)
                    return True
                else:
                    error, temp_list = self.BPR.parse_to_path("$.notifications.formErrors[0].code",
                                                              self.RCR.page_source)
                    if not error:
                        error, temp_list = self.BPR.parse_to_path(
                            "$.notifications.fieldErrors[0].code", self.RCR.page_source)
                        if not error:
                            self.logger.info("请求服务未知错误(*>﹏<*)【service】")
                            self.callback_msg = "请求服务未知错误"
                            return False
                
                    self.logger.info(f"请求服务返回错误(*>﹏<*)【{error}】")
                    self.callback_msg = f"请求服务返回错误【{error}】"
                    return False
            # # # 错误重试。
            self.logger.info(f"服务第{count + 1}次超时或者错误(*>﹏<*)【service】")
            self.callback_msg = f"请求服务第{count + 1}次超时"
            return self.process_to_service(count + 1, max_count)
    
    def process_to_payment(self, count: int = 0, max_count: int = 1) -> bool:
        """Payment process. 支付过程。

        Args:
            count (int): 累计计数。
            max_count (int): 最大计数。

        Returns:
            bool
        """
        if count >= max_count:
            return False
        else:
            # # # 解析详情页
            self.RCR.url = "https://www.southwest.com/api/air-booking/v1/air-booking/page/air/booking/confirmation"
            self.RCR.param_data = None
            self.RCR.header = self.base_header
            self.RCR.header.update({
                "referer": "https://www.southwest.com/air/booking/purchase.html"
            })
            passengers_list = []
            # # # 拼接每个成人具体的参数
            for n, v in enumerate(self.CPR.adult_list):
                sex = "MALE"
                if v.get("gender") == "F":
                    sex = "FEMALE"
                birthday = v.get("birthday")
                birthday = self.DFR.format_to_transform(birthday, "%Y%m%d")
                birthday = birthday.strftime("%Y-%m-%d")
                
                passengers_list.append({
                    "passengerFirstName": v.get("first_name"), "passengerMiddleName": "",
                    "passengerLastName": v.get("last_name"), "passengerSuffix": "0", "passengerGender": sex,
                    "passengerDateOfBirth": birthday,
                    "passengerRapidRewards": "", "passengerRedressTravelerNumber": "",
                    "passengerKnownTravelerNumber": "",
                    "passengerPassportCountryOfResidence": "", "passengerPassportExpirationDate": "",
                    "passengerPassportIssuedBy": "", "passengerPassportNationality": "",
                    "passengerPassportNumber": "", "passengerDisabilityBlind": False,
                    "passengerDisabilityDeaf": False,
                    "passengerDisabilityCognitive": False, "passengerDisabilityAssistanceAnimal": False,
                    "passengerDisabilityEmotionalAnimal": False,
                    "passengerDisabilityWheelchairAssistance": "NO_NEEDED",
                    "passengerDisabilityWheelchairStowage": "NO_NEEDED", "passengerDisabilitySpillableBatteries": "0",
                    "passengerDisabilityNonSpillableBatteries": "0", "passengerDisabilityPeanut": False,
                    "passengerDisabilityOxygen": False, "passengerType": "ADULT"
                })

            # # # 拼接每个儿童具体的参数
            if self.CPR.child_num:
                for n, v in enumerate(self.CPR.child_list):
                    n += self.CPR.adult_num
                    sex = "MALE"
                    if v.get("gender") == "F":
                        sex = "FEMALE"
                    birthday = v.get("birthday")
                    birthday = self.DFR.format_to_transform(birthday, "%Y%m%d")
                    birthday = birthday.strftime("%Y-%m-%d")
                    
                    passengers_list.append({
                        "passengerFirstName": v.get("first_name"), "passengerMiddleName": "",
                        "passengerLastName": v.get("last_name"),
                        "passengerSuffix": "0", "passengerGender": sex, "passengerDateOfBirth": birthday,
                        "passengerRapidRewards": "", "passengerRedressTravelerNumber": "",
                        "passengerKnownTravelerNumber": "",
                        "passengerPassportCountryOfResidence": "", "passengerPassportExpirationDate": "",
                        "passengerPassportIssuedBy": "", "passengerPassportNationality": "",
                        "passengerPassportNumber": "", "passengerDisabilityBlind": False,
                        "passengerDisabilityDeaf": False,
                        "passengerDisabilityCognitive": False, "passengerDisabilityAssistanceAnimal": False,
                        "passengerDisabilityEmotionalAnimal": False,
                        "passengerDisabilityWheelchairAssistance": "NO_NEEDED",
                        "passengerDisabilityWheelchairStowage": "NO_NEEDED",
                        "passengerDisabilitySpillableBatteries": "0",
                        "passengerDisabilityNonSpillableBatteries": "0", "passengerDisabilityPeanut": False,
                        "passengerDisabilityOxygen": False, "passengerType": "ADULT"
                    })

            card_year = "20" + self.CPR.card_date[:2]
            card_month = self.CPR.card_date[2:]
            card_code = self.AFR.decrypt_into_aes(
                self.AFR.encrypt_into_sha1(self.AFR.password_key), self.CPR.card_code)
            if not card_code:
                self.logger.info(f"解密支付卡失败(*>﹏<*)【{self.CPR.card_code}】")
                self.callback_msg = "解密支付卡失败"
                return False
    
            self.RCR.post_data = {
                "planSectionFirstEmail": "", "planSectionSecondEmail": "", "planSectionThirdEmail": "",
                "planSectionFourthEmail": "", "fundsCoverTotalFlight": False, "paymentMethodSelected": "creditcard",
                "savedCreditCardSelected": False, "cvvHidden": False, "aboutTripBusinessCheckBox": False,
                "aboutTripFirstTimeCheckBox": False, "aboutTripPersonalCheckBox": True, "savedEmailAddress": "",
                "savedReceiptEmailSelected": False, "sendYourReceiptEmail": self.CPR.contact_email,
                "contactCountryCode": "1", "contactEmailAddress": self.CPR.contact_email, "contactMethod": "email",
                "contactOptOut": False, "contactPhoneNumber": "", "contactPreferredLanguage": "EN",
                "cartProducts": self.air_data, "chaseSessionId": None, "minorFormData": None,
                "pointsToUse": 0, "selectedCardInfo": None, "application": "air-booking", "site": "southwest",
                "creditCard": {
                    "cardNumber": self.CPR.card_num, "cityTown": "beijing", "country": "CN",
                    "countryCode": "86", "creditCardType": "MASTERCARD", "expiration": f"{card_month}-{card_year}",
                    "firstNameOnCard": self.CPR.card_first, "lastNameOnCard": self.CPR.card_last,
                    "phoneNumber": self.CPR.contact_mobile, "primary": False, "provinceRegion": "beijing",
                    "securityCode": card_code, "state": "", "streetAddress": "beijing",
                    "streetAddressSecond": "", "zipCode": "10000", "zipCodeRequired": True
                },
                "dutyOfCareContactInfo": {}, "passengersList": passengers_list
            }
            
            if self.RCR.request_to_post("json", "json"):
                success = self.RCR.page_source.get("success")
                data = self.RCR.page_source.get("data")
                if success and data:
                    self.record, temp_list = self.BPR.parse_to_path(
                        "$.data.searchResults.reservations.air.ADULT.confirmationNumber", self.RCR.page_source)
                    if self.record:
                        return True
                    else:
                        self.logger.info("获取PNR失败(*>﹏<*)【payment】")
                        self.callback_msg = "获取PNR失败，可能已出票"
                        self.callback_data["orderIdentification"] = 2
                        return False
                else:
                    error, temp_list = self.BPR.parse_to_path(
                        "$.notifications.formErrors[0].code", self.RCR.page_source)
                    if not error:
                        error, temp_list = self.BPR.parse_to_path(
                            "$.notifications.fieldErrors[0].code", self.RCR.page_source)
                        if not error:
                            self.logger.info("提交支付未知错误(*>﹏<*)【payment】")
                            self.callback_msg = "提交支付未知错误"
                            self.callback_data["orderIdentification"] = 2
                            return False

                    self.logger.info(f"提交支付返回错误(*>﹏<*)【{error}】")
                    self.callback_msg = f"提交支付返回错误【{error}】"
                    self.callback_data["orderIdentification"] = 2
                    return False
            # # # 错误重试。
            self.logger.info(f"请求支付第{count + 1}次超时(*>﹏<*)【payment】")
            self.callback_msg = f"请求支付第{count + 1}次超时，请重试。"
            self.callback_data["orderIdentification"] = 2
            return self.process_to_payment(count + 1, max_count)

    def process_to_return(self) -> bool:
        """Return process. 返回过程。

		Returns:
			bool
		"""
        self.callback_data["success"] = "true"
        self.callback_data['msg'] = "出票成功"
        self.callback_data['totalPrice'] = self.return_price
        self.callback_data["currency"] = self.CPR.currency
        self.callback_data['pnrCode'] = self.record
        self.callback_data["orderIdentification"] = 3
        self.callback_data["baggages"] = self.CPR.return_baggage
        self.logger.info(self.callback_data)
        return True

