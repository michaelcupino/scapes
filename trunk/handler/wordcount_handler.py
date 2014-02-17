import webapp2
from service import config
import file_core
import revision_core
import os
import urllib
from mapreduce_dependencies import input_readers
from mapreduce_dependencies import output_writers
from mapreduce_dependencies import mapreduce_pipeline
from mapreduce_dependencies import base_handler

from google.appengine.ext import blobstore,db
from google.appengine.ext.webapp import blobstore_handlers

class Wrapper(db.Model):
  user = db.UserProperty(auto_current_user=True)
  blob = blobstore.BlobReferenceProperty(required=True)
  date = db.DateTimeProperty(auto_now_add=True)
  
  
###MAP FUNCTION###
def word_count_map(data):
  """Word count map function."""
  (entry, text_fn) = data
  text = text_fn()

  logging.debug("Got %s", entry.filename)
  for s in split_into_sentences(text):
    for w in split_into_words(s.lower()):
      yield (w, "")
  
  
###REDUCE FUNCTION###    
def word_count_reduce(key, values):
  """Word count reduce function."""
  yield "%s: %d\n" % (key, len(values))
  
 
class WordcountHandler(webapp2.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/upload')
    self.response.out.write('<html><body>')
    self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
    self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
        name="submit" value="Submit"> </form></body></html>""")

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
      upload_files = self.get_uploads('file')
      print(upload_files)
      if len(upload_files) > 0:
        blob_info = upload_files[0]
        blob_key = blob_info.key()
        Wrapper(blob=blob_key).put()
        blob_key = self.request.get('blobkey')
        filekey = self.request.get('filekey')
        pipeline = WordCountPipeline(filekey,blob_key)
        self.redirect('/serve/{}'.format(blob_info.key()))
        self.response.out.write('Uploading disabled')
        #pipeline.start()
        
        
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

        
class WordCountPipeline(base_handler.PipelineBase):
  """A pipeline to run Word count demo.

  Args:
    blobkey: blobkey to process as string. Should be a zip archive with
      text files inside.
  """

  def run(self, filekey, blobkey):
    print('filekey is {}'.format(filekey))
    output = yield mapreduce_pipeline.MapreducePipeline(
        "word_count",
        "word_count_map",
        "word_count_reduce",
        "mapreduce_dependencies.input_readers.BlobstoreZipInputReader",
        "mapreduce_dependencies.output_writers.BlobstoreOutputWriter",
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
    elif mr_type == "Index":
      m.index_link = output[0]
    elif mr_type == "Phrases":
      m.phrases_link = output[0]

    m.put()
  