Run the tests with PyCharm, it will add the parent folder to $PYTHONPATH, and then the import line will work.

The old way was:

python -m unittest mkrspc_web_tests

That doesn't work because the tests are now in a subfolder and can't import
the web app python file from their parent folder.

Well, they could, if they were treated as a python module.

The test script could then do a relative import:

import ..mkrpc_web_app

But then PyCharm's testrunner wouldn't work, because it passes in the script name.

So another way to run them without PyCharm would be:

 cd mkrspc_web
 ln -s tests/mkrspc_web_tests.py

 Now this will work:

 python -m unittest mkrspc_web_tests
