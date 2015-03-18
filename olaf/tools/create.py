# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~~~

	Simple commandline utility for creating post/page

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import sys
import argparse
from distutils import util
from datetime import datetime

import click

from olaf.utils import bcolors, console_message, \
	create_directory, get_unix_time


# Detailed post creator
def get_input():
	"""
	Utility for getting content meta data via Commandline

	returns user specified data:
		content_type : 'post' or 'page'
		created_date : current date or user specified date
		title: content title
		slug/filename : taken from title if user hasn't specified
		summary : conten summary
		tags : applicable only to 'post' content type
	"""

	# Initial header messages
	click.secho('Create new content', fg='white', bg='blue')

	# Get page type
	click.secho('Set content type', fg='white', bg='blue')
	page_type = raw_input('\nEnter page type (post/page)'
			'[default: post]: ') or 'post'

	if page_type not in ('post', 'page'):
		click.secho('Invalid content type.', fg='red')
		sys.exit(0)

	# Get creation date
	click.secho('Set content date', fg='white', bg='blue')
	created_date = get_date()

	# Get title
	click.secho('Set content title', fg='white', bg='blue')
	title = raw_input('\nEnter title : ')
	create_slug = True  # By default dont take slug from title

	# Prompt user for a custom slug or create it from title
	if title:
		create_slug = util.strtobool(raw_input(
			'\nWant to create custom post slug ? \n'
			'(else it will create from post title you have provided) [default: no] \n'
			'Enter your choice: (y/n): ') or 'n')
	else:
		title = 'Title of your new content'

	# Get slug
	if create_slug:
		# Get page file name
		click.secho('Set content slug', fg='white', bg='blue')
		while True:
			filename = raw_input('\nEnter slug (required) : ')
			if filename:
				filename = filename.strip().replace(' ', '-')
				break
			else:
				click.secho('Page filename is a required field, '
						'Please try again.', fg='yellow')
	else:
		filename = title.strip().replace(' ', '-')

	# Get summary
	click.secho('Set content summary', fg='white', bg='blue')
	summary = (raw_input('\nEnter {} summary : '.format(page_type)) or
			'Summary of your new content in few words')

	# Get tags (post specific fields)
	if page_type == 'post':
		click.secho('Set post tags', fg='white', bg='blue')
		raw_tags = raw_input('\nPost tags with comma seperated : ') or ''
		try:
			tags = [i.strip() for i in raw_tags.split(',')]
		except ValueError as e:
			click.secho(e.message, fg='red')

	return (page_type, created_date, filename, title, summary, tags)


def get_date():
	"""
	Utility for getting date via Commandline
	"""

	set_date = util.strtobool(
		raw_input('\nSet as current date ? (y/n): ') or 'y')

	# Return current date if user asks for it
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
			click.secho(e.message, fg='red')
			retry = util.strtobool(raw_input('\nWant to re-enter the date '
					'(Current date will be set if not) ? (y/n): ') or 'n')
		if retry:
			pass
		else:
			return post_date or datetime.now()


def create(data):
	"""
	Create a content with provided date

	'data' contains list/tuple of
		content_type
		date
		filename
		title
		summary
		tags [can be empty]
	"""

	page_type, date, filename, title, summary, tags = data

	# Lis of post meta
	post_meta = [('type', page_type), ('timestamp', date.strftime('%s')),
			('updated', date.strftime('%s')), ('title', title), ('summary', summary)]

	if page_type == 'post':
		# If its a post then add tags
		path = create_directory(config.FLATPAGES_ROOT + date.strftime('/%Y/%m/%d/'))
		post_meta.append(('tags', str(tags)))
	elif page_type == 'page':
		# It its a page then create file in contents directory
		path = config.FLATPAGES_ROOT + '/'

	# Fina file path
	full_path = path + filename + config.FLATPAGES_EXTENSION

	# If file exists ask for a overwrite
	overwrite = False
	if os.path.exists(full_path):
		click.secho('File already exists with same date and same name',
			fg='yellow')
		overwrite = util.strtobool(raw_input('\nDo you want to over write the '
				'existing post ? (y/n): ') or 'n')

		if not overwrite:
			click.secho('Aborted', fg='yellow')
			return None

	# Write post meta to file
	with open(full_path, 'wb+') as f:
		for meta in post_meta:
			f.write((meta[0] + ': ' + meta[1] or '') + ' \n')
		f.write('\n' + 'Your content goes here, Happy blogging !!!')

	click.secho('Successfully created post at : {}'.format(full_path),
		fg='green')

	# Open created file in preferred text editor
	open_file = util.strtobool(raw_input('\nDo you want to open the file '
		'in your preferred text editor ? (y/n): ') or 'n')

	if open_file:
		text_editor = raw_input('\nPlease enter your preferred text editor '
				'(vim, vi, nano, subl, etc.. : ')

		if text_editor:
			os.system('{} {}'.format(text_editor, full_path))


def create_manually():
	create(get_input())


def quick_create(type, filename):
	filename = filename.strip().replace(' ', '-')
	create((type, datetime.now(), filename,
			'My new post', 'Summary of my new post', []))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Olaf Commandline content creator')
	parser.add_argument(
		'-post', type=str, help='Quickly create a post [required: slug/filename]')
	parser.add_argument(
		'-page', type=str, help='Quickly create a page [required: slug/filename]')
	parser.add_argument(
		'-t', '--time', action='store_true', help='Get unix time')

	args = parser.parse_args()

	if args.post:
		quick_create('post', args.post)
	elif args.page:
		quick_create('page', args.page)
	elif args.time:
		console_message(get_unix_time(), 'OKGREEN')
	else:
		create_manually()
