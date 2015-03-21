# -*- coding: utf-8 -*-
"""
	tests - utility
	~~~~~~~~~~~~~~~

	test cases for utility functions

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import shutil
import random
import string
import unittest
import datetime

import click
from click.testing import CliRunner

from olaf import utils

class TestUtils(unittest.TestCase):
	def setUp(self):
		self.runner = CliRunner()

	def tearDown(self):
		pass

	@staticmethod
	def get_random_string():
		return ''.join(random.choice(
			string.ascii_lowercase + string.digits) for _ in range(10))

	def test_create_directory(self):
		random_string = self.get_random_string()
		with self.runner.isolated_filesystem():
			temp_path = os.path.join(os.getcwd(), random_string)

			# create directory
			self.assertEqual(
				utils.create_directory(temp_path), temp_path)

			# check for created directory
			self.assertTrue(os.path.isdir(temp_path))

	def test_date_tostring(self):
		# default output format
		self.assertEqual(
			utils.date_tostring(2015, 01),
			datetime.datetime(2015, 01, 01).strftime('%d %b %Y'))

		# custom output format
		self.assertEqual(
			utils.date_tostring(2015, 03, 03, format='%d%b%Y'),
			datetime.datetime(2015, 03, 03).strftime('%d%b%Y'))

		# invalid date
		with self.assertRaises(ValueError):
			utils.date_tostring(2015, 33, 33)

	def test_font_size(self):
		# test min case
		self.assertEqual(utils.font_size(100, 200, 100, 0), 100)

		# test max case
		self.assertEqual(utils.font_size(100, 200, 100, 100), 200)

		# test max greater then min and high greater then current value
		with self.assertRaises(ValueError):
			utils.font_size(200, 100, 100, 0)
			utils.font_size(100, 200, 100, 200)

	def test_slugify(self):
		# text with simple string
		self.assertEqual(utils.slugify('some text'), 'some-text')

		# encoding
		self.assertEqual(utils.slugify('正體hello',
			encoding='utf-8'), 'hello')

		# custom permitted chars
		self.assertEqual(utils.slugify('some text',
			permitted_chars='me'), 'mee')

		# special characters
		self.assertEqual(utils.slugify('@#$% ^&*()',
			permitted_chars='@#$%-^&*()'), '@#$%-^&*()')

	def test_change_dir(self):
		random_string = self.get_random_string()
		with self.runner.isolated_filesystem():
			temp_path = os.path.join(os.getcwd(), random_string)
			os.mkdir(temp_path)
			with utils.change_dir(temp_path):
				self.assertEqual(temp_path, os.getcwd())
