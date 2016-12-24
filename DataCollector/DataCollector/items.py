# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ResearchPaperItem(scrapy.Item):
    ID=scrapy.Field()
    Link=scrapy.Field()
    Title=scrapy.Field()
    Abstract=scrapy.Field()
    Authors=scrapy.Field()
    Published_in=scrapy.Field()
    Publication_date=scrapy.Field()
    References=scrapy.Field()
    References_links=scrapy.Field()
    Cited_by=scrapy.Field()
    Cited_by_links=scrapy.Field()
