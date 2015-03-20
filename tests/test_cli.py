import os
import random
import shutil
import unittest
import string

import click
from click.testing import CliRunner

from olaf import cli, contents_dir, posts_dir
from olaf.utils import change_dir

class TestCli(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	@staticmethod
	def get_random_string():
		return ''.join(random.choice(
			string.ascii_lowercase + string.digits) for _ in range(10))

	def test_createsite(self):

		runner = CliRunner()
		with runner.isolated_filesystem():
			self.assertNotEqual(
				runner.invoke(cli.createsite).exit_code, 0)

		# check with demo
		with runner.isolated_filesystem():
			site_name = self.get_random_string()
			result = runner.invoke(cli.createsite, [site_name])

			self.assertEqual(result.exit_code, 0)

			project_path = os.path.join(os.getcwd(), site_name)
			posts_path = os.path.join(project_path, contents_dir, posts_dir)

			config_path = os.path.join(project_path, 'config.py')
			self.assertTrue(os.path.exists(config_path))

			# try to create again
			recreate = runner.invoke(cli.createsite, [site_name])
			self.assertEqual(recreate.exit_code, 1)


			# check for created directory
			self.assertTrue(os.path.isdir(project_path))

			# check for demo files
			self.assertGreater(len(os.listdir(posts_path)), 0)


		# check without demo
		with runner.isolated_filesystem():
			site_name = self.get_random_string()
			result = runner.invoke(
				cli.createsite, [site_name, '--demo', False])

			self.assertEqual(result.exit_code, 0)

			project_path = os.path.join(os.getcwd(), site_name)
			posts_path = os.path.join(project_path, contents_dir, posts_dir)

			# check for created directory
			self.assertTrue(os.path.isdir(project_path))

			# check for demo files
			self.assertEqual(len(os.listdir(posts_path)), 0)


	def test_run(self):
		runner = CliRunner()
		with runner.isolated_filesystem():
			self.assertEqual(
				runner.invoke(cli.run).exit_code, 1)

		# check with demo
		with runner.isolated_filesystem():
			site_name = self.get_random_string()
			site = runner.invoke(cli.createsite, [site_name])
			self.assertEqual(site.exit_code, 0)

			project_path = os.path.join(os.getcwd(), site_name)

			# change dir to project and run
			with change_dir(project_path):
				result = runner.invoke(cli.run)
				self.assertEqual(result.exit_code, 0)

				with_invalid_theme = runner.invoke(cli.run,
					['--theme', 'invalid-theme'])
				self.assertEqual(with_invalid_theme.exit_code, 1)

				# need to write test for __init__ functions first
				os.makedirs(os.path.join(project_path, 'themes', site_name))
				with_valid_theme = runner.invoke(cli.run,
					['--theme', site_name])
				self.assertEqual(with_valid_theme.exit_code, 0)

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
