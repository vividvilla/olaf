from setuptools import setup

setup(
	name='olaf',
	version='1.0.0',
	url='https://github.com/vividvilla/olaf',
	pymodules=['olaf'],
	license='BSD',
	author='Vivek R',
	author_email='vividvilla@gmail.com',
	description='A static site generator based on flask and markdown',
	platforms='any',
	install_requires=[
		'Click',
		'Flask',
		'Flask-FlatPages',
		'Frozen-Flask',
		'Markdown',
		'Pygments'
	],
	classifiers=[
		'Development Status :: 1 - Alpha',
		'Framework :: Flask',
		'Environment :: Console',
		'Environment :: Web Environment',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
	],
	entry_points='''
		[console_scripts]
		olaf=olaf:cli
	'''
)
