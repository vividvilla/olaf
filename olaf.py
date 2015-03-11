# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~~~

	Main utility to run and freeze blog

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import sys
import os
import datetime
import argparse
from collections import Counter, OrderedDict

import click
from flask import Flask
from urlparse import urljoin
from flask_frozen import Freezer
from werkzeug.contrib.atom import AtomFeed
from flask import render_template, abort, redirect, url_for, \
	request, make_response
from flask_flatpages import FlatPages, pygments_style_defs

from utils import timestamp_tostring, date_tostring, \
	font_size, console_message

# If config file not found copy sample config
if not os.path.exists('config.py'):
	os.system('cp config-sample.py config.py')
	sys.stdout.write('created config file')

import config

app = Flask(__name__)
app.config.from_object('config')

# App module initialize
contents = FlatPages(app)
freeze = Freezer(app)
exclude_from_sitemap = []  # List of urls to be excluded from XML sitemap

# Register utility functions to be used in jinja2 templates
app.jinja_env.globals.update(
	timestamp_tostring=timestamp_tostring,
	date_tostring=date_tostring, font_size=font_size)


def get_posts(**filters):
	"""
	Filters posts
	All arguments are optional

	Optional keyword arguments

	'sort'		: boolean	:: sort by timestamp (default: True)
	'reverse'	: boolean	:: Reverse the order (default: True)
	'tag'		: string	:: Filters by tag name (default: None)
	'page_no'	: integer	:: Paginates results and returns result
								according to page_no (default: None)
	'limit'		: integer	:: Pagination limit (default: global limit)
	'abort'		: boolean	:: Aborts with 404 error if no posts in
								filtered results (default: False)
	"""

	posts = [post for post in contents if post.meta.get('type') == 'post']

	# Filter conditions

	# Sort posts by timestamp (True by default)
	sort = filters.get('sort', True)
	if(sort):
		posts.sort(
			key=lambda x: x.meta['timestamp'],
			reverse=filters.get('reverse', True))

	# Filter based on tag
	tag = filters.get('tag')
	if(tag):
		posts = [post for post in posts if tag in post.meta.get('tags', [])]

	# Filter based on year and month
	year = filters.get('year')
	if(year):
		posts = [post for post in posts if int(timestamp_tostring(
			post.meta.get('timestamp'), '%Y')) == year]

		# Filter by month only if year is given
		month = filters.get('month')
		if month:
			posts = [post for post in posts if int(timestamp_tostring(
				post.meta.get('timestamp'), '%m')) == month]

	# Get total number of posts without pagination
	post_meta = {}
	post_meta['total_pages'] = len(posts)

	# Filter based on page number and pagination limit
	page_no = filters.get('page_no')
	limit = filters.get('limit') or config.SITE['limit']
	max_pages = 0
	if(page_no):
		paginated = [posts[n:n + limit] for n in range(0, len(posts), limit)]
		max_pages = len(paginated)
		try:
			posts = paginated[page_no - 1]
		except IndexError:
			posts = []

	post_meta['max_pages'] = max_pages

	# Abort if posts not found
	if not posts and filters.get('abort') is True:
		abort(404)

	return (posts, post_meta)


def get_posts_by_slug(slug):
	# Check for slug in root which means pages
	content = [page for page in contents if page.path == slug]

	# Check for slug in posts if not found in pages
	if not content:
		content = [post for post in contents if post.path[11::] == slug]
	return content


""" Views """


@app.route('/404.html')
def custom_404():
	""" Custom 404 page view """
	return render_template('404.html')


@app.route('/pygments.css')
def pygments_css():
	""" Default pygments style """
	pyments_style = config.SITE.get('pygments') or 'tango'
	return (pygments_style_defs(pyments_style), 200, {'Content-Type': 'text/css'})

exclude_from_sitemap.append('/pygments.css')  # Excludes url from sitemap


def get_index():
	""" Check if custom home page set else return default index view """
	if config.SITE.get('custom_home_page'):
		content = get_posts_by_slug(config.SITE['custom_home_page'])

		# Exception if slug not found both in pages and posts
		if not content:
			raise Exception('Custom home page url not found')

		# Exception if duplicates found
		if len(content) > 1:
			raise Exception('Duplicate slug')

		return custom_index
	else:
		return default_index


def default_index():
	""" Default index view """
	posts, post_meta = get_posts(page_no=1)
	return render_template('index.html',
		page_no=1, posts=posts, next_page=post_meta['max_pages'] > 1)


def custom_index():
	""" Custom home page view """
	content = get_posts_by_slug(config.SITE['custom_home_page'])
	content[0].meta['type'] = 'page'
	return render_template('page.html', page=content[0])

# Set home page
app.add_url_rule('/', 'index', get_index())


@app.route('/pages/<int:page_no>/')
def pagination(page_no):
	""" Home page pagination view """

	# Redirect if it is a first page (except when custom home page is set)
	if page_no == 1 and not config.SITE.get('custom_home_page'):
		return redirect(url_for('index'))

	posts, post_meta = get_posts(page_no=page_no, abort=True)
	return render_template('index.html', page_no=page_no,
			posts=posts, next_page=(post_meta['max_pages'] > page_no),
			previous_page=(page_no > 1))


@app.route('/<path:slug>/')
def posts(slug):
	""" Individual post/page view """
	content = get_posts_by_slug(slug)

	if not content:
		abort(404)  # Slug not found both in pages and posts

	# Exception if duplicates found
	if len(content) > 1:
		raise Exception('Duplicate slug')

	return render_template('page.html', page=content[0])


# Tag views

@app.route('/tags/')
def tags():
	""" List of tags view """
	tags = [tag for post in contents
				for tag in post.meta.get('tags', [])]
	tags = sorted(Counter(tags).items())  # Count tag occurances

	max_occ = 0 if not tags else max([tag[1] for tag in tags])

	return render_template('tags.html', tags=tags, max_occ=max_occ)


@app.route('/tags/<string:tag>/')
def tag_page(tag):
	""" Individual tag view """
	posts, post_meta = get_posts(tag=tag, page_no=1, abort=True)
	return render_template('tag.html', tag=tag, posts=posts,
			page_no=1, next_page=(post_meta['max_pages'] > 1),
			len = post_meta['total_pages'])


@app.route('/tags/<string:tag>/pages/<int:page_no>/')
def tag_pages(tag, page_no):
	""" Pagination for Individual tags """
	posts, post_meta = get_posts(tag=tag, page_no=page_no, abort=True)

	# Redirect if it is a first page
	if page_no == 1:
		return redirect(url_for('tag_page', tag=tag))

	return render_template('tag.html', tag=tag, posts=posts,
			page_no=page_no, next_page=(post_meta['max_pages'] > page_no),
			len = post_meta['total_pages'], previous_page=(page_no > 1))


@app.route('/list/posts/')
def list_posts():
	""" All posts list view """
	return render_template("list_posts.html", posts=get_posts()[0])


@app.route('/list/pages/')
def list_pages():
	""" All pages list view """
	pages = [page for page in contents
				if page.meta.get('type') == 'page']

	return render_template("list_pages.html", pages=pages)


@app.route('/archive/')
def archive():
	""" Date based archive view """
	# Get all posts dates in format (year, month)
	dates = [(timestamp_tostring(post.meta.get('timestamp'), '%Y'),
			timestamp_tostring(post.meta.get('timestamp'), '%m'))
			for post in contents if post.meta.get('timestamp')]

	# Get sorted yearly archive lists ex: [(year, no_occur), ...]
	yearly = sorted(Counter([date[0] for date in dates]).items(), reverse=True)

	# Get sorted yearly and monthly archive lists [((year, month), no_occur), ...]
	monthly = sorted(Counter([date for date in dates]).items(), reverse=True)

	yearly_dict = OrderedDict()
	for i in yearly:
		year = i[0]
		yearly_dict[year] = {}
		yearly_dict[year]['count'] = i[1]
		yearly_dict[year]['months'] = [(j[0][1], j[1])
				for j in monthly if j[0][0] == year]

	return render_template('archive.html', archive=yearly_dict)


@app.route('/archive/<int:year>/')
def yearly_archive(year):
	""" Yearly archive view """
	posts, post_meta = get_posts(year=year, abort=True)
	return render_template('archive_page.html', tag=year, year=year, posts=posts)


@app.route('/archive/<int:year>/<int:month>/')
def monthly_archive(year, month):
	""" Monthly archive view """
	date_string = date_tostring(year, month, format='%b %Y')
	posts, post_meta = get_posts(year=year, month=month, abort=True)
	return render_template('archive_page.html', tag=date_string, year=year,
			month=month, posts=posts)


@app.route('/recent.atom')
def recent_feed():
	""" Atom feed generator """
	feed = AtomFeed('Recent Articles',
					feed_url=request.url, url=request.url_root)
	posts, max_page = get_posts()
	feed_limit = config.SITE.get('feed_limit', 10)

	for post in posts[:feed_limit]:
		dated = datetime.datetime.fromtimestamp(int(post.meta['timestamp']))
		updated = dated
		if post.meta.get('updated'):
			updated = datetime.datetime.fromtimestamp(int(post.meta['updated']))

		feed.add(post.meta.get('title'), unicode(post.html),
					content_type='html',
					author=post.meta.get('author', config.SITE.get('author', '')),
					url=urljoin(request.url_root, post.path[11::]),
					updated=updated,
					published=dated)

	return feed.get_response()


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
	""" XML sitemap generator """
	pages = []

	# Set last updated date for static pages as 10 days before
	ten_days_ago = (datetime.datetime.now() -
		datetime.timedelta(days=10)).date().isoformat()

	# Add static pages
	for rule in app.url_map.iter_rules():
		if ("GET" in rule.methods and len(rule.arguments) == 0 and
			rule.rule not in exclude_from_sitemap):
			pages.append([rule.rule, ten_days_ago])

	# Add posts
	posts, max_page = get_posts()

	for post in posts:
		# Get post updation or creation date
		if post.meta.get('updated'):
			updated = datetime.datetime.fromtimestamp(
				int(post.meta['updated'])).date().isoformat()
		else:
			updated = datetime.datetime.fromtimestamp(
				int(post.meta['timestamp'])).date().isoformat()
		# Add posts url
		pages.append([post.path[10::], updated])

	sitemap_xml = render_template('sitemap.xml', pages=pages)
	response = make_response(sitemap_xml)
	response.headers["Content-Type"] = "application/xml"

	return response

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Olaf - because some blogs are worth freezing for.')
	parser.add_argument('-f', '--freeze', action='store_true', help='Freeze site')
	parser.add_argument(
		'-p', '--port', type=int, default=5000,
		help='Port to run app [default: 5000]')
	parser.add_argument(
		'-host', '--host', type=str, default='127.0.0.1',
		help='Port to run app [default: 5000]')
	args = parser.parse_args()

	if args.freeze:
		console_message('Successfully freezed.', 'OKGREEN', newline=True)
		freeze.freeze()
	else:
		app.run(port=args.port, host=args.host)


@click.group()
def cli():
	'''
	Olaf command line utility
	'''
	pass

@cli.command()
@click.option('--theme', default='basic',
	help='blog theme (default: basic)')
@click.option('--port', default=5000,
	help='port to run (default: 5000)')
@click.option('--host', default='127.0.0.1',
	help='hostname to run (default: 127.0.0.1)')
def run(theme, port, host):
	'''
	run olaf local server
	'''
	pass

@cli.command()
@click.option('--theme', default='basic',
	help='blog theme (default: basic)')
@click.argument('path', type=click.Path())
def freeze(theme, path):
	'''
	freeze blog to static files
	'''
	pass

@cli.command()
@click.option('--message', default='new updates',
	help='commit message')
@click.option('--branch', default='master',
	help='branch to be pushed (default: master)')
def upload():
	'''
	Git upload helper
	'''
	pass

@cli.command()
def cname():
	'''
	Update CNAME file
	'''
	pass

@cli.command()
@click.argument('project_name', type=str, required=True)
def createsite(project_name):
	'''
	create a blog
	'''
	pass
