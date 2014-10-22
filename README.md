mkrspc_web
==========

A small website with basic wiki functionality, using the bottle microframework.

It uses Redis to store user and wiki data. The 'fixed' pages are HTML fragments in the 'content' directory.


To run locally for development
-----

Install Debian / Ubuntu packages:

redis-server python-redis python-bottle

Copy site_config.example.py to site_config.py and edit to suit your machine.

python mkrspc_web_app.py

