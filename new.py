# Inteface for creating pages

"""
yet to do

Warn about duplicate slug
"""

import os
import sys
from distutils import util
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
	# Initial header messages
	console_message('\nCreate new content', 'HEADER')
	console_message('\nYou can always change these settings later \n',
			'OKBLUE', upper = False)

	# Get page type
	console_message('Set content type', 'OKBLUE')
	page_type = raw_input('\nEnter page type (post/page)'
			'[default: post]: ') or 'post'

	if not page_type in ('post', 'page'):
		console_message('Invalid page type.', 'FAIL')
		sys.exit()

	# Get creation date
	console_message('Set content creation date', 'OKBLUE')
	created_date = get_date()

	# Get title
	console_message('Set content title', 'OKBLUE')
	title = raw_input('\nEnter title : ')

	create_slug = True
	if title:
		create_slug = util.strtobool(raw_input('\nWant to create custom post slug ? \n'
				'(else it will create from post title you have provided) [default: no] \n'
				'Enter your choice: (y/n): ') or 'n')
	else:
		title = 'My awesome post title'

	if create_slug:
		# Get page file name
		console_message('Set content slug', 'OKBLUE')
		while True:
			filename = raw_input('\nEnter slug (required) : ')
			if filename:
				filename = filename.strip().replace(' ', '-')
				break
			else:
				console_message('Page filename is a required field, '
						'Please try again.', 'WARNING')
	else:
		filename = title.strip().replace(' ', '-')

	# Get summary
	console_message('Set content summary', 'OKBLUE')
	summary = raw_input('\nEnter {} summary : '.format(page_type))

	# Get tags (post specific fields)
	if page_type == 'post':
		console_message('Set post tags', 'OKBLUE')
		raw_tags = raw_input('\nPost tags with comma seperated : ') or ''
		try:
			tags = [i.strip() for i in raw_tags.split(',')]
		except ValueError as e:
			console_message(e.message, 'FAIL', upper = False)

	return (page_type, created_date, filename, title, summary, tags)

def console_message(message, type, upper = True):
	if upper:
		message = message.upper()

	sys.stdout.write(bcolors[type] + bcolors['BOLD'] +
			'\n' + message + bcolors['ENDC'])

def get_date():
	set_date = util.strtobool(
		raw_input('\nSet as current date ? (y/n): ') or 'y')

	# Return current date
	if set_date:
		return datetime.now()

	# Loop till user opts out or provides valid date
	while True:
		retry = False
		post_date = None

		date = raw_input('\nCustom date in the format of "Year, Month, Day" '
				'(ex: 2015, 1, 12): ')
		time = raw_input('\nTime in the format of "Hour Minutes"'
				'(ex: 10, 55) : ') or '0 0'

		try:
			year, month, day = [int(i.strip()) for i in date.split(',')]
			hour, minutes = [int(i.strip()) for i in time.split(',')]
			post_date = datetime(year, month, day, hour, minutes)
		except ValueError as e:
			console_message(e.message, 'FAIL', upper = False)
			retry = util.strtobool(raw_input('\nWant to re-enter the date '
					'(Current date will be set if not) ? (y/n): ') or 'n')
		if retry:
			pass
		else:
			return post_date or datetime.now()

def create_directory(path):
	create_path = 'contents/' + path
	if not os.path.isdir(create_path):
		os.makedirs(create_path)
	return create_path

def create_post():
	page_type, date, filename, title, summary, tags = get_input()

	# Lis of post meta
	post_meta = [('type', page_type), ('timestamp', date.strftime('%s')),
			('title', title), ('summary', summary)]

	if page_type == 'post':
		# If its a post then add tags
		path = create_directory(date.strftime('%Y/%m/%d/'))
		post_meta.append(('tags', str(tags)))
	elif page_type == 'page':
		# It its a page then create file in contents directory
		path = 'contents/'

	# Fina file path
	full_path = path + filename + '.md'

	overwrite = False
	if os.path.exists(full_path):
		console_message('File already exists with same date and same name',
				'WARNING')
		overwrite = util.strtobool(raw_input('\nDo you want to over write the '
				'existing post ? (y/n): ') or 'n')

		if not overwrite:
			console_message('Aborted. ', 'WARNING')
			return None

	# Write post meta to file
	with open(full_path, 'wb+') as f:
		for meta in post_meta:
			f.write((meta[0] + ': ' + meta[1] or '') + ' \n')
		f.write('\n\n' + 'Your content goes here, Happy blogging !!!')

	console_message('Successfully created post at {}. '.format(full_path.strip()),
			'OKGREEN')

def update_post():
	pass

if __name__ == '__main__':
	create_post()
