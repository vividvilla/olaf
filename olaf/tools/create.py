# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~~~

	Commandline utility for creating post/page

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import sys
from datetime import datetime

import click

from olaf import contents_dir, posts_dir, pages_dir, get_current_dir, \
	content_extension
from olaf.utils import slugify, create_directory


def get_confirmation(message, fallback='error', fg=''):
	"""
	Get user get_confirmation
	"""
	click.secho(message + ' (y/n) : ', nl=False, fg=fg)
	choice = click.getchar()
	click.echo()
	if choice == 'y':
		return True
	elif choice == 'n':
		return False
	else:
		if fallback == 'error':
			raise ValueError('Invalid type')
		else:
			return fallback


def retry(force_retry=False, fallback=None,
	retry_message='do you want to retry?', return_check=None):
	"""
	Decorator which helps to repeat a teask untill the function returns true output
	"""
	def retry_decorator(func):
		def decorated_function(*args, **kwargs):
			while True:
				retry = False
				result = func(*args, **kwargs)
				if not result == return_check:
					return result
				elif force_retry:
					retry = True
				else:
					try:
						retry = get_confirmation(retry_message, fg='cyan')
					except ValueError:
						retry = True

				if not retry:
					return fallback
			return func(*args, **kwargs)
		return decorated_function
	return retry_decorator


@retry(force_retry=True)
def get_content_type():
	click.secho('Choose content type (page or post): ', nl=False)
	choice = raw_input()

	if choice not in ('post', 'page'):
		click.secho('Invalid content type, should be either '
			'"page" or "post"', fg='red')
		return None
	else:
		return choice


@retry()
def get_content_title():
	click.secho('Choose content title: ', nl=False)
	choice = raw_input()

	if not choice:
		click.secho('Invalid content title', fg='red')
		return None
	return choice


@retry(force_retry=True)
def get_content_slug():
	click.secho('Choose content slug(will also be the file name): ', nl=False)
	choice = raw_input()

	if not choice:
		click.secho('Invalid slug', fg='red')
		return None
	return choice


def get_content_summary():
	click.secho('Choose content summary (optional): ', nl=False)
	choice = raw_input()
	return choice


@retry(return_check='retry', fallback='')
def get_content_tags():
	click.secho('Choose post tags, comma seperated (ex. tag1, tag2) : ', nl=False)
	tags_string = raw_input()

	if not tags_string:
		return ''

	try:
		tags = [i.strip() for i in tags_string.split(',')]
	except ValueError:
		click.secho('Invalid tags format', fg='red')
		return 'retry'
	else:
		return tags


@retry(fallback=datetime.now().date())
def get_date():
	"""
	Utility for getting date via Commandline
	"""

	set_date = get_confirmation('Set todays date?')

	# Return current date if user asks for it
	if set_date:
		return datetime.now().date()

	click.secho('Custom date in the format of "Year, Month, Day" '
		'(ex: 2015, 1, 12): ', nl=False)
	date_string = raw_input()

	try:
		year, month, day = [int(i.strip()) for i in date_string.split(',')]
		date = datetime(year, month, day).date()
	except ValueError:
		click.secho('Invalid date format', fg='red')
		return None
	else:
		return date


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
		try:
			slug_from_title = get_confirmation(
				'Create a slug from content title?')
		except ValueError:
			slug_from_title = False

	slug = None
	if slug_from_title:
		slug = slugify(title)

	if not slug:
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
	if data.get('date'):
		date_string = data['date'].strftime('%Y-%m-%d')

	content_meta = {
		'date': date_string,
		'title': data.get('title'),
		'summary': data.get('summary', '')
	}

	if data['type'] == 'post':
		content_directory = os.path.join(
			get_current_dir(), contents_dir, posts_dir)
		content_path = os.path.join(
			content_directory, data['slug'] + content_extension)
		content_meta['tags'] = str(data.get('tags', []))
	elif data['type'] == 'page':
		content_directory = os.path.join(
			get_current_dir(), contents_dir, pages_dir)
		content_path = os.path.join(
			content_directory, data['slug'] + content_extension)
	else:
		raise ValueError('Invalid content type "{}"'.format(data['type']))

	# If file exists ask for a overwrite
	overwrite = False
	if os.path.exists(content_path):
		click.secho('File already exists with file name (slug)',
			fg='yellow')

		overwrite = get_confirmation('Do you want to over write the '
			'existing content?')

		if not overwrite:
			click.secho('Aborted', fg='yellow')
			sys.exit(0)

	try:
		create_directory(content_directory)
	except Exception as e:
		click.secho('unable to create content directory : {}'.format(e),
			fg='red')
		sys.exit(0)

	# Write post meta to file
	try:
		with open(content_path, 'wb+') as f:
			for meta_key, meta_value in content_meta.iteritems():
				f.write(meta_key + ': ' + meta_value + '\n')
			f.write('\n' + 'Your content goes here, Happy blogging !!!')
	except Exception as e:
		raise
		click.secho('unable to create content : {}'.format(e),
			fg='red')
		sys.exit(0)

	click.secho('Successfully created content at : {} '
		'you can preview it on url /{}'.format(content_path, data['slug']),
		fg='green')

	# Open created file in preferred text editor
	open_file = get_confirmation(
		'Want to open the file in a text editor?', fallback=False)

	if open_file:
		click.secho('Please enter your preferred text editor '
				'(vim, vi, nano, subl, etc.. : ', nl=False)
		text_editor = raw_input()

		try:
			click.edit(filename=content_path, editor=text_editor)
		except:
			click.secho('Unable to open the file in given text editor', fg=False)


def verbose_create():
	"""
	Initiate detailed post creation process
	"""
	create(get_input())


def quick_create(type, slug):
	"""
	create post or page quickly with some sensible defaults
	"""
	create(dict(
		type=type,
		date=datetime.now(),
		slug=slugify(slug),
		title='Hello world',
		)
	)
