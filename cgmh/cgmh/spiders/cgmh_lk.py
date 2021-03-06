# -*- coding: utf-8 -*-
import sys
import scrapy
import time
import re
from datetime import datetime
from scrapy.http import Request, FormRequest, TextResponse
from scrapy.contrib.spiders import CrawlSpider,Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import log
from ..items import CgmhItem
#from scrapy.stats import Stats

class Cgmh(CrawlSpider):
	name = "cgmh_lk"
	allowed_domains = ["org.tw"]
	start_urls = [
		"https://www.cgmh.org.tw/register/Department.aspx?dpt=3"
	]

	rules = [
		Rule(LinkExtractor(allow = ('RMSTimeTable\.aspx\?dpt=.*'), deny= ('RMSTimeTable\.aspx\?dpt=5.*')),
		callback = 'parse_table', follow = True)
	 ]

	def parse_table(self, response):
		
		items = []
		sel = Selector(response)
		#print sel.extract()
		tables = sel.xpath('//table[@class="tableStyle"]/tr')
		print 'len of table = '+ str(len(tables))
		
		for t in range(len(tables)-1):
			##每個table看有幾個row
			table = tables[t+1].xpath('.//td')
			#print "list: " + str(t) + "," + table[0].extract()
			
			

			for column in range(3):
				#print table[column+1].extract()
				
				br = table[column+1].extract().split('<br>')

				#當一個欄位有兩個人的時候，用br分開
				for b in range(len(br)-1):
					item = CgmhItem()
					n = Selector(text = br[b])
					
					nameFull = n.xpath('.//span/text()').extract()
					
					if (nameFull != []):
						name = re.sub('\d+', '', nameFull[0])
						item['name'] = name.strip()
						status = n.xpath('.//font/text()')[0].extract()
						

						if (status == u'(額滿)'):
							item['full'] = '名額已滿'
							try:
								item['link'] = 'https://www.cgmh.org.tw/register/' + n.xpath('.//a/@href')[0].extract()
							except Exception as e:
								pass

						elif (status == u'(停診)'):
							continue

					else:
						name = re.sub('\d+', '', n.xpath('.//a/text()')[0].extract())
						item['name'] = name.strip()
						item['full'] = '可掛號' 
						item['link'] = 'https://www.cgmh.org.tw/register/' + n.xpath('.//a/@href')[0].extract()
					
					if (column==0):
						item['time'] = 'morning'
					
					if (column==1):
						item['time'] = 'afternoon'
					
					if (column==2):
						item['time'] = 'evening'	
					
					##將中文的年月日轉換成yyddmm
					date = table[0].xpath('.//text()')[0].extract().encode('utf-8')
					dateFormat = '%Y年%m月%d日'
					date = time.strptime(date, dateFormat)
					item['date'] = time.strftime("%Y%m%d", date)
					item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
					item['hospital'] = 'cgmh_lk'
					item['dept'] = sel.xpath('.//span[@id="ctl00_ContentPlaceHolder1_lbDptTitle"]//span/text()')[0].extract().split(" ")[1]

					items.append(item)


		return items