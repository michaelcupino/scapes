import logging

from google.appengine.ext import db
from mapreduce import base_handler
from model.file_metadata import FileMetadata

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

