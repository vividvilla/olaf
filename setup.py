from setuptools import setup

setup(
	name= 'olaf',
	version= '1.0.0',
	pymodules= ['olaf'],
	install_requires= [
		'Click'
	],
	entry_points = '''
		[console_scripts]
		olaf=olaf:cli
	'''
)
