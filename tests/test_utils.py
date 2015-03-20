# -*- coding: utf-8 -*-
"""
	utility tests
	~~~~~~~~~~~~~

	test cases for utility functions

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import shutil
import unittest
import datetime

from olaf import utils


class TestUtils(unittest.TestCase):
	def setUp(self):
		self.current_dir = os.path.dirname(os.path.abspath(__file__))
		self.temp_dir = os.path.join(self.current_dir, 'tmp')
		self.test_dir = os.path.join(self.current_dir, 'tmp/tmp1/tmp2')

	def tearDown(self):
		# if temp_dir created then delete it
		if os.path.isdir(self.temp_dir):
			shutil.rmtree(self.temp_dir)

		# if test_dir created then delete it
		if os.path.isdir(self.test_dir):
			shutil.rmtree(self.test_dir)

	def test_create_directory(self):
		# create directory
		self.assertEqual(
			utils.create_directory(self.test_dir), self.test_dir)

		# check for created directory
		self.assertTrue(os.path.isdir(self.test_dir))

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
		os.mkdir(self.temp_dir)

		with utils.change_dir(self.temp_dir):
			self.assertEqual(self.temp_dir, os.getcwd())
