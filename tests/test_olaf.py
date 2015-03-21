import os
import unittest
import random
import string

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
