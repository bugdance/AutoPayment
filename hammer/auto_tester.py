#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""Script test.

written by pyLeo.
"""
# # # Import current path.
import sys
sys.path.append('..')
# # # Analog interface.
import requests
import time
from explorer.perswn_scraper import PersWNScraper
from explorer.persmm_scraper import PersMMScraper
from explorer.persvj_scraper import PersVJScraper
from explorer.persnk_scraper import PersNKScraper
from explorer.persvy_scraper import PersVYScraper
from explorer.persfy_scraper import PersFYScraper
from explorer.perstw_scraper import PersTWScraper
from explorer.corpsl_scraper import CorpSLScraper


post_data = {
    "carrierAccount": "QCYG003", "carrierPassword": "OEJ9R260NtiRBd2L6A8PuQ==",
    "automaticGetTicketId": 5548, "price": "1000", "priceDifference": "2000",
    "departureAirport": "GMP", "arriveAirport": "CJU", "promotionCode": "123",
    "departureTime": "20200229", "flightNumber": "TW701", "pnrCode": "LEDJFC",
    # "departureAirport": "OKA", "arriveAirport": "ICN", "promotionCode": "123",
    # "departureTime": "20200522", "flightNumber": "TW272", "pnrCode": "LEDJFC",
    "VCC": {
        "cardTermValidity": "2702",
        "cardName": "GUO/LIN",
        "cardSafetyCode": "ThDqO+aFXPn4yao4ajLMnA==",
        "cardNumber": "5329598085312649"
    },
    "passengerBaggages": [
        {"type": 0, "passengerName": "weng/han", "gender": "M", "birthday": "19840526",
         "nationality": "CN", "cardNum": "EA3071284", "cardIssuePlace": "CN", "cardExpired": "20270517",
         "baggages": [
             # {"weight": 25, "number": 1, "parent": 19362, "id": 26037}
         ]},
        # {"type": 0, "passengerName": "liu/han", "gender": "F", "birthday": "19730626",
        #  "nationality": "CN", "cardNum": "EA3071281", "cardIssuePlace": "CN", "cardExpired": "20270517",
        #  "baggages": [
        #      # {"weight": 10, "number": 1, "parent": 19362, "id": 26037},
        #      # {"weight": 20, "number": 1, "parent": 19362, "id": 26037},
        #  ]},
        # {"type": 1, "passengerName": "weng/niu", "gender": "M", "birthday": "20080526",
        #  "nationality": "CN", "cardNum": "EA3071287", "cardIssuePlace": "CN", "cardExpired": "20270517",
        #  "baggages": [
        #      # {"weight": 36, "number": 1, "parent": 19362, "id": 26037}
        #  ]},
        # {"type": 1, "passengerName": "weng/kan", "gender": "F", "birthday": "20080626",
        #  "nationality": "CN", "cardNum": "EA3071288", "cardIssuePlace": "CN", "cardExpired": "20270517",
        #  "baggages": [
        #      {"weight": 10, "number": 1, "parent": 19362, "id": 26037},
        #      {"weight": 25, "number": 1, "parent": 19362, "id": 26037},
        #  ]}
    ],
}



def post_test():
    """
    
    Returns:

    """
    company = "uo"
    url = f"http://interface.python.flight.yeebooking.com/auto/{company}/"
    # url = f"http://119.3.169.64:18082/auto/{company}/"
    response = requests.post(url=url, json=post_data)
    print(response.text)


if __name__ == '__main__':
    
    post_test()
    # while 1:
    #
    #     process_dict = {
    #         "task_id": 1111, "log_path": "test.log", "source_dict": post_data,
    #         "enable_proxy": False, "address": "http://127.0.0.1:9000", "retry_count": 1
    #     }
    #
    #     airline_account = "pers"
    #     airline_company = "tw"
    #     create_var = locals()
    #     scraper = create_var[airline_account.capitalize() + airline_company.upper() + "Scraper"]()
    #     result = scraper.process_to_main(process_dict)
    #     time.sleep(600)

