#!/usr/bin/env python

""" SCAPES app. Analyzes a list of google documents.

bit.ly/scapescode
bit.ly/scapeseng"""

import csv
import datetime
import functools
import jinja2
import logging
import pickle
import re
import tempfile
import urllib
import webapp2
import google.appengine.ext.cloudstorage as gcs

from google.appengine.api import files
from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import login_required
from handler.file_id_handler import documents_in_folder
from handler.index_handler import IndexHandler
from handler.revision_analyzer_core import revision_text
from handler.revision_core import retrieve_revisions
from mapreduce import base_handler
from mapreduce import mapreduce_pipeline
from mapreduce import operation as op
from mapreduce import shuffler
from model.file_metadata import FileMetadata
from model.file_model import File
from service import config

def split_into_sentences(s):
  """Split text into list of sentences."""
  s = re.sub(r"\s+", " ", s)
  s = re.sub(r"[\\.\\?\\!]", "\n", s)
  return s.split("\n")


def split_into_words(s):
  """Split a sentence into list of words."""
  s = re.sub(r"\W+", " ", s)
  s = re.sub(r"[_0-9]+", " ", s)
  return s.split()

app = webapp2.WSGIApplication(
    [
        ('/', IndexHandler),
        (config.decorator.callback_path, config.decorator.callback_handler()),
    ],
    debug=True)

def scapes_write_to_blobstore(filename, contents):
  """Create a GCS file with GCS client lib.

  Args:
    filename: GCS filename.

  Returns:
    The corresponding string blobkey for this GCS file.
  """
  # Create a GCS file with GCS client.
  with gcs.open(filename, 'w') as f:
    f.write(contents)

  # Blobstore API requires extra /gs to distinguish against blobstore files.
  blobstore_filename = '/gs' + filename
  # This blob_key works with blobstore APIs that do not expect a
  # corresponding BlobInfo in datastore.
  return blobstore.create_gs_key(blobstore_filename)
  
  
def scapes_analyse_document(data):
  # recall that ASCII 30 is the record separator
  file_id, http = data.split(chr(30))
  http = pickle.loads(http.replace(chr(31),"\n"),0)
  revisions = retrieve_revisions(http, file_id)
  revision_map = functools.partial(scapes_analyze_revision, http, file_id)
  revisions = map(revision_map, revisions)

  # Postprocess code (Serialization etc.?)
  
  yield revisions

def scapes_analyze_reduce(key, values):
  """Word count reduce function."""
  yield "%s: %d\n" % (key, len(values))
  

def scapes_analyze_revision(http, file_id, rev_id):
    text = revision_text(http, file_id, rev_id)
    for s in split_into_sentences(text):
        for w in split_into_words(s.lower()):
            yield (w, "")

class ScapesStoreOutput(base_handler.PipelineBase):
  """A pipeline to store the result of the MapReduce job in the database.

  Args:
    mr_type: the type of mapreduce job run (e.g., WordCount, Index)
    encoded_key: the DB key corresponding to the metadata of this job
    output: the blobstore location where the output of the job is stored
  """
  
  def run(self, mr_type, encoded_key, output):
    logging.debug("output is %s" % str(output))
    key = db.Key(encoded=encoded_key)
    m = FileMetadata.get(key)
    
    if mr_type == "scapes_analyze":
      m.wordcount_link = output[0]

    m.put()
