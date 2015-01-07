from flask import Flask
from flask import render_template
from flask_flatpages import FlatPages

app = Flask(__name__)
app.config.from_object('config')

#App module initialize
pages = FlatPages(app)

#Routes
@app.route('/')
def index():
	return 'Hello World !!! This is my superblog'

@app.route('/<path:path>/')
def page(path):
	return render_template('page.html',
		page=pages.get_or_404(path),
		site=app.config.get('SITE'))

if __name__ == '__main__':
	app.run()
