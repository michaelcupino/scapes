#!/usr/bin/env python
#
# Copyright 2011 Google Inc.
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

""" This is a sample application that tests the MapReduce API.

It does so by allowing users to upload a zip file containing plaintext files
and perform some kind of analysis upon it. Currently three types of MapReduce
jobs can be run over user-supplied input data: a WordCount MR that reports the
number of occurrences of each word, an Index MR that reports which file(s) each
word in the input corpus comes from, and a Phrase MR that finds statistically
improbably phrases for a given input file (this requires many input files in the
zip file to attain higher accuracies)."""

__author__ = """aizatsky@google.com (Mike Aizatsky), cbunch@google.com (Chris
Bunch)"""

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


def send_email():
    """Sends an email."""
    
    # TODO(tbawaz): Send a hardcoded email.
    
    # makes a temp file for csv writer
    csvFile = tempfile.TemporaryFile()
    writer = csv.writer(csvFile)
    
    values = [['Date', 'Time']]
    writer.writerows(values)
    csvFile.seek(0)
    csvFileBytes = csvFile.read()
    
    # ensure it is a plain byte string
    csvFileBytes = bytes(csvFileBytes)
    csvFile.close()
    
    mail.send_mail(sender = "Scapes Robot <robot@scapes-uci.appspotmail.com>",
              to = "Tristan Biles <tbawaz@gmail.com>",
              subject = "Getting through the first sprint",
              body = """
              Testing the mail.send_mail() function over the mail.EmailMessage()
                                """, 
                          attachments = [("csvTempFile.csv",csvFileBytes)])
    logging.info("value of my csv is %s", csvFileBytes)

def word_count_map(data):
  """Word count map function."""
  (entry, text_fn) = data
  text = text_fn()
    
  logging.debug("Got %s", entry.filename)
  for s in split_into_sentences(text):
    for w in split_into_words(s.lower()):
      yield (w, "")


def word_count_reduce(key, values):
  send_email()
  """Word count reduce function."""
  yield "%s: %d\n" % (key, len(values))



class WordCountPipeline(base_handler.PipelineBase):
  """A pipeline to run Word count demo.

  Args:
    blobkey: blobkey to process as string. Should be a zip archive with
      text files inside.
  """

  def run(self, filekey, blobkey):
    logging.debug("filename is %s" % filekey)
    output = yield mapreduce_pipeline.MapreducePipeline(
      "word_count",
      "main.word_count_map",
      "main.word_count_reduce",
      "mapreduce.input_readers.BlobstoreZipInputReader",
      "mapreduce.output_writers.BlobstoreOutputWriter",
      mapper_params={
        "blob_key": blobkey,
      },
        reducer_params={
          "mime_type": "text/plain",
        },
        shards=16)
    yield StoreOutput("WordCount", filekey, output)

class StoreOutput(base_handler.PipelineBase):
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

    if mr_type == "WordCount":
      m.wordcount_link = output[0]

    m.put()

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
  """Handler to download blob by blobkey."""

  def get(self, key):
    key = str(urllib.unquote(key)).strip()
    logging.debug("key is %s" % key)
    blob_info = blobstore.BlobInfo.get(key)
    self.send_blob(blob_info)


app = webapp2.WSGIApplication(
    [
        ('/', IndexHandler),
        (r'/blobstore/(.*)', DownloadHandler),
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
