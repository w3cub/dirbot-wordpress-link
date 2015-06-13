# -*- coding: utf-8 -*-

# Scrapy settings for daf2e project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'daf2e'

SPIDER_MODULES = ['daf2e.spiders']
NEWSPIDER_MODULE = 'daf2e.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'daf2e (+http://www.yourdomain.com)'

ITEM_PIPELINES = [
    'daf2e.pipelines.RequiredFieldsPipeline',
    'daf2e.pipelines.FilterWordsPipeline',
    'daf2e.pipelines.MySQLStorePipeline',
]


DB_NAME = 'wordpress'
# MySQL database username
DB_USER = 'root'
# MySQL database password 
DB_PASSWORD = '123456'
#MySQL hostname
DB_HOST = 'localhost'
# Database Charset to use in creating database tables.
DB_CHARSE =  'utf8'
