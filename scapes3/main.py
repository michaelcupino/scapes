#!/usr/bin/env python

""" SCAPES app. Analyzes a list of google documents.

bit.ly/scapescode
bit.ly/scapeseng"""

import webapp2

from handler.angular_handler import AngularHandler
from handler.document_analysis_handler import DocumentAnalysisHandler
from handler.email_map_reduce_handler import EmailMapReduceHandler
from handler.folder_analysis_handler import FolderAnalysisHandler
from handler.folder_fetcher_handler import FolderFetcherHandler
from handler.folder_prototype_handler import FolderPrototypeHandler
from handler.index_handler import IndexHandler
from handler.layout_handler import LayoutHandler
from handler.revisions_analysis_handler import RevisionsAnalysisHandler
from service import config

app = webapp2.WSGIApplication([
    ('/', LayoutHandler),
    ('/angular', AngularHandler),
    ('/emailmr', EmailMapReduceHandler),
    ('/folder-analysis', FolderAnalysisHandler),
    ('/folder-fetcher', FolderFetcherHandler),
    ('/index', IndexHandler),
    ('/revisions-analysis', RevisionsAnalysisHandler),
    (r'/document-analysis/(.*)', DocumentAnalysisHandler),
    (r'/folder/(.*)', FolderPrototypeHandler),
    (config.decorator.callback_path, config.decorator.callback_handler()),
], debug=True)

