from flask import Flask
from flask import render_template, abort
from flask_flatpages import FlatPages

app = Flask(__name__)
app.config.from_object('config')

#App module initialize
contents = FlatPages(app)

#Routes
@app.route('/')
def index():
	return 'Hello World !!! This is my superblog'

@app.route('/<slug>/')
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

	print content[0].html
	return render_template('page.html',
				page=content[0], site=app.config.get('SITE'))

if __name__ == '__main__':
	app.run()
