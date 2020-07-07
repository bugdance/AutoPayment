#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""Unit test.

written by pyLeo.
"""
# # # Import current path.
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.append('..')
# # # Analog Function.
from loguru import logger
from accessor.request_crawler import RequestCrawler
from accessor.selenium_crawler import SeleniumCrawler
from booster.aes_formatter import AESFormatter
from booster.basic_formatter import BasicFormatter
from booster.basic_parser import BasicParser
from booster.date_formatter import DateFormatter
from booster.dom_parser import DomParser
from detector.persvj_simulator import PersVJSimulator
from hammer.data_tester import a
import datetime
import time
import requests

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('mysql://root:@127.0.0.1:3306/reference')

Model = declarative_base()


logger.add("unit_tester.log", colorize=True, enqueue=True,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")


class News(Model):
	"""MM造值表,abck
    """
	__tablename__ = "news"
	id = Column(Integer, primary_key=True)
	url = Column(String)
	title = Column(String)
	scrape_date = Column(Integer)
	content = Column(Text)

	def __init__(self, url, title, scrape_date, content):
		self.url = url
		self.title = title
		self.scrape_date = scrape_date
		self.content = content

class Counts(Model):
	"""VY造值表,abck
    """
	__tablename__ = "counts"
	id = Column(Integer, primary_key=True)
	scrape_date = Column(Integer)
	news_count = Column(Integer)

	def __init__(self, scrape_date, news_count):
		self.scrape_date = scrape_date
		self.news_count = news_count


def get_proxy():
	"""
    判断代理，在规定时间段内使用
    :return:
    """
	url = 'http://cloudmonitorproxy.51kongtie.com/Proxy/getProxyByServiceType?proxyNum=1&serviceType=4'
	# 塔台
	res = requests.get(url)
	res = res.json()
	ip = res[0]['proxyIP']
	return f"http://yunku:123@{ip}:3138"


def get_page(day, RC, BF, DP, init_header, session):



	RC.url = f"https://new.zlck.com/ckxx/date/{day}.html"
	RC.param_data = None
	RC.header = BF.format_to_same(init_header)
	RC.header.update({
		"Host": "new.zlck.com",
	})
	RC.post_data = None
	if not RC.request_to_get():
		# print(f"错误======================={day}")
		get_ip = get_proxy()
		RC.set_to_proxy(True, get_ip)
		get_page(day, RC, BF, DP, init_header, session)
	else:
		view_count, temp_list = DP.parse_to_attributes(
			"href", "css", "#news_content a[href*='/news/']", RC.page_source)

		sql = "insert ignore into counts(scrape_date, news_count) values('%s', '%s')" % (day, len(temp_list))
		session.execute(sql)
		session.commit()

		for i in temp_list:
			sql = "insert ignore into news(url, title, scrape_date, content) values('%s', '', '%s', '')" % (
			"https://new.zlck.com/" + i, day)
			session.execute(sql)
			session.commit()



def run(b):


	RC = RequestCrawler()
	BF = BasicFormatter()
	DP = DomParser()
	RC.logger = logger
	BF.logger = logger
	DP.logger = logger


	RC.set_to_session()
	get_ip = get_proxy()
	RC.set_to_proxy(True, get_ip)
	user_agent, init_header = RC.build_to_header("none")
	RC.timeout = 10

	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	# 1983-10-17
	begin = datetime.date(b[0], b[1], b[2])
	end = datetime.date(b[3], b[4], b[5])
	delta = datetime.timedelta(days=1)

	# # # 请求接口服务。
	while begin <= end:
		time.sleep(5)
		day = begin.strftime("%Y%m%d")
		begin += delta
		get_page(day, RC, BF, DP, init_header, session)

	session.close()




if __name__ == '__main__':
	


	executor = ThreadPoolExecutor(max_workers=5)
	urls = [[1988,1,1,1991,1,1], [1991,1,1,1994,1,1], [1994,1,1,1997,1,1], [1997,1,1,2000,1,1], [2000,1,1,2002,12,31]]  # 并不是真的url
	for data in executor.map(run, urls):
		pass







			# RC.url = "https://new.zlck.com" + i
			# if RC.request_to_get():
			# 	title, title_list = DP.parse_to_attributes(
			# 		"text", "css", "#news h1", RC.page_source)
			#
			# 	content, content_list = DP.parse_to_attributes(
			# 		"text", "css", "#news_content>p", RC.page_source)
			#
			# 	for j in content_list:
			# 		if j:
			# 			if "同期推荐" in j:
			# 				break
			# 			print(j)
			# 	print("=================================")

