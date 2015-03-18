# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~~~

	Simple commandline utility for creating post/page

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import argparse
from datetime import datetime
from functools import wraps

import click

from olaf.utils import slugify, \
	create_directory


def get_confirmation(message):
	click.secho(message + ' (y/n) : ', nl=False)
	choice = click.getchar()
	if choice == 'y':
		return True
	elif choice == 'n':
		return False
	else:
		raise ValueError('Invalid type')


def retry_option(func):
	@wraps(func)
	def decorated_function(*args, **kwargs):
		fallback = None
		retry_message = 'do you want to retry?'
		while True:
			retry = False
			result = func(*args, **kwargs)
			if result:
				return result
			else:
				try:
					retry = get_confirmation(retry_message)
				except ValueError:
					retry = True

			if not retry:
				return fallback
		return func(*args, **kwargs)
	return decorated_function


@retry_option
def get_content_type():
	click.secho('\nChoose content type (page or post): ', nl=False)
	choice = raw_input()
	if choice not in ('post', 'page'):
		click.secho('Invalid content type, should be either '
			'"page" or "post"', fg='red')
		return None
	else:
		return choice


@retry_option
def get_content_title():
	click.secho('\nChoose content title: ', nl=False)
	choice = raw_input()
	if not choice:
		click.secho('Invalid content title', fg='red')
	return choice


@retry_option
def get_content_slug():
	click.secho('\nChoose content slug(will also be the file name): ', nl=False)
	choice = raw_input()
	if not choice:
		click.secho('Invalid slug', fg='red')
	return choice


@retry_option
def get_content_summary():
	click.secho('\nChoose content summary (optional): ', nl=False)
	choice = raw_input()
	if not choice:
		click.secho('Invalid content summary', fg='red')
	return choice


@retry_option
def get_content_tags():
	click.secho('\nPost tags with comma seperated : ', nl=False)
	tags_string = raw_input()
	try:
		tags = [i.strip() for i in tags_string.split(',')]
	except ValueError:
		click.secho('Invalid tags format', fg='red')
		return None
	else:
		return tags


def get_date():
	"""
	Utility for getting date via Commandline
	"""

	set_date = get_confirmation('\nSet todays date?')

	# Return current date if user asks for it
	if set_date:
		return datetime.today()

	# Loop till user opts out or provides valid date
	while True:
		retry = False

		click.secho('\nCustom date in the format of "Year, Month, Day" '
			'(ex: 2015, 1, 12): ', nl=False)
		date_string = raw_input()

		try:
			year, month, day = [int(i.strip()) for i in date_string.split(',')]
			date = datetime(year, month, day).today()
		except ValueError as e:
			click.secho(e.message, fg='red')
			retry = get_confirmation('\nWant to re-enter the date '
					'(Current date will be set if not)?')
		else:
			return date

		if not retry:
			return datetime.now().today()


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

	# Get page type
	content_type = get_content_type()

	# Get creation date
	created_date = get_date()

	# Get title
	title = get_content_title()

	# get slug
	if not title:
		slug_from_title = False
		title = 'hello world'
	else:
		slug_from_title = get_confirmation('\nCreate a slug from content title?')

	slug = None
	if slug_from_title:
		slug = slugify(title)

	if not slug_from_title or slug:
		get_slug = get_content_slug()
		if get_slug:
			slug = slugify(get_content_slug())

	# get content summary
	summary = get_content_summary()

	# Get tags (post specific fields)
	if content_type == 'post':
		tags = get_content_tags()

	return dict(
		type=content_type,
		date=created_date,
		slug=slug,
		title=title,
		summary=summary,
		tags=tags)


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
	pass
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
"""
