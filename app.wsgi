APP_CONFIG = "/var/www/blog-app/production.ini"

#Setup Logging
import logging.config
logging.config.fileConfig(APP_CONFIG)

#Load The Application
from paste.deploy import loadapp
application = loadapp('config:%s' % APP_CONFIG)
