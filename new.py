# Inteface for creating pages

"""
Page type : post/page

if page:
	pass

if post:
	creation time: default now else choose:
		date : '%Y %m %d'
		Hour : default current
		minutes : default current
	tags: with , default empty
	title: default empty
	summary: default empty

if page:
	title:
	creation time:


tool to update creation or updation date
"""

import sys
from datetime import datetime

#Shell script colors
bcolors = {
	"HEADER": "\033[95m",
	"OKBLUE": "\033[94m",
	"OKGREEN": "\033[92m",
	"WARNING": "\033[93m",
	"FAIL": "\033[91m",
	"ENDC": "\033[0m",
	"BOLD": "\033[1m",
	"UNDERLINE": "\033[4m"
}

def get_input():
	console_message('\n'*2 + 'Create new content', 'HEADER')
	console_message('='*18, 'HEADER')
	console_message('You can always change these settings later',
			'OKBLUE', upper = False)
	console_message('-'*45 + '\n', 'OKBLUE')

	console_message('Set content type', 'OKBLUE')
	page_type = raw_input('Enter page type (post/page)'
			' [default: post]: ') or 'post';
	print '\n'

	if not page_type in ('post', 'page'):
		console_message('Invalid page type.', 'FAIL')
		sys.exit()

	console_message('Set content creation date', 'OKBLUE')
	created_date = get_date()
	print '\n'

	console_message('Set content title', 'OKBLUE')
	title = raw_input('Enter title : ')
	print '\n'

	console_message('Set content summary', 'OKBLUE')
	summary = raw_input('Enter {} summary : '.format(page_type))
	print '\n'

	if page_type == 'post':
		console_message('Set post tags', 'OKBLUE')
		raw_tags = raw_input('Post tags with comma seperated : ') or ''
		tags = [i.strip() for i in raw_tags.split(',')]

def console_message(message, type, upper = True):
	if upper:
		message = message.upper()

	print (bcolors[type] + bcolors['BOLD'] + message + bcolors['ENDC'])

def get_date():
	set_date = raw_input('Set as current date ? (y/n): ') or 'y'

	if set_date == 'y':
		return datetime.now()

	while True:
		retry = None
		post_date = None

		date = raw_input('Custom date in the format of "Year, Month, Day" '
				'(ex: 2015, 1, 12): ')
		time = raw_input('Time in the format of "Hour Minutes"'
				'(ex: 10, 55) : ') or '0 0'

		try:
			year, month, day = [int(i.strip()) for i in date.split(',')]
			hour, minutes = [int(i.strip()) for i in time.split(',')]

			post_date = datetime(year, month, day, hour, minutes)
		except ValueError as e:
			print bcolors['FAIL'] + e.message + bcolors['ENDC']
			retry = raw_input('Want to re-enter the date (Current date will be '
					'set if not) ? (y/n): ')

		if retry == 'y':
			pass
		else:
			return post_date or datetime.now()

def create_post():
	pass

def update_post_date():
	pass

if __name__ == '__main__':
	get_input()
