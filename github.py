import sys
import config

# Creates CNAME file with custom domain
# Upload /build directory to github repository

def update_cname():
	if config.SITE.get('github_domain'):
		f = open('build/CNAME', 'w+')
		f.write(config.SITE['github_domain'])
		f.close()
		print 'CNAME updated'
		return True

def upload():
	pass

if __name__ == '__main__':
	if len(sys.argv) > 1:
		if sys.argv[1] == "update_cname":
			update_cname()
		elif sys.argv[1] == "upload":
			upload()
