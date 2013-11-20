#!/usr/bin/env python
#
# Copyright 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Starting template for Google App Engine applications.

Use this project as a starting point if you are just beginning to build a Google
App Engine project. Remember to download the OAuth 2.0 client secrets which can
be obtained from the Developer Console <https://code.google.com/apis/console/>
and save them as 'client_secrets.json' in the project directory.
"""

import os
import logging
import httplib2
import pprint
import random

from apiclient import discovery, errors
from google.appengine.ext.webapp.util import login_required
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache
from handler.email_handler import EmailHandler
from handler.revision_handler import RevisionHandler
from handler.file_id_handler import FileIDHandler

import webapp2
import jinja2

from service import config

from handler import scapes_file_drive
from handler import scapes_revision_drive


class MainHandler(webapp2.RequestHandler):
  @config.decorator.oauth_required
  def get(self):
    self.response.write("Welcome to SCAPES!")

app = webapp2.WSGIApplication(
    [
     ('/', MainHandler),
     ('/email', EmailHandler),
     ('/revisions', RevisionHandler),
     ('/fileids',FileIDHandler),
     (config.decorator.callback_path, config.decorator.callback_handler()),
    ],
    debug=True)
