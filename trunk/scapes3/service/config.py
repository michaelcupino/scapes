import os
import logging
import httplib2

import jinja2
import webapp2

from apiclient import discovery, errors
from oauth2client import appengine, client
from google.appengine.api import memcache

# jinja templating environment
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

# client secrets - the location of our authentication keys
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__),
    '../client_secrets.json')

# decorators for oauth2 manipulation
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
  To make this sample run you will need to populate the client_secrets.json file found at:
</p>
<p><code>%s</code>.</p>
<p>
  with information found on the
  <a href="https://code.google.com/apis/console">
    APIs Console
  </a>.
</p>
""" % CLIENT_SECRETS

# the decorator
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=[
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.appdata',
        'https://www.googleapis.com/auth/drive.apps.readonly',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.scripts',
    ],
    message=MISSING_CLIENT_SECRETS_MESSAGE)

http_cache = httplib2.Http(memcache)


service = None
def getService():
  global service
  if not service:
    service = discovery.build('drive', 'v2', http=http_cache)
  return service
    
