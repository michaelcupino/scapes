#All MapReduce function goes here

import datetime
import jinja2
import logging
import re
import urllib
import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext import db

from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import files
from google.appengine.api import taskqueue
from google.appengine.api import users

from mapreduce_dependencies import base_handler
from mapreduce_dependencies import mapreduce_pipeline
from mapreduce_dependencies import operation as op
from mapreduce_dependencies import shuffler

from service import config

# import scapes_revision_drive is this necessary?

"""

Whoever is doing the template for homepage got to edit IndexHandler Class. Note-
1. Attach the getFirstKeyForUser() and getLastKeyForUser() helper methods (check example)
2. Attach FileMetaData class if needed
3. Load correct template
4. Change post method accordingly

class IndexHandler(webapp2.RequestHandler):
  The main page that users will interact with, which presents users with                                                                           
  the ability to upload new data or run MapReduce jobs on their existing data.                                                                        
  

  template_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
                                    autoescape=True)

  def get(self):
    user = users.get_current_user()
    username = user.nickname()


    first = FileMetadata.getFirstKeyForUser(username)
    last = FileMetadata.getLastKeyForUser(username)

    q = FileMetadata.all()
    q.filter("__key__ >", first)
    q.filter("__key__ < ", last)
    results = q.fetch(10)

    items = [result for result in results]
    length = len(items)

    upload_url = blobstore.create_upload_url("/upload")

    self.response.out.write(self.template_env.get_template("index.html").render(
        {"username": username,
         "items": items,
         "length": length,
         "upload_url": upload_url}))

  def post(self):
    filekey = self.request.get("filekey")
    blob_key = self.request.get("blobkey")

    if self.request.get("word_count"):
      pipeline = WordCountPipeline(filekey, blob_key)
    elif self.request.get("index"):
      pipeline = IndexPipeline(filekey, blob_key)
    else:
      pipeline = PhrasesPipeline(filekey, blob_key)

    pipeline.start()
    self.redirect(pipeline.base_path + "/status?root=" + pipeline.pipeline_id)
"""

class MREmailHandler(webapp2.RequestHandler):
    pass

def revision_map(file_id):
  http = config.decorator.http()
  for revisions in retrieve_revisions(http, file_id):
      yield (file_id, "")

def revision_reduce(key, values):
  yield "%s: %d\n" % (key, len(values))

class RevisionCountPipeline(base_handler.PipelineBase):
  def run(self, filekey, blobkey):
    logging.debug("filename is %s" % filekey)
    output = yield mapreduce_pipeline.MapreducePipeline(
        "revision_count",
        "map_reduce_handler.revision_map",
        "map_reduce_handler.revision_reduce",
  #      "mapreduce.input_readers.BlobstoreZipInputReader", Got to fix this accordingly
  #      "mapreduce.output_writers.BlobstoreOutputWriter", Got to fix this accordingly
        mapper_params={
            "blob_key": blobkey,
        },
        reducer_params={
            "mime_type": "text/plain",
        },
        shards=16)
    yield StoreOutput("RevisionCount", filekey, output)
