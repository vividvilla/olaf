# -*- coding: utf-8 -*-
"""
    Olaf
    ~~~~~~~~~

    Tools used all around the project, independent of any other module in project.

    :copyright: (c) 2015 by Vivek R.
    :license: BSD, see LICENSE for more details.
"""

import os
import sys
import datetime

#Shell script colors
bcolors = {
	"HEADER": "\033[95m",
	"OKBLUE": "\033[94m",
	"OKGREEN": "\033[92m",
	"WARNING": "\033[93m",
	"FAIL": "\033[91m",
	"ENDC": "\033[0m",
	"BOLD": "\033[1m",
	"UNDERLINE": "\033[4m"
}

# Colored std out messages
def console_message(message, type,
			upper = True, newline = False):
	if upper:
		message = message.upper()

	if type:
		sys.stdout.write(bcolors[type] + bcolors['BOLD'] + '\n' +
				message + bcolors['ENDC'] + '\n' if newline else '')
	else:
		sys.stdout.write('\n' + message + '\n' if newline else '')

# Create a directory recursively
def create_directory(path):
	if not os.path.isdir(path):
		os.makedirs(path)
	return path

def get_unix_time():
	date = get_date()
	return date.strftime('%s')

def timestamp_tostring(timestamp, format = '%d %m %Y'):
	#Converts unix timestamp to date string with given format
	return datetime.datetime.fromtimestamp(
			int(timestamp)).strftime(format)

def date_tostring(year, month, day = 1, format = '%d %b %Y'):
	#Returns date string for given year, month and day with given format
	date = datetime.datetime(int(year), int(month), int(day))
	return date.strftime(format)

def font_size(min, max, high, n):
	# Calculate font size for tags
	return (n/high)*(max-min) + min