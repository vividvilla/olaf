# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~~~

	Git and github pages utility tool

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import sys
import click
import subprocess
from urlparse import urlparse

from olaf.utils import change_dir
from olaf import get_current_dir, is_valid_site

config_path = os.path.join(get_current_dir(), 'config.py')

# check for valid site directory
is_valid_site()

# Load config from relative path
sys.path.append(os.path.dirname(os.path.expanduser(config_path)))
import config


def sys_exit():
	sys.exit(0)


def update_cname(path):
	"""
	Create CNAME file or update if its defined in settings
	else delete CNAME file.
	"""

	if config.SITE.get('domain_url'):
		domain_url = urlparse(config.SITE['domain_url']).netloc
		f = open(os.path.join(path, 'CNAME'), 'w+')
		f.write(domain_url)
		f.close()
		click.secho('CNAME updated', fg='green')
	else:
		try:
			os.remove(os.path.join(path, 'CNAME'))
		except OSError:
			pass


def upload(path, message, branch):
	if not os.path.isdir(os.path.join(path, '.git')):
		click.secho('Initializing git repo', fg='green')
		git_init(path)

	add_commit_push(path, message, branch)
	click.secho('Successfully updated recent changes', fg='green')


def git_init(path):
	""" If not .git folder in build/ directory,
		initialize git and add git remote url """

	if config.SITE.get('github_repo'):
		with change_dir(path):
			init_status = subprocess.call(['git', 'init'])
			remote_add_status = subprocess.call(
				['git', 'remote', 'add', 'origin',
				config.SITE['github_repo']])

		if init_status != 0:
			click.secho('Error while intiializing git repo', fg='red')
			sys_exit()
		elif remote_add_status != 0:
			click.secho('Error while addming remote url', fg='red')
			sys_exit()
	else:
		""" Exit if git remote ulr not defined in settings """
		click.secho(
			'You need to add github repo url in config file', fg='red')
		sys_exit()


def add_commit_push(path, message, branch):
	with change_dir(path):
		subprocess.call(['git', 'add', '.'])
		subprocess.call(
			['git', 'commit', '-m', '"{}"'.format(message)])
		status_pull = subprocess.call(['git', 'pull', 'origin', branch])

	if status_pull == 256:
		click.secho('MERGE CONFLICT', fg='red')
		click.secho(
			'Discarding remote changes and pushing local changes',
			fg='yello')

		with change_dir(path):
			subprocess.call(['git', 'checkout', '--ours', '.'])
			subprocess.call(['git', 'add', '-u'])
			subprocess.call(['git', 'commit', '-m',
				'"{}"'.format('Ignored remote changes')])

	subprocess.call(['git', 'push', 'origin', branch])
