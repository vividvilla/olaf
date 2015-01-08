from flask import Flask
from flask import render_template, abort
from flask_flatpages import FlatPages
import config

app = Flask(__name__)
app.config.from_object('config')

#App module initialize
contents = FlatPages(app)

#Routes

#Home page
@app.route('/')
def index():
	posts = sorted([post for post in contents
				if post.meta.get('type', '') == 'post'], reverse = True,
					key = lambda x: x.meta['timestamp'])[:config.SITE['limit']]

	return render_template('index.html', posts=posts)

#For pagination
@app.route('/<int:page_no>/')
def pagination(page_no):
	limit = config.SITE['limit']

	posts = sorted([post for post in contents
				if post.meta.get('type') == 'post'], reverse = True,
					key = lambda x: x.meta['timestamp'])
	paginated = [posts[n:n+limit] for n in range(0, len(posts), limit)]

	try:
		filtered_posts = paginated[page_no]
	except IndexError:
		abort(404)

	return render_template('index.html', posts=filtered_posts)

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

@app.route('/tags/<string:tag>/')
def tags(tag):
	posts = [post for post in contents
				if tag in post.meta.get('tags', [])]

	return render_template('tags.html', tag = tag, posts=posts)

if __name__ == '__main__':
	app.run()
