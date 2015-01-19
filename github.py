import os
import sys
import argparse

import config

""" Shell script colors """
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

def update_cname():
	""" Create CNAME file or update if its defined
		in settings else delete CNAME file """

	if config.SITE.get('github_domain'):
		f = open('build/CNAME', 'w+')
		f.write(config.SITE['github_domain'])
		f.close()
		print 'CNAME updated'
	else:
		try:
			os.remove('build/CNAME')
		except OSError:
			pass

def upload(commit, branch):
	""" """
	if not os.path.isdir("build/.git"):
		print bcolors['OKGREEN'] + 'Initializing git repo' + bcolors['ENDC']
		git_init()

	add_commit_push(commit, branch)
	print bcolors['OKGREEN'] + 'completed' + bcolors['ENDC']

def git_init():
	""" If not .git folder in build/ directory,
		initialize git and add git remote url """

	if config.SITE.get('github_repo'):
		os.system('cd build && git init && git remote add origin {} && cd ..'.format(
				config.SITE['github_repo']))
	else:
		""" Exit if git remote ulr not defined in settings """
		print (bcolors['FAIL'] + "You need to add github repo "
					"url in config file" + bcolors['ENDC'])
		exit()

def add_commit_push(message, branch):
	os.system('cd build && git add .')
	os.system('cd build && git commit -m "{}"'.format(message))
	os.system('cd build && git pull origin {repo} && git push origin {repo}'.format(
			repo = branch))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Frog Github helper')
	parser.add_argument('-m', type=str, default='blog updated',
			help='commit message')
	parser.add_argument('-b', type=str, default='master',
			help='Git branch')
	parser.add_argument('-c', action='store_true', help='CNAME update')

	args = parser.parse_args()

	if args.c:
		update_cname()
	else:
		upload(args.m, args.b)
