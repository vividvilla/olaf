# -*- coding: utf-8 -*-
"""
	utility.py
	~~~~~~~~~

	common utilitity functions independent of other modules in project.

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import datetime
import contextlib
from unicodedata import normalize


def create_directory(path):
	"""
	create multilevel directories
	"""
	if not os.path.isdir(path):
		try:
			os.makedirs(path)
		except OSError:
			raise
	return path


def timestamp_tostring(timestamp, format='%d %m %Y'):
	"""
	Converts unix timestamp to date string with given format
	"""
	return datetime.datetime.fromtimestamp(
		int(timestamp)).strftime(format)


def date_format(date, format='%d %m %Y'):
	"""
	convert date to string in a given format
	"""
	return date.strftime(format)


def date_tostring(year, month, day=1, format='%d %b %Y'):
	"""
	create date string from year, month and day with given format
	"""
	date = datetime.datetime(int(year), int(month), int(day))
	return date.strftime(format)


def font_size(min, max, high, current_value):
	"""
	calculate font size by min and max occurances
	min - minimum output value
	max - maximum output value
	high - maximum input value
	n - current occurances
	"""
	if max < min:
		raise ValueError('Max cannot be lesser then Min')

	if current_value > high:
		raise ValueError('current_value cannot be greatter then high_value')

	return int((float(current_value) / high) * (max - min) + min)


def slugify(text, encoding=None,
	permitted_chars='abcdefghijklmnopqrstuvwxyz0123456789-'):
	"""
	sanatize string and convert to a url slug
	"""
	if isinstance(text, str):
		text = text.decode(encoding or 'ascii')
	clean_text = text.strip().replace(' ', '-').lower()

	while '--' in clean_text:
		clean_text = clean_text.replace('--', '-')

	ascii_text = normalize('NFKD', clean_text).encode('ascii', 'ignore')
	strict_text = map(lambda x: x if x in permitted_chars else '', ascii_text)

	return ''.join(strict_text)


@contextlib.contextmanager
def change_dir(newPath):
	"""
	mimics unix cd command
	"""
	savedPath = os.getcwd()
	os.chdir(newPath)
	yield
	os.chdir(savedPath)
