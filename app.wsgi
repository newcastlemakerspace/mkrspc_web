
import os

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))

import mkrspc_web_app

# ... build or import your bottle application here ...
# Do NOT use bottle.run() with mod_wsgi
application = mkrspc_web_app.app
