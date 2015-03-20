import os
import random
import shutil
import unittest

import click
from click.testing import CliRunner

from olaf import cli
from olaf.utils import change_dir

class TestCli(unittest.TestCase):
	def setUp(self):
		self.current_dir = os.path.dirname(os.path.abspath(__file__))
		self.temp_dir = os.path.join(self.current_dir, 'tmp')

	def tearDown(self):
		# if temp_dir created then delete it
		if os.path.isdir(self.temp_dir):
			shutil.rmtree(self.temp_dir)

	def test_createsite(self):
		os.mkdir(self.temp_dir)

		runner = CliRunner()
		with change_dir(self.temp_dir):
			self.assertNotEqual(
				runner.invoke(cli.createsite).exit_code, 0)

			result = runner.invoke(cli.createsite, ['samplesite'])
			self.assertEqual(result.exit_code, 0)

	def test_run(self):
		pass

	def test_freeze(self):
		pass

	def test_git(self):
		pass

	def test_cname(self):
		pass

	def test_utils(self):
		pass

	def test_content_create(self):
		pass

	def test_quick_content_create(self):
		pass

	def test_importer(self):
		pass

	def test_exporter(self):
		pass
