import datetime
from collections import Counter, OrderedDict

from flask import Flask
from flask import render_template, abort
from flask_flatpages import FlatPages

import config

app = Flask(__name__)
app.config.from_object('config')

#App module initialize
contents = FlatPages(app)

def timestamp_tostring(timestamp, format):
	#Converts unix timestamp to date string with given format
	return datetime.datetime.fromtimestamp(
			int(timestamp)).strftime(format)

def date_tostring(year, month, day = 1, format = '%d %b %Y'):
	#Returns date string for given year, month and day with given format
	date = datetime.datetime(year, month, day)
	return date.strftime(format)

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

	posts = [post for post in contents
				if post.meta.get('type') == 'post']

	#Filter conditions

	#Sort posts by timestamp (True by default)
	sort = filters.get('sort', True)
	if(sort):
		posts.sort(key = lambda x: x.meta['timestamp'],
					reverse = filters.get('reverse', True))

	#Filter based on tag
	tag = filters.get('tag')
	if(tag):
		posts = [post for post in posts
					if tag in post.meta.get('tags', [])]

	#Filter based on year and month
	year = filters.get('year')
	if(year):
		posts = [post for post in posts if int(timestamp_tostring(
						post.meta.get('timestamp'), '%Y')) == year]

		#Filter by month only if year is given
		month = filters.get('month')
		if month:
			posts = [post for post in posts if int(timestamp_tostring(
							post.meta.get('timestamp'), '%m')) == month]

	#Filter based on page number and pagination limit
	page_no = filters.get('page_no')
	limit = filters.get('limit') or config.SITE['limit']
	if(page_no):
		paginated = [posts[n:n+limit] for n in range(0, len(posts), limit)]
		try:
			posts = paginated[page_no - 1]
		except IndexError:
			posts = []

	#Abort if posts not found
	if(not posts and filters.get('abort') == True):
		abort(404)

	return posts


# All Views

@app.route('/')
def index():
	return render_template('index.html', posts=get_posts(page_no = 1))

@app.route('/pages/<int:page_no>/')
def pagination(page_no):
	#Pagination to homepage
	return render_template('index.html',
			posts=get_posts(page_no = page_no), abort = True)

@app.route('/<path:slug>/')
def posts(slug):
	#Check for slug in root which means pages
	content = [page for page in contents if page.path == slug]

	#Check for slug in posts if not found in pages
	if not content:
		content = [post for post in contents
					if post.path[11::] == slug]

	if not content:
		abort(404) #Slug not found both in pages and posts

	#Exception if duplicates found
	if len(content) > 1:
		raise Exception('Duplicate slug')

	return render_template('page.html', page=content[0])


# Tag views

@app.route('/tags/')
def tags():
	tags = [tag for post in contents
				for tag in post.meta.get('tags', [])]
	tags = dict(Counter(tags)) #Count tag occurances
	return render_template('tags.html', tags = tags)

@app.route('/tags/<string:tag>/')
def tag(tag):
	return render_template('tag.html', tag=tag,
		posts=get_posts(tag=tag, page_no=1, abort=True))

@app.route('/tags/<string:tag>/pages/<int:page_no>/')
def tag_pages(tag, page_no):
	return render_template('tag.html', tag=tag, page_no=page_no,
			posts=get_posts(tag=tag, page_no=page_no, abort=True))

# Archive views

@app.route('/archive/')
def archive():
	# Get all posts dates in format (year, month)
	dates = [(timestamp_tostring(post.meta.get('timestamp'), '%Y'),
			timestamp_tostring(post.meta.get('timestamp'), '%m'))
			for post in contents if post.meta.get('timestamp')]

	# Get sorted yearly archive lists ex: [(year, no_occur), ...]
	yearly = sorted(Counter([date[0] for date in dates]).items(), reverse=True)

	# Get sorted yearly and monthly archive lists [((year, month), no_occur), ...]
	monthly = sorted(Counter([date for date in dates]).items(), reverse=True)

	# Get sorted yearly and monthly formatted archive lists
	# [('date string', (year, month), no_occur), ....]
	monthly = [(date_tostring(int(date[0][0]), int(date[0][1]),
		format='%b %Y'), date[0], date[1]) for date in monthly]

	return render_template('archive.html', yearly=yearly, monthly=monthly)

@app.route('/archive/<int:year>/')
def yearly_archive(year):
	return render_template('tag.html', tag=year,
		posts=get_posts(year=year, page_no=1, abort=True))

@app.route('/archive/<int:year>/pages/<int:page_no>/')
def yearly_archive_pages(year, page_no):
	return render_template('tag.html', tag=year,
		posts=get_posts(year=year, page_no=page_no, abort=True))

@app.route('/archive/<int:year>/<int:month>/')
def monthly_archive(year, month):
	date_string = date_tostring(year, month, format='%b %Y')
	return render_template('tag.html', tag=date_string, month=month,
		posts=get_posts(year=year, page_no=1, abort=True))

@app.route('/archive/<int:year>/<int:month>/pages/<int:page_no>/')
def monthly_archive_pages(year, month, page_no):
	date_string = date_tostring(year, month, format='%b %Y')
	return render_template('tag.html', tag=date_string, month=month,
		posts=get_posts(year=year, page_no=page_no, abort=True))

if __name__ == '__main__':
	app.run()
