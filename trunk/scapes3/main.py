#!/usr/bin/env python

""" SCAPES app. Analyzes a list of google documents.

bit.ly/scapescode
bit.ly/scapeseng"""

import webapp2
from handler.index_handler import IndexHandler
from service import config

app = webapp2.WSGIApplication(
    [
        ('/', IndexHandler),
        (config.decorator.callback_path, config.decorator.callback_handler()),
    ],
    debug=True)

