# -*- coding: utf-8 -*-
import scrapy
from daf2e.items import Daf2EItem
import time

class DaqianduanSpider(scrapy.Spider):
	name = "daqianduan"
	allowed_domains = ["daqianduan.com"]
	start_urls = (
	    'http://www.daqianduan.com/nav',
	)

	def parse(self, response):
		items = []
		for sel in response.xpath('//*[@id="navs"]/div/div/ul/li'):
			item = Daf2EItem()
			item['link_category'] = "".join(sel.xpath('../../h2/text()').extract())
			item['link_name'] = "".join(sel.xpath('a/text()').extract())
			item['link_url'] = "".join(sel.xpath('a/@href').extract())
			item['link_description'] = "".join(sel.xpath('text()').extract())
			#print item	
			yield item
			time.sleep(1) # io error