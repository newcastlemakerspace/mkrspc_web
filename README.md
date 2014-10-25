mkrspc_web
==========

A small website with basic wiki functionality, using the bottle microframework.

It uses Redis to store user and wiki data. The 'fixed' pages are HTML fragments in the 'content' directory.


TODO

~~Backups of the Redis data store~~
Restore backups of the Redis data store
Image/file/media gallery, so we can store stuff to share
Wiki improvements
Revisions
Allow deletion of pages, categories
Allow moving/renaming pages/categories
Human readable wiki category URLs (no UUIDs)
Beautification
Tags



To run locally for development
-----

Install Debian / Ubuntu packages:

redis-server python-redis python-bottle markdown

Copy site_config.example.py to site_config.py and edit to suit your machine.

python mkrspc_web_app.py

