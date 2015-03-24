# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~

	Flask main app

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import sys
import shutil

import click

default_theme = 'basic'
module_path = os.path.dirname(os.path.abspath(__file__))
contents_dir = '_contents'
posts_dir = 'posts'
pages_dir = 'pages'
content_extension = '.md'


def get_current_dir():
	return os.getcwd()


def is_valid_path(path):
	"""
	check if path exists
	"""
	if not os.path.exists(path):
		click.secho(
			'path "{}" does not exist'.format(path), fg='red')
		raise OSError('path "{}" does not exist'.format(path))
	return True


def is_valid_site():
	"""
	check if the current path is a valid site directory
	"""
	config_path = os.path.join(get_current_dir(), 'config.py')

	# check if inside site directory
	if not os.path.exists(config_path):
		click.secho(
			'Cannot find config file, please make sure'
			' you are inside the site directory', fg='red')
		raise OSError('Cannot find config file, please make sure'
			' you are inside the site directory')
	return True


def get_themes_list(path):
	"""
	Get list of themes from a given themes path
	"""
	if not os.path.exists(path):
		child_dir = []
	else:
		child_dir = os.walk(path).next()[1]

	valid_themes = []
	for dir in child_dir:
		if (os.listdir(os.path.join(path, dir))
			and not dir.startswith('.')):
			valid_themes.append(
				dict(name=dir, path=os.path.join(path, dir)))
	return valid_themes


def get_theme_by_name(theme):
	# get list of inbuilt themes
	inbuilt_themes = get_themes_list(os.path.join(module_path, 'themes'))
	# get list of custom themes
	custom_themes = get_themes_list(os.path.join(get_current_dir(), 'themes'))

	# check for theme in inbuilt themes directory
	theme_exists_in_inbuilt = [
		item['name'] for item in inbuilt_themes if item['name'] == theme]

	# check for theme in custom themes directory
	theme_exists_in_custom = [
		item['name'] for item in custom_themes if item['name'] == theme]

	theme_path = None

	if theme_exists_in_inbuilt:
		# If theme in bundled themes list then get from default themes directory
		theme_path = os.path.join(module_path, 'themes', theme)
	elif theme_exists_in_custom:
		# If theme not found in bundled themes then get from sites directory
		theme_path = os.path.join(get_current_dir(), 'themes', theme)

	return theme_path


def get_default_theme_name(theme):
	"""
	get theme from config or set it default
	"""

	# return theme name if its set via commandline argument
	if theme:
		return theme

	# load config file
	config_path = os.path.join(get_current_dir(), 'config.py')
	sys.path.append(os.path.dirname(os.path.expanduser(config_path)))
	import config

	# If theme specified as option then ignore other rules
	# else get from config file, if not found in config file set default theme
	if config.SITE.get('theme'):
		return config.SITE['theme']
	else:
		return default_theme


def create_project_site(project_name):
	try:
		# create project directory
		os.mkdir(os.path.join(get_current_dir(), project_name))
	except OSError:
		raise

	try:
		# copy config file
		shutil.copyfile(
			os.path.join(module_path, 'config-sample.py'),
			os.path.join(get_current_dir(), project_name, 'config.py'))
	except IOError:
		raise

	try:
		# create init file
		open(
			os.path.join(get_current_dir(), project_name, '__init__.py'), 'a'
		).close()
		# disqus file
		open(
			os.path.join(get_current_dir(), project_name, 'disqus.html'), 'a'
		).close()
		# create contents directory
		os.mkdir(os.path.join(get_current_dir(), project_name, contents_dir))
		os.mkdir(
			os.path.join(get_current_dir(), project_name, contents_dir, posts_dir))
		os.mkdir(
			os.path.join(get_current_dir(), project_name, contents_dir, pages_dir))
	except OSError:
		raise

	return True
