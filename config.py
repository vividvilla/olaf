# set flask server to debug mode
DEBUG = True

# site specific settings
SITE = {
	# Required settings

	# Site title
	'title': 'Your blog title',

	# assets folder
	'assets': '',

	# Theme specific settings

	# Site description
	'description': 'Your blog description',

	# Summary length, used by specific themes
	'summary_offset': 180,


	# Optional settings

	# default theme, defaults to 'basic' or theme provided via commandline utility
	# try "olaf utils -t" to get list of inbuilt and custom themes installed
	'theme': '',

	# Default pagination limit, defaults to 10 if not set
	'limit': 10,

	# Site author(s) name
	# used in atom feeds and by themes
	'author': ['Your name'],

	# Set default home page using page/post slug
	# defaults to recent posts list
	'custom_home_page': '',

	# Feeds page limit, defaults to 10 if not set
	'feed_limit': 15,

	# Google analytics tracking id
	# if not set analytics scripts not included (depends on themes)
	'analytics': 'UA-XXX-VVV',

	# Enable or disable disqus comments
	# If enabled add disqus script to disqus.html page in site root
	'disqus': True,

	# Base domain to be used in xm sitemaps and feed urls
	# Please add full url with http or https
	# defaults to host name of the app("localhost")
	'domain_url': 'http://vivek.github.io',

	# enforce SSL
	# if ssl enforced then canonical link will be added and users will redireced to ssl version of the site
	# please make sure domain_url has https:// if its enabled
	'enforce_ssl': False,

	# Sites git url - required if  you are using git uploads commandline tool
	# Try "olaf upload --help" from site root directory for more help
	'github_repo': 'https://github.com/vividvilla/vividvilla.github.io.git',

	# Set syntax highlighting style (pygments styles)
	# Try "olaf utils -p" to get list of inbuilt styles
	'pygments_style': ''

}
