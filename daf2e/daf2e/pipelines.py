# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from datetime import datetime
from hashlib import md5
from scrapy import log
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
import urllib
import sys
import logging
from scrapy.log import ScrapyFileLogObserver



# class Daf2EPipeline(object):

# 	def process_item(self, item, spider):
# 		return item


class FilterWordsPipeline(object):

	"""A pipeline for filtering out items which contain certain words in their
	description"""

	# put all words in lowercase
	words_to_filter = ['politics', 'religion']

	def process_item(self, item, spider):
		# for word in self.words_to_filter:
		#     desc = item.get('description') or ''
		#     if word in desc.lower():
		#         raise DropItem("Contains forbidden word: %s" % word)
		# else:
		return item


class RequiredFieldsPipeline(object):

	"""A pipeline to ensure the item have the required fields."""

	required_fields = ('link_name', 'link_url', 'link_description', 'link_category')

	def process_item(self, item, spider):
		for field in self.required_fields:
			if not item.get(field):
				raise DropItem("Field '%s' missing: %r" % (field, item))
		return item


class MySQLStorePipeline(object):

	"""A pipeline to store the item in a MySQL database.
	This implementation uses Twisted's asynchronous database API.
	"""

	def __init__(self, dbpool):
		self.dbpool = dbpool
		reload(sys)                         # 2
		sys.setdefaultencoding('utf-8')     # 3
		logfile = open('testlog.log', 'w')
		log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
		log_observer.start()


	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=settings['DB_HOST'],
			db=settings['DB_NAME'],
			user=settings['DB_USER'],
			passwd=settings['DB_PASSWORD'],
			charset= settings['DB_CHARSE'],
			use_unicode=True
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)

	def process_item(self, item, spider):
		# run db query in the thread pool
		d = self.dbpool.runInteraction(self.wp_insert_link, item, spider)
		d.addErrback(self._handle_error, item, spider)
		# at the end return the item in case of success or failure
		d.addBoth(lambda _: item)
		# return the deferred instead the item. This makes the engine to
		# process next item (according to CONCURRENT_ITEMS setting) after this
		# operation (deferred) has finished.
		return d

	def compact(locals, *keys):
		return dict((k, locals[k]) for k in keys)

	def wp_set_object_terms(self, conn, object_id, terms, spider):

		# wp_get_object_terms
		# conn.execute("""
		# 	SELECT tr.term_taxonomy_id
		# 	FROM wp_term_relationships AS tr
		# 	INNER JOIN wp_term_taxonomy AS tt
		# 	ON tr.term_taxonomy_id = tt.term_taxonomy_id
		# 	WHERE tr.object_id IN (%s)
		# 	AND tt.taxonomy IN ('link_category')
		# 	""", (object_id,))
		# term_taxonomy_id = conn.fetchone()
		# spider.log("term_taxonomy_id : %s %r" % (object_id, term_taxonomy_id))

		# term_exists
		conn.execute("""
			SELECT tt.term_id, tt.term_taxonomy_id
			FROM wp_terms AS t
			INNER JOIN wp_term_taxonomy as tt
			ON tt.term_id = t.term_id
			WHERE t.term_id = %s
			AND tt.taxonomy = 'link_category'
			""",(terms[0],))
		rec = conn.fetchone()
		if not rec:
			spider.log("return: %r" % (rec,))
			return 0

		conn.execute("""
			SELECT term_taxonomy_id
			FROM wp_term_relationships
			WHERE object_id = %s
			AND term_taxonomy_id = %s 
			""",(object_id, terms[0]))
		result = conn.fetchone()
		spider.log("term_taxonomy_id in wp_term_relationships: %r" % (result,))
		spider.log("term_taxonomy_id id: %r" % (terms,))
		if not result:
			conn.execute("""
				INSERT INTO `wp_term_relationships` (`object_id`, `term_taxonomy_id`)
				VALUES (%s, %s)
				""",(object_id, terms[0]))
			
			# _update_generic_term_count
			conn.execute("""  
				SELECT COUNT(*)
				FROM wp_term_relationships
				WHERE term_taxonomy_id = %s
				""",(terms[0],)) 
			count = conn.fetchone()[0];

			# _update_generic_term_count
			conn.execute("""
				UPDATE `wp_term_taxonomy`
				SET `count` = %s
				WHERE `term_taxonomy_id` = %s
				""",(count, terms[0]))
		
		#if not term_taxonomy_id:

				# clean_term_cache
				# conn.execute("""
				# 	SELECT term_id, taxonomy
				# 	FROM wp_term_taxonomy
				# 	WHERE term_taxonomy_id IN (%s)
				# 	""",(terms[0],))
		#/wp-includes/taxonomy.php

	def wp_set_link_cats(self, conn,  link_id, link_categories, spider):
		# If $link_categories isn't already an array, make it one:
		# if not isinstance(link_categories, list) or (not link_categories):
		# 	link_categories = ['2'];
		#link_categories = map( int, link_categories)
		self.wp_set_object_terms(conn, link_id, link_categories, spider )

	def term_exists_link_category(self, conn, cat_name, spider):
		conn.execute("""
			SELECT tt.term_id, tt.term_taxonomy_id
			FROM wp_terms AS t
			INNER JOIN wp_term_taxonomy as tt
			ON tt.term_id = t.term_id
			WHERE t.name = %s
			AND tt.taxonomy = 'link_category'
			ORDER BY t.term_id ASC
			LIMIT 1
		""", (cat_name,)) # urllib.quote(str(cat_name)).lower()
		ret = conn.fetchone()
		spider.log("term_exists_link_category: %r" % (ret,))
		return ret

	def wp_insert_term_link_category(self, conn, cat_name, spider):
		conn.execute("""
			INSERT INTO `wp_terms` (`name`, `slug`, `term_group`)
			VALUES (%s, %s, 0)
			""",(cat_name, urllib.quote(str(cat_name)).lower()))
		reid = int(conn.lastrowid)
		spider.log("wp_terms id : %r" % (reid,))

		conn.execute("""
			INSERT INTO `wp_term_taxonomy` (`term_id`, `taxonomy`, `description`, `parent`, `count`)
			VALUES (%s, 'link_category', '', 0, 0)
			""",(reid,))
		reid2 = int(conn.lastrowid)
		spider.log("wp_term_taxonomy id : %r" % (reid2,))
		
		return reid2

	def wp_insert_link(self, conn, linkdata, spider):
		defaults = {'link_id': 0, 'link_description' : '','link_image': '', 'link_name': '', 'link_owner': 1, 'link_visible': 'Y', 'link_rss': '', 'link_rel': '', 'link_notes': '', 'link_target' : '_blank', 'link_url': '', 'link_rating': 0 }
		defaults.update(linkdata)
		r = defaults
		#link_id = r['link_id']
		link_name = r['link_name']
		link_url = r['link_url']

		update = False

		if link_url:
			conn.execute("""SELECT EXISTS(
				SELECT 1 FROM wp_links WHERE link_url = %s
			)""", (link_url, ))
			update = int(conn.fetchone()[0])

		if not link_name.strip():
			if link_url.strip():
				link_name = link_url
			else:
				return 0

		if not link_url.strip():
			return 0

		cat_id = self.term_exists_link_category(conn, r['link_category'], spider)
		if not cat_id:
			cat_id = self.wp_insert_term_link_category(conn, r['link_category'], spider) # getlink cat  wp_insert_term
			spider.log('insert new cat_id is: %r' % (cat_id,))
			link_category = [cat_id]
		else:
			link_category = [cat_id[0]]

		link_rating = (r['link_rating'] if r['link_rating'] else 0)
		link_image = (r['link_image'] if r['link_image'] else '')
		link_target = (r['link_target'] if r['link_target'] else '_blank')
		link_visible = (r['link_visible'] if r['link_visible'] else 'Y')
		# get_current_user_id();
		link_owner = (r['link_owner'] if r['link_owner'] else 1)
		link_notes = (r['link_notes'] if r['link_notes'] else '')
		link_description = (r['link_description'] if r['link_description'] else '')
		link_rss = (r['link_rss'] if r['link_rss'] else '')
		link_rel = (r['link_rel'] if r['link_rel'] else '')

		if not update:
		# 	pass
		# 	# conn.execute("""
		# 	# 	UPDATE website
		# 	# 	SET name=%s, description=%s, url=%s, updated=%s
		# 	# 	WHERE guid=%s
		# 	# """, (item['name'], item['description'], item['url'], now, guid))
		# 	# spider.log("Item updated in db: %s %r" % (guid, item))
		# else:
			conn.execute("""
				INSERT INTO `wp_links` (link_url, link_name, link_image, link_target, link_description, link_visible, link_owner, link_rating, link_rel, link_notes, link_rss)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""", (link_url, link_name, link_image, link_target, link_description, link_visible, link_owner, link_rating, link_rel, link_notes, link_rss))
			
			link_id = int(conn.lastrowid)
			spider.log("Item stored in db: %s %s" % (link_id, link_url))
			self.wp_set_link_cats(conn, link_id, link_category, spider)

	def _handle_error(self, failure, item, spider):
		"""Handle occurred on db interaction."""
		# do nothing, just log
		log.err(failure)


