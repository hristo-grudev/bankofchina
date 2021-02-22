import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import BankofchinaItem
from itemloaders.processors import TakeFirst


class BankofchinaSpider(scrapy.Spider):
	name = 'bankofchina'
	start_urls = ['https://www.bank-of-china.com/lu/aboutus/bi1/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news"]/ul/li')
		for post in post_links:
			url = post.xpath('.//a/@href').get()
			date = post.xpath('./span//text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//li[@class="turn_next"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)


	def parse_post(self, response, date):
		title = response.xpath('//h2/text()').get()
		description = response.xpath('//div[@class="sub_con"]//text()[normalize-space() and not(ancestor::script)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		if date:
			date = re.findall(r'\d+-\d+-\d+', date)[0]

		item = ItemLoader(item=BankofchinaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()