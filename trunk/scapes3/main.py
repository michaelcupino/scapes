#!/usr/bin/env python

""" SCAPES app. Analyzes a list of google documents.

bit.ly/scapescode
bit.ly/scapeseng"""

import webapp2

from handler.document_revisions_mr_handler import DocumentRevisionsMRHandler
from handler.email_map_reduce_handler import EmailMapReduceHandler
from handler.folder_prototype_handler import FolderPrototypeHandler
from handler.index_handler import IndexHandler
from service import config

app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/emailmr', EmailMapReduceHandler),
    (r'/documentmr/(.*)/revisions', DocumentRevisionsMRHandler),
    (r'/folder/(.*)', FolderPrototypeHandler),
    (config.decorator.callback_path, config.decorator.callback_handler()),
], debug=True)

