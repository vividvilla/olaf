# -*- coding: utf-8 -*-
"""
	site.py
	~~~~~~~

	Flask main app

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import datetime
from urlparse import urljoin
from collections import Counter, OrderedDict

from flask import Flask
from flask_frozen import Freezer
from werkzeug.contrib.atom import AtomFeed
from flask import render_template, abort, redirect, url_for, \
	request, make_response, current_app, Blueprint, send_from_directory
from flask_flatpages import FlatPages, pygments_style_defs

from olaf import contents_dir, content_extension, get_current_dir
from olaf.utils import timestamp_tostring, date_tostring, \
	font_size, date_format, create_directory

# initialize extensions
freeze = Freezer()
contents = FlatPages()

app = Blueprint('app', __name__)  # create blueprint

exclude_from_sitemap = []  # List of urls to be excluded from XML sitemap


def create_app(current_path, theme_path, **kwargs):
	"""
	Create app with dynamic configurations
	"""
	flask_app = Flask(
		__name__,
		template_folder=os.path.join(theme_path, 'templates'),
		static_folder=os.path.join(theme_path, 'static'))

	# update configurations
	flask_app.config.from_pyfile(os.path.join(
		current_path, 'config.py'))

	freeze_path = current_path
	if kwargs.get('freeze_path'):
		freeze_path = kwargs['freeze_path']

	freeze_static = False
	if kwargs.get('freeze_static'):
		freeze_static = True

	flask_app.config.update(
		current_path=current_path,
		FREEZER_DESTINATION=freeze_path,
		FREEZER_RELATIVE_URLS=freeze_static,
		FREEZER_REMOVE_EXTRA_FILES=False,
		FLATPAGES_AUTO_RELOAD=True,
		FLATPAGES_EXTENSION=content_extension,
		FLATPAGES_ROOT=os.path.join(current_path, contents_dir))

	# initialize with current flask app
	contents.init_app(flask_app)
	freeze.init_app(flask_app)

	# Register blueprint as root
	flask_app.register_blueprint(app)

	# check for duplicate slugs
	check_duplicate_slugs(contents)

	# filter contents for posts and pages only
	filter_valid_contents(contents)

	with flask_app.app_context():
		# Set home page
		flask_app.add_url_rule('/', 'app.index', get_index())

		# Register utility functions to be used in jinja2 templates
		flask_app.jinja_env.globals.update(
			timestamp_tostring=timestamp_tostring,
			date_tostring=date_tostring,
			font_size=font_size,
			content_type=check_content_type,
			date_format=date_format,
			config=current_app.config)

	return flask_app


def filter_valid_contents(contents):
	"""
	filter contents to only post and pages and
	add url attribute to individual content.
	"""
	contents = [post for post in contents if (
		post.path.startswith('posts/') or
		post.path.startswith('pages/'))]

	for post in contents:
		if(post.path.startswith('posts/')
			or post.path.startswith('pages/')):
			post.slug = post.path[6:]


def check_content_type(path, content_type):
	"""
	check for specific content type
	"""
	if content_type == 'post':
		if path.startswith('posts/'):
			return True

	if content_type == 'page':
		if path.startswith('pages/'):
			return True

	return False


def check_duplicate_slugs(contents):
	"""
	check for duplicate slugs
	"""
	slugs = []
	for post in contents:
		slug = ''
		if post.path.startswith('pages/'):
			slug = post.path.split('pages/')[1]
		elif post.path.startswith('posts/'):
			slug = post.path.split('posts/')[1]

		if slug and slug in slugs:
			raise ValueError('Duplicate slug : {}'.format())


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

	posts = [post for post in contents if (
		post.path.startswith('posts/') and
		post.meta.get('date') and
		post.meta.get('title'))]

	# import pdb; pdb.set_trace()

	# Filter conditions

	# Sort posts by timestamp (True by default)
	sort = filters.get('sort', True)
	if(sort):
		posts.sort(
			key=lambda x: x.meta['date'],
			reverse=filters.get('reverse', True))

	# Filter based on tag
	tag = filters.get('tag')
	if(tag):
		posts = [post for post in posts
			if tag in (post.meta.get('tags') or [])]

	# Filter based on year and month
	year = filters.get('year')
	if(year):
		posts = [post for post in posts
			if post.meta['date'].year == year]

		# Filter by month only if year is given
		month = filters.get('month')
		if month:
			posts = [post for post in posts
				if post.meta['date'].month == month]

	# Get total number of posts without pagination
	post_meta = {}
	post_meta['total_pages'] = len(posts)

	# Filter based on page number and pagination limit
	page_no = filters.get('page_no')
	limit = filters.get('limit') or current_app.config['SITE']['limit'] or 10
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


def get_post_by_slug(slug):
	"""
	filter contents by slug
	"""
	content = [post for post in contents if post.slug == slug]
	return content


"""
Views
"""


@app.route('/404.html')
def custom_404():
	"""
	custom 404 page view
	"""
	return render_template('404.html')


@app.route('/pygments.css')
def pygments_css():
	"""
	default pygments style
	"""
	pyments_style = current_app.config['SITE'].get('pygments_style') or 'tango'
	return (pygments_style_defs(pyments_style), 200, {'Content-Type': 'text/css'})

exclude_from_sitemap.append('/pygments.css')  # Excludes url from sitemap


@app.route('/assets/<path:filename>')
def custom_static(filename):
	"""
	custom assets folder
	"""
	# custom assets folder
	assets_path = os.path.join(
		get_current_dir(),
		current_app.config['SITE'].get('assets') or 'assets')

	# create assets folder if not there
	if not os.path.exists(assets_path):
		create_directory(assets_path)

	return send_from_directory(assets_path, filename)


def get_index():
	"""
	check if custom home page set else return default index view
	"""
	if current_app.config['SITE'].get('custom_home_page'):
		content = get_post_by_slug(current_app.config['SITE']['custom_home_page'])

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
	"""
	default index view
	"""
	posts, post_meta = get_posts(page_no=1)
	return render_template('index.html',
		page_no=1, posts=posts, next_page=post_meta['max_pages'] > 1)


def custom_index():
	"""
	custom home page view
	"""
	content = get_post_by_slug(current_app.config['SITE']['custom_home_page'])
	content[0].meta['type'] = 'page'
	return render_template('content.html', content=content[0])


@app.route('/pages/<int:page_no>/')
def pagination(page_no):
	"""
	home page pagination view
	"""
	# Redirect if it is a first page (except when custom home page is set)
	if page_no == 1 and not current_app.config['SITE'].get('custom_home_page'):
		return redirect(url_for('.index'))

	posts, post_meta = get_posts(page_no=page_no, abort=True)
	return render_template('index.html', page_no=page_no,
			posts=posts, next_page=(post_meta['max_pages'] > page_no),
			previous_page=(page_no > 1))


@app.route('/<path:slug>/')
def posts(slug):
	"""
	individual post/page view
	"""
	content = get_post_by_slug(slug)

	if not content:
		abort(404)  # Slug not found both in pages and posts

	# Exception if duplicates found
	if len(content) > 1:
		raise Exception('Duplicate slug')

	disqus_html = ''
	disqus_file_path = os.path.join(current_app.config['current_path'], 'disqus.html')
	with open(disqus_file_path, 'r') as f:
		disqus_html = f.read()

	return render_template('content.html', content=content[0],
		disqus_html=disqus_html)


# Tag views

@app.route('/tags/')
def tags():
	"""
	list of tags view
	"""
	# import pdb; pdb.set_trace()
	tags = [tag for post in contents if post.meta.get('tags')
		for tag in post.meta['tags']]

	tags = sorted(Counter(tags).items())  # Count tag occurances

	max_occ = 0 if not tags else max([tag[1] for tag in tags])

	return render_template('tags.html', tags=tags, max_occ=max_occ)


@app.route('/tags/<string:tag>/')
def tag_page(tag):
	"""
	individual tag view
	"""
	posts, post_meta = get_posts(tag=tag, page_no=1, abort=True)
	return render_template('tag.html', tag=tag, posts=posts,
			page_no=1, next_page=(post_meta['max_pages'] > 1),
			len = post_meta['total_pages'])


@app.route('/tags/<string:tag>/pages/<int:page_no>/')
def tag_pages(tag, page_no):
	"""
	pagination for Individual tags
	"""
	posts, post_meta = get_posts(tag=tag, page_no=page_no, abort=True)

	# Redirect if it is a first page
	if page_no == 1:
		return redirect(url_for('.tag_page', tag=tag))

	return render_template('tag.html', tag=tag, posts=posts,
			page_no=page_no, next_page=(post_meta['max_pages'] > page_no),
			len = post_meta['total_pages'], previous_page=(page_no > 1))


@app.route('/list/posts/')
def list_posts():
	"""
	all posts list view
	"""
	return render_template("list_posts.html", posts=get_posts()[0])


@app.route('/list/pages/')
def list_pages():
	"""
	all pages list view
	"""
	pages = [page for page in contents
				if page.path.startswith('pages/')]

	return render_template("list_pages.html", pages=pages)


@app.route('/archive/')
def archive():
	"""
	date based archive view
	"""
	# Get all posts dates in format (year, month)
	dates = [(post.meta['date'].year, post.meta['date'].month)
			for post in contents if post.meta.get('date')]

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
	"""
	yearly archive view
	"""
	posts, post_meta = get_posts(year=year, abort=True)
	return render_template('archive_page.html', tag=year, year=year, posts=posts)


@app.route('/archive/<int:year>/<int:month>/')
def monthly_archive(year, month):
	"""
	monthly archive view
	"""
	date_string = date_tostring(year, month, format='%b %Y')
	posts, post_meta = get_posts(year=year, month=month, abort=True)
	return render_template('archive_page.html', tag=date_string, year=year,
			month=month, posts=posts)


@app.route('/recent.atom')
def recent_feed():
	"""
	atom feed generator
	"""
	posts, max_page = get_posts()
	feed_limit = current_app.config['SITE'].get('feed_limit', 10)

	domain_url = current_app.config['SITE'].get('domain_url')
	if not domain_url:
		domain_url = request.url_root

	feed = AtomFeed('Recent Articles',
					url=domain_url,
					feed_url=urljoin(domain_url, '/recent.atom'),
					id=urljoin(domain_url, '/recent.atom'))

	for post in posts[:feed_limit]:
		dated = post.meta['date']
		updated = dated
		if post.meta.get('updated'):
			updated = post.meta['updated']

		# if its a date object convert to datetime object
		# since tzinfo needed to create feeds
		if isinstance(updated, datetime.date):
			updated = datetime.datetime.combine(
				updated, datetime.datetime.min.time())

		if isinstance(dated, datetime.date):
			dated = datetime.datetime.combine(
				dated, datetime.datetime.min.time())

		feed.add(
			post.meta.get('title'),
			unicode(post.html),
			content_type='html',
			author=post.meta.get(
				'author', ', '.join(
					current_app.config['SITE'].get('author', []))),
			url=urljoin(domain_url, post.slug),
			updated=updated,
			published=dated,
			xml_base=urljoin(domain_url, '/recent.atom'))

	return feed.get_response()


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
	"""
	XML sitemap generator
	"""
	resources = []

	# Set last updated date for static pages as 10 days before
	ten_days_ago = (
		datetime.datetime.now() -
		datetime.timedelta(days=10)).date().isoformat()

	# import pdb; pdb.set_trace()

	domain_url = current_app.config['SITE'].get('domain_url')
	if not domain_url:
		domain_url = request.url_root

	# Add static pages
	for rule in current_app.url_map.iter_rules():
		if ("GET" in rule.methods and len(rule.arguments) == 0 and
			rule.rule not in exclude_from_sitemap):
			resources.append(
				{
					'url': urljoin(domain_url, rule.rule),
					'modified': ten_days_ago
				}
			)

	# Add posts
	posts, max_page = get_posts()

	for content in contents:
		# Get post update or creation date
		if content.meta.get('updated'):
			updated = content.meta['updated'].isoformat()
		elif content.meta.get('date'):
			updated = content.meta['date'].isoformat()
		else:
			updated = ten_days_ago

		# Add posts url
		resources.append(
			{
				'url': urljoin(domain_url, content.slug),
				'modified': updated
			}
		)

	sitemap_xml = render_template('sitemap.xml', resources=resources)
	response = make_response(sitemap_xml)
	response.headers["Content-Type"] = "application/xml"

	return response
