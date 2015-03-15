# -*- coding: utf-8 -*-
"""
	Olaf
	~~~~~~~~~

	Github pages uploader utility

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import sys
import click
import subprocess
import argparse

from olaf import current_path
from utils import console_message, change_dir

config_path = os.path.join(current_path, 'config.py')

# check if inside site directory
if not os.path.exists(config_path):
	click.secho(
		'Cannot find config file, please make sure'
		' you are inside the site directory', fg='red')
	sys.exit(0)

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

	if config.SITE.get('github_domain'):
		f = open(os.path.join(path,'CNAME'), 'w+')
		f.write(config.SITE['github_domain'])
		f.close()
		click.secho('CNAME updated', fg='green')
	else:
		try:
			os.remove(os.path.join(path,'CNAME'))
		except OSError:
			pass


def upload(path, commit, branch):
	if not os.path.isdir(os.path.join(path, '.git')):
		click.secho('Initializing git repo', fg='green')
		git_init(path)

	add_commit_push(commit, branch)
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

		if init_status !=0:
			click.secho('Error while intiializing git repo', fg='red')
			sys_exit()
		elif remote_add_status !=0:
			click.secho('Error while addming remote url', fg='red')
			sys_exit()
	else:
		""" Exit if git remote ulr not defined in settings """
		click.secho(
			'You need to add github repo url in config file', fg='red')
		sys_exit()


def add_commit_push(message, branch):
	os.system('cd build && git add .')
	os.system('cd build && git commit -m "{}"'.format(message))
	pull_status = os.system('cd build && git pull origin {repo}'.format(
		repo=branch))

	if pull_status == 256:
		console_message('MERGE CONFLICT', 'FAIL')
		console_message('Discarding remote changes and pushing local changes', '')

		os.system('cd build && git checkout --ours .')
		os.system('cd build && git add -u && git commit -m "{}"'.format(
			"Ignored remote changes"))

	os.system('cd build && git push origin {}'.format(branch))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Olaf Github helper')
	parser.add_argument(
		'-m', '--message', type=str, default='new update', help='commit message')
	parser.add_argument(
		'-b', '--branch', type=str, default='master', help='Git branch')
	parser.add_argument(
		'-c', '--cname', action='store_true', help='CNAME update')

	args = parser.parse_args()

	if args.cname:
		update_cname()
	else:
		upload(args.message, args.branch)
