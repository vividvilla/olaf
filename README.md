# Olaf

Simple static site generator based on Python. 
Run dynamic blog locally and freeze it as static pages which can be hosted anywhere including Github.

## [Demo blog](http://olaf.vivekr.net)

## Basic features
	- Markdown support
	- Content types (Posts and pages)
	- Custom content slug
	- Custom home page
	- Tags and Archives list
	- Synatx highlighting
	- Disqus comments
	- XML sitemap
	- Atom feed
	- Google Analytics integration
	- Custom themes
	- Commandline tool for content creation
	- Host it on Github
	
## Get started

1. Install from pip

		pip install getolaf
		
2. Create a blog

		olaf createsite myblog

3. Change directory to `myblog` and Run dev server

		olaf run --port 3000

4. Freeze the current version

		olaf freeze

5. Create content via Commandline

		olaf create

Contents are stored as a markdown formatted file at `_contents` folder.
So you can directly edit the markdown files to edit existing contents.

## What to do next

1. You can edit site settings such as title, description etc from `config.py` file.
2. Edit file 

## Features in pipeline
	- Ghost/WordPress like GUI content creator/editor
	- Admin tools
	- Themes ecosystem
	- Migration tools for popular blog such as WordPress
	- PDF Generator (Publish entire site as a ebook)
