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
import datetime
import argparse

import click

import blog
from utils import console_message, slugify

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
current_path = os.getcwd()
default_themes = ['basic']

def create_project_site(project_name):
	try:
		# create project directory
		os.mkdir(project_name)
	except OSError as e:
		click.secho('Error while creating site - {}'.format(e),
			fg='red')
		sys.exit(0)

	try:
		# copy config file
		shutil.copyfile(
			os.path.join(dir_path, 'config-sample.py'),
			os.path.join(current_path, project_name, 'config.py'))
	except IOError:
		click.secho('Error while creating site - {}'.format(e),
			fg='red')
		sys.exit(0)

	try:
		# create init file
		open(os.path.join(current_path, project_name, '__init__.py'),
			'a').close()
		# disqus file
		open(os.path.join(current_path, project_name, 'disqus.html'),
			'a').close()
		# create contents directory
		os.mkdir(os.path.join(current_path, project_name, '_contents'))
		os.mkdir(os.path.join(current_path, project_name, '_contents', 'posts'))
		os.mkdir(os.path.join(current_path, project_name, '_contents', 'pages'))
	except OSError:
		click.secho('Error while creating site - {}'.format(e),
			fg='red')
		sys.exit(0)

@click.group()
def cli():
	'''
	Olaf command line utility
	'''
	pass

@cli.command()
@click.argument('project_name', type=str, required=True)
@click.option('--demo', type=bool, default=True)
def createsite(project_name, demo):
	'''
	create a blog
	'''

	project_name = slugify(project_name) # santize project name
	create_project_site(project_name)
	click.secho('site "{}" has been successfully created'.format(
		project_name), fg='green')

	# populate demo files (True by default)
	if demo:
		shutil.copyfile(
			os.path.join(dir_path, 'demo-files', 'hello-world.md'),
			os.path.join(current_path,
				project_name, '_contents', 'posts', 'hello-world.md'))

		shutil.copyfile(
			os.path.join(dir_path, 'demo-files', 'typography.md'),
			os.path.join(current_path,
				project_name, '_contents', 'posts', 'typography.md'))

		shutil.copyfile(
			os.path.join(dir_path, 'demo-files', 'sample-page.md'),
			os.path.join(current_path,
				project_name, '_contents', 'pages', 'sample-page.md'))

	click.secho('demo files successfully populated', fg='green')

@cli.command()
@click.option('--theme', default='basic',
	help='blog theme (default: basic)')
@click.option('--port', default=5000,
	help='port to run (default: 5000)')
@click.option('--host', default='127.0.0.1',
	help='hostname to run (default: 127.0.0.1)')
def run(theme, port, host):
	'''
	run olaf local server
	'''
	config_path = os.path.join(current_path, 'config.py')

	# check if inside site directory
	if not os.path.exists(config_path):
		click.secho('Cannot find config file, please make sure'
			' you are inside the site directory', fg='red')
		sys.exit(0)

	# get theme directory
	if theme in default_themes:
		# If theme in bundled themes list then get from default themes directory
		theme_path = os.path.join(dir_path, 'themes', theme)
	else:
		# If theme not found in bundled themes then get from sites directory
		theme_path = os.path.join(current_path, 'themes', theme)

	contents_path = os.path.join(current_path, '_contents')

	# create app
	app = blog.create_app(config_path,
		theme_path, contents_path, current_path)
	app.run(port=port, host=host)

@cli.command()
@click.option('--theme', default='basic',
	help='blog theme (default: basic)')
@click.argument('path', type=click.Path())
def freeze(theme, path):
	'''
	freeze blog to static files
	'''
	pass

@cli.command()
@click.option('--message', default='new updates',
	help='commit message')
@click.option('--branch', default='master',
	help='branch to be pushed (default: master)')
def upload():
	'''
	Git upload helper
	'''
	pass

@cli.command()
def cname():
	'''
	Update CNAME file
	'''
	pass

@cli.command()
def utils():
	'''
	olaf utils
	'''
	pass

@cli.command()
def importer():
	'''
	Importer tools
	'''
	pass

@cli.command()
def export():
	'''
	Export tools
	'''
	pass


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Olaf - because some blogs are worth freezing for.')
	parser.add_argument('-f', '--freeze', action='store_true', help='Freeze site')
	parser.add_argument(
		'-p', '--port', type=int, default=5000,
		help='Port to run app [default: 5000]')
	parser.add_argument(
		'-host', '--host', type=str, default='127.0.0.1',
		help='Port to run app [default: 5000]')
	args = parser.parse_args()

	if args.freeze:
		console_message('Successfully freezed.', 'OKGREEN', newline=True)
		freeze.freeze()
	else:
		app.run(port=args.port, host=args.host)
