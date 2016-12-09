Olaf
====

Olaf is a simple static site generator written on Python. You can run
dynamic blog locally and freeze it as static pages which can be hosted
anywhere including Github.

`Demo blog <http://olaf.vivekr.net>`__
--------------------------------------

Features
--------

-  Markdown support
-  Content types (Posts and pages)
-  Custom content slug
-  Custom home page
-  Tags and Archives list
-  Synatx highlighting
-  Disqus comments
-  XML sitemap
-  Atom feed
-  Google Analytics integration
-  Custom themes
-  Commandline tool for content creation
-  Host it on Github

Get started
-----------

1. Install from pip

   ::

       pip install getolaf

2. Create a blog

   ::

       olaf createsite myblog

3. Change directory to ``myblog`` and Run dev server

   ::

       olaf run --port 3000

4. Freeze the current version

   ::

       olaf freeze

5. Create content via Commandline

   ::

       olaf create

Contents are stored as a markdown formatted files in ``_contents``
folder. Markdown files can be directly edited to modify existing
contents.

What to do next
---------------

You can edit site settings such as title, description etc from
``config.py`` file.

Features in pipeline
--------------------

-  Ghost/WordPress like GUI content creator/editor
-  Admin tools
-  Themes ecosystem
-  Migration tools for popular blog such as WordPress
-  PDF Generator (Publish entire site as a ebook)
