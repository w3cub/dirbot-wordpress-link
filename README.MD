
dirbot-wordpress-link
===



 This project you can scrape the website link  as your wordpress link.

 This project base on [git@github.com:darkrho/dirbot-mysql.git](git@github.com:darkrho/dirbot-mysql.git).


##Items

The items scraped by this project are websites, and the item is defined in the class:

	daf2e.items.Daf2EItem

	link_category = scrapy.Field()
	link_name = scrapy.Field()
	link_url = scrapy.Field()
	link_description = scrapy.Field()

##Spiders
See the source code

**note**: `time.sleep(1)`, if not, it would trigger sql query io error.
This affects the `wp_terms`, `wp_term_taxonomy` and `wp_term_relationships`.
if you have any good idea, give me a fork.
keyword: `multiple items per page`, `yield`...


##Pipelines


###Requiring certain item fields


A pipeline to discard items that lack of certain fields. This pipeline is
defined in the class::

    daf2e.pipelines.RequiredFieldsPipeline


###Storing items in a MySQL database


A pipeline to store (insert or update) scraped items in a MySQL database. This
pipeline is defined in the class:

    daf2e.pipelines.MySQLStorePipeline

The database table include `wp_links`, `wp_terms`, `wp_term_taxonomy` and `wp_term_relationships`.

##Command
    scrapy crawl daqianduan


##Read more


[http://doc.scrapy.org/en/latest/](http://doc.scrapy.org/en/latest/)

[git@github.com:scrapinghub/portia.git](https://github.com/scrapinghub/portia)

