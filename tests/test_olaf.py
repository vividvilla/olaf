# -*- coding: utf-8 -*-
"""
	tests - helper functions
	~~~~~~~~~~~~~~~~~~~~~~~~

	test cases for olaf helper function

	:copyright: (c) 2015 by Vivek R.
	:license: BSD, see LICENSE for more details.
"""

import os
import unittest
import random
import string
import sys

import click
from click.testing import CliRunner

import olaf

class TestOlaf(unittest.TestCase):
	def setUp(self):
		self.runner = CliRunner()

	def tearDown(self):
		pass

	@staticmethod
	def get_random_string():
		return ''.join(random.choice(
			string.ascii_lowercase + string.digits) for _ in range(10))

	def test_is_valid_path(self):
		random_string = self.get_random_string()
		with self.runner.isolated_filesystem():
			temp_path = os.path.join(os.getcwd(), random_string)

			with self.assertRaises(OSError):
				olaf.is_valid_path(temp_path)

			os.mkdir(temp_path)
			self.assertTrue(olaf.is_valid_path(temp_path))

	def test_is_valid_site(self):
		with self.runner.isolated_filesystem():
			with self.assertRaises(OSError):
				olaf.is_valid_site()

			open(os.path.join(os.getcwd(), 'config.py'), 'a').close()
			self.assertTrue(olaf.is_valid_site())

	def test_get_themes_list(self):
		with self.runner.isolated_filesystem():
			current_path = os.path.join(os.getcwd())

			# invalid theme path
			self.assertEqual(olaf.get_themes_list(current_path), [])

			# create random number of theme folders
			random_no = random.randint(1, 20)
			for num in range(random_no):
				temp_folder = os.path.join(
					os.path.join(current_path, self.get_random_string()))
				os.mkdir(temp_folder)
				open(os.path.join(temp_folder, 'temp.txt'), 'a').close()

			# check for newly created themes above
			self.assertEqual(
				len(olaf.get_themes_list(current_path)), random_no)

	def test_get_theme_by_name(self):
		# valid theme
		self.assertIsNotNone(olaf.get_theme_by_name('basic'))

		# invalid theme
		self.assertIsNone(olaf.get_theme_by_name(self.get_random_string()))

		with self.runner.isolated_filesystem():
			# create a random theme
			random_theme_name = self.get_random_string()
			current_path = os.path.join(os.getcwd())
			theme_path = os.path.join(current_path, 'themes', random_theme_name)
			os.makedirs(theme_path)
			open(os.path.join(theme_path, 'temp.txt'), 'a').close()

			# check with random theme created above
			self.assertIsNotNone(olaf.get_theme_by_name(random_theme_name))

	def test_create_project_site(self):
		with self.runner.isolated_filesystem():
			random_project_name = self.get_random_string()
			self.assertTrue(olaf.create_project_site(random_project_name))

			files_to_check = ['__init__.py', 'config.py', 'disqus.html',
				olaf.contents_dir,
				os.path.join(olaf.contents_dir, olaf.posts_dir),
				os.path.join(olaf.contents_dir, olaf.pages_dir)]

			for f in files_to_check:
				path = os.path.join(os.getcwd(), random_project_name, f)
				self.assertTrue(os.path.exists(path))

	def test_get_default_theme_name(self):
		random_theme_name = self.get_random_string()
		self.assertEqual(
			olaf.get_default_theme_name(random_theme_name), random_theme_name)

		self.assertEqual(
			olaf.get_default_theme_name(None), olaf.default_theme)

		# with self.runner.isolated_filesystem():
		# 	with open(os.path.join(os.getcwd(), 'config.py'), 'w+') as f:
		# 		f.write('SITE={"theme": "' + random_theme_name + '"}')

		# 	self.assertEqual(
		# 		olaf.get_default_theme_name(None), random_theme_name)
