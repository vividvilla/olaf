import os
import sys

import config

# Creates CNAME file with custom domain
# Upload /build directory to github repository

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
	if config.SITE.get('github_domain'):
		f = open('build/CNAME', 'w+')
		f.write(config.SITE['github_domain'])
		f.close()
		print 'CNAME updated'
		return True

def upload(commit):
	if not os.path.isdir("build/.git"):
		git_init()
	else:
		print commit
	# os.system('./upload.sh {}'.format(config.SITE['github_repo']))

def git_init():
	if config.SITE.get('github_repo'):
		os.system('cd build && git init && git remote add origin {} && cd ..'.format(
				config.SITE['github_repo']))
	else:
		print (bcolors['FAIL'] + "You need to add github repo "
					"url in config file" + bcolors['ENDC'])
		exit()

def add_commit_push(message = "Usual post update", branch = "master"):
	os.system('./upload.sh')
	# os.system('cd build && git add .')
	# os.system('cd build && git commit -m {}'.format(message))
	# os.system('git pull origin {branch} && git push origin {branch}'.format(
	# 		branch = branch)
	# os.system('cd ..')

if __name__ == '__main__':
	# git_init()
	add_commit_push()
	# if len(sys.argv) > 1:
	# 	if sys.argv[1] == "update_cname":
	# 		update_cname()
	# 	elif sys.argv[1] == "upload":
	# 		try:
	# 			commit_message = sys.argv[2]
	# 		except IndexError:
	# 			commit_message = 'Usual post update'

	# 		upload(commit_message)
