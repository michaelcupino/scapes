#!/usr/bin/env python

""" SCAPES app. Analyzes a list of google documents.

bit.ly/scapescode
bit.ly/scapeseng"""

import webapp2
from handler.folder_prototype_handler import FolderPrototypeHandler
from handler.index_handler import IndexHandler
from handler.email_map_reduce_handler import EmailMapReduceHandler
from service import config

app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    (r'/folder/(.*)', FolderPrototypeHandler),
    ('/emailmr', EmailMapReduceHandler),
    (config.decorator.callback_path, config.decorator.callback_handler()),
], debug=True)

