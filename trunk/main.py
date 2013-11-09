import ConfigParser
import gdata.docs.client
import gdata.gauth
import jinja2
import os
import webapp2
import diff_match_patch.diff_match_patch

import config

from scapesother import MainPage
from scapesother import GoogleWebmasterVerify
from scapesother import Fetcher
from scapesother import RequestTokenCallback
from scapesother import FetchCollection
from scapesother import RequestRawRevision
from scapesother import TestNaren
from scapesother import TestTristan
from scapesother import TestFoster
from scapesother import TestJonathan
from scapesother import TestHelio
from scapesasync import AsyncExampleRequestHandler
from scapesasync import CounterWorker
from scapesresource import RequestAResource
from scapesother import RequestARawRevision
from scapesrevision import RequestARevision
from scapesexport import CsvExportRequestHandler
from scapesmanualtests import ScapesManualTests
from step3 import FetchRevision
from step4 import RequestRevision
from folderexport import FolderExportRequestHandler

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Configure gdata
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
SETTINGS = {
  'APP_NAME': config.get('gdata_settings', 'APP_NAME'),
  'CONSUMER_KEY': config.get('gdata_settings', 'CONSUMER_KEY'),
  'CONSUMER_SECRET': config.get('gdata_settings', 'CONSUMER_SECRET'),
  'SCOPES': [config.get('gdata_settings', 'SCOPES')]
}

gdocs = gdata.docs.client.DocsClient(source = SETTINGS['APP_NAME'])
gdiff = diff_match_patch.diff_match_patch()


# TODO(mcupino): Maybe find out how to have the GoogleWebmasterVerify
# automatically route to the html page?
app = webapp2.WSGIApplication([('/', MainPage),
    ('/google910e6da758dc80f1.html', GoogleWebmasterVerify),
    ('/step1', Fetcher),
    ('/step2', RequestTokenCallback),
    ('/step3', FetchRevision),
    ('/step4', RequestRevision),
    ('/collections', FetchCollection),
    ('/raw', RequestRawRevision),
    ('/requestAResource', RequestAResource),
    ('/requestARawRevision', RequestARawRevision),
    ('/requestARevision', RequestARevision),
    ('/asyncExample', AsyncExampleRequestHandler),
    ('/worker', CounterWorker),
    ('/csv', CsvExportRequestHandler),
    ('/folderexport', FolderExportRequestHandler),
    ('/runTest', ScapesManualTests),
    ('/naren', TestNaren),
    ('/tristan', TestTristan),
    ('/foster', TestFoster),
    ('/jonathan', TestJonathan),
    ('/helio', TestHelio)],
    debug=True)
