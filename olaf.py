# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~~~

	Olaf command line utility

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import sys
import shutil

import click

import blog
from utils import slugify

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
current_path = os.getcwd()
default_theme = 'basic'


def check_path(path):
	"""
	check if path exists
	"""
	if not os.path.exists(path):
		click.secho(
			'path "{}" does not exist'.format(path), fg='red')
		sys.exit(0)


def check_valid_site():
	"""
	check if the current path is a valid site directory
	"""
	config_path = os.path.join(current_path, 'config.py')

	# check if inside site directory
	if not os.path.exists(config_path):
		click.secho(
			'Cannot find config file, please make sure'
			' you are inside the site directory', fg='red')
		sys.exit(0)


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
	inbuilt_themes = get_themes_list(os.path.join(dir_path, 'themes'))
	# get list of custom themes
	custom_themes = get_themes_list(os.path.join(current_path, 'themes'))

	# check for theme in inbuilt themes directory
	theme_exists_in_inbuilt = [
		item['name'] for item in inbuilt_themes if item['name'] == theme]

	# check for theme in custom themes directory
	theme_exists_in_custom = [
		item['name'] for item in custom_themes if item['name'] == theme]

	theme_path = None

	if theme_exists_in_inbuilt:
		# If theme in bundled themes list then get from default themes directory
		theme_path = os.path.join(dir_path, 'themes', theme)
	elif theme_exists_in_custom:
		# If theme not found in bundled themes then get from sites directory
		theme_path = os.path.join(current_path, 'themes', theme)

	return theme_path


def get_default_theme_name(theme):
	"""
	get theme from config or set it default
	"""

	# return theme name if its set via commandline argument
	if theme:
		return theme

	# load config file
	config_path = os.path.join(current_path, 'config.py')
	sys.path.append(os.path.dirname(os.path.expanduser(config_path)))
	import config

	# If theme specified as option then ignore other rules
	# else get from config file, if not found in config file set default theme
	if config.SITE.get('theme'):
		return config.SITE.get('theme')
	else:
		return default_theme


def create_project_site(project_name):
	try:
		# create project directory
		os.mkdir(project_name)
	except OSError as e:
		click.secho('Error while creating site - {}'.format(e), fg='red')
		sys.exit(0)

	try:
		# copy config file
		shutil.copyfile(
			os.path.join(dir_path, 'config-sample.py'),
			os.path.join(current_path, project_name, 'config.py'))
	except IOError:
		click.secho('Error while creating site - {}'.format(e), fg='red')
		sys.exit(0)

	try:
		# create init file
		open(
			os.path.join(current_path, project_name, '__init__.py'), 'a'
		).close()
		# disqus file
		open(
			os.path.join(current_path, project_name, 'disqus.html'),
			'a'
		).close()
		# create contents directory
		os.mkdir(os.path.join(current_path, project_name, '_contents'))
		os.mkdir(
			os.path.join(current_path, project_name, '_contents', 'posts'))
		os.mkdir(
			os.path.join(current_path, project_name, '_contents', 'pages'))
	except OSError:
		click.secho(
			'Error while creating site - {}'.format(e), fg='red')
		sys.exit(0)


@click.group()
def cli():
	"""
	Olaf command line utility
	"""
	pass


@cli.command()
@click.argument('project_name', type=str, required=True)
@click.option('-d', '--demo', type=bool, default=True)
def createsite(project_name, demo):
	"""
	create a blog
	"""
	project_name = slugify(project_name)  # santize project name
	create_project_site(project_name)
	click.secho('site "{}" has been successfully created'.format(
		project_name), fg='green')

	# populate demo files (True by default)
	if demo:
		shutil.copyfile(
			os.path.join(dir_path, 'demo-files', 'hello-world.md'),
			os.path.join(
				current_path, project_name, '_contents',
				'posts', 'hello-world.md'))

		shutil.copyfile(
			os.path.join(dir_path, 'demo-files', 'typography.md'),
			os.path.join(
				current_path, project_name, '_contents',
				'posts', 'typography.md'))

		shutil.copyfile(
			os.path.join(dir_path, 'demo-files', 'sample-page.md'),
			os.path.join(
				current_path, project_name, '_contents',
				'pages', 'sample-page.md'))

	click.secho('demo files successfully populated', fg='green')


@cli.command()
@click.option(
	'-t', '--theme', help='blog theme (default: basic)')
@click.option(
	'-p', '--port', default=5000, help='port to run (default: 5000)')
@click.option(
	'-h', '--host', default='localhost',
	help='hostname to run (default: localhost)')
def run(theme, port, host):
	"""
	run olaf local server
	"""

	# check for a valid site directory
	check_valid_site()

	# get specified theme path
	theme_name = get_default_theme_name(theme)
	theme_path = get_theme_by_name(theme_name)
	if not theme_path:
		# sepcified theme not found
		click.secho(
			'Sepcified theme "{}" not found'.format(theme_name), fg='red')
		sys.exit(0)

	try:
		app = blog.create_app(current_path, theme_path)
		app.run(port=port, host=host)
	except ValueError as e:
		click.secho(e, fg='red')


@cli.command()
@click.option(
	'-t', '--theme', default='basic', help='blog theme (default: basic)')
@click.option(
	'-p', '--path', default='',
	help='Freeze directory (default: current directory)')
@click.option(
	'-s', '--static', default=False, type=bool, help='Freeze with relative urls'
	'(Run without web server) (default: False)')
def freeze(theme, path, static):
	"""
	freeze blog to static files
	"""
	# check for a valid site directory
	check_valid_site()

	# get specified theme path
	theme_name = get_default_theme_name(theme)
	theme_path = get_theme_by_name(theme_name)
	if not theme_path:
		# sepcified theme not found
		click.secho(
			'Sepcified theme "{}" not found'.format(theme_name), fg='red')
		sys.exit(0)

	if path:
		path = os.path.join(current_path, slugify(path))
	else:
		path = current_path

	try:
		# create app
		app = blog.create_app(
			current_path,
			theme_path,
			freeze_path=path,
			freeze_static=static)
		blog.freeze.freeze()

		if not os.path.exists(os.path.join(path, '.nojekyll')):
			open(os.path.join(path, '.nojekyll'), 'a').close()

		click.secho('successfully freezed app', fg='green')
	except ValueError as e:
		click.secho(e, fg='red')


@cli.command()
@click.option(
	'-p', '--path', default='',
	help='Directory where site has been freezed (default: current directory)')
@click.option(
	'-m', '--message', default='new update', help='commit message')
@click.option(
	'-b', '--branch', default='master',
	help='branch to be pushed (default: master)')
def upload(path, message, branch):
	"""
	Git upload helper
	"""
	full_path = os.path.join(current_path, path)
	check_path(os.path.join(current_path, path))

	import upload
	upload.upload(full_path, message, branch)


@cli.command()
@click.option(
	'-p', '--path', default='',
	help='Directory where site has been freezed (default: current directory)')
def cname(path):
	"""
	Update CNAME file
	"""
	full_path = os.path.join(current_path, path)
	check_path(os.path.join(current_path, path))

	import upload
	upload.update_cname(full_path)


@cli.command()
@click.option(
	'-p', '--pygments-styles', count=True, help='Get list of pygments styles')
@click.option(
	'-i', '--inbuilt-themes', count=True, help='Get list of inbuilt themes')
@click.option(
	'-t', '--themes', count=True, help='Get list of all themes')
def utils(pygments_styles, inbuilt_themes, themes):
	"""
	olaf utils
	"""

	if pygments_styles:
		from pygments.styles import STYLE_MAP
		styles = STYLE_MAP.keys()
		click.secho('list of pygments styles', fg='cyan')
		for style in styles:
			if style == 'tango':
				click.echo('tango' + click.style(' (default)', fg='green'))
			else:
				click.echo(style)

	if inbuilt_themes or themes:
		inbuilt_themes_list = get_themes_list(os.path.join(dir_path, 'themes'))

		click.secho('list of inbuilt themes', fg='blue', bold=True)
		for theme in inbuilt_themes_list:
			if theme['name'] == 'basic':
				click.secho(
					' - ' + theme['name'] + click.style(' (default)', fg='green'))
			else:
				click.echo(theme['name'])

			if not inbuilt_themes_list:
				click.secho(' - no inbuilt themes available', fg='red')

		if themes:
			custom_themes_list = get_themes_list(
				os.path.join(current_path, 'themes'))
			click.secho('list of custom themes', fg='blue', bold=True)
			for theme in custom_themes_list:
				click.echo(' - ' + theme['name'])

			if not custom_themes_list:
				click.secho(' - no custom themes available', fg='red')


@cli.command()
def importer():
	"""
	Importer tools
	"""
	pass


@cli.command()
def export():
	"""
	Export tools
	"""
	pass
