from setuptools import setup

README = open('README.md').read()

setup(
	name='getolaf',
	version='1.0.1',
	url='https://github.com/vividvilla/olaf',
	pymodules=['olaf'],
	license='MIT',
	author='Vivek R',
	author_email='vividvilla@gmail.com',
	description='A static site generator based on flask and markdown',
	long_description=README,
	platforms='any',
	install_requires=[
		'Click',
		'Flask',
		'Flask-FlatPages',
		'Frozen-Flask',
		'Markdown',
		'Pygments'
	],
	packages=['olaf', 'olaf.tools'],
	include_package_data=True,
	classifiers=[
		'Framework :: Flask',
		'Environment :: Console',
		'Environment :: Web Environment',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
	],
	entry_points={
		'console_scripts': [
			'olaf = olaf.cli:cli',
			]
		}
)
