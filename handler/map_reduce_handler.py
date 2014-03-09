import webapp2
from service import config
import file_core
import revision_core
import os
import urllib
import logging
from mapreduce_dependencies import input_readers
from mapreduce_dependencies import output_writers
from mapreduce_dependencies import mapreduce_pipeline
from mapreduce_dependencies import base_handler
from email_handler import EmailHandler

from google.appengine.ext import blobstore,db
from google.appengine.ext.webapp import blobstore_handlers

class MRSendEmailPipeline(base_handler.PipelineBase):
  """A pipeline to run Word count demo.

  Args:
    blobkey: blobkey to process as string. Should be a zip archive with
      text files inside.
  """
  print('Entered Pipeline')
  def run(self, filekey, blobkey):
    print('WORDCOUNTPIPELINEWORDCOUNTPIPELINEWORDCOUNTPIPELINEWORDCOUNTPIPELINEWORDCOUNTPIPELINE')
    print('filekey is {}'.format(filekey))
    output = yield mapreduce_pipeline.MapreducePipeline(
        "send_email",
        "send_email_map",
        "send_email_reduce",
        "mapreduce_dependencies.input_readers.BlobstoreZipInputReader",
        "mapreduce_dependencies.output_writers.BlobstoreOutputWriter",
        mapper_params={
            "blob_key": blobkey,
        },
        reducer_params={
            "mime_type": "text/plain",
        },
        shards=16)
    yield StoreOutput("MRSendEmail", filekey, output)
    

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  print("Entered UploadHandlers")
  def post(self):
      print("Entered POST of Up")
      upload_files = self.get_uploads('file')
      print(upload_files)
      if len(upload_files) > 0:
        blob_info = upload_files[0]
        blob_key = blob_info.key()
        Wrapper(blob=blob_key).put()
        blob_key = self.request.get('blobkey')
        filekey = self.request.get('filekey')
        pipeline = MRSendEmailPipeline(filekey,blob_key)
        logging.debug("got to pipeline start")
        print("got to pipeline.start")
        pipeline.start()
        self.redirect('/serve/{}'.format(blob_info.key()))
        self.response.out.write('Uploading disabled')
        pipeline.start()

class Wrapper(db.Model):
  print("Entered Wrapper")
  user = db.UserProperty(auto_current_user=True)
  blob = blobstore.BlobReferenceProperty(required=True)
  date = db.DateTimeProperty(auto_now_add=True)

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  print("Entered ServeHanlder")
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

        

class StoreOutput(base_handler.PipelineBase):
  """A pipeline to store the result of the MapReduce job in the database.

  Args:
    mr_type: the type of mapreduce job run (e.g., WordCount, Index)
    encoded_key: the DB key corresponding to the metadata of this job
    output: the blobstore location where the output of the job is stored
  """
  print("Entered StoreOutput")
  def run(self, mr_type, encoded_key, output):
    logging.debug("output is %s" % str(output))
    key = db.Key(encoded=encoded_key)
    m = FileMetadata.get(key)

    if mr_type == "MRSendEmail":
      m.MRSendEmail_link = output[0]
    elif mr_type == "Index":
      m.index_link = output[0]
    elif mr_type == "Phrases":
      m.phrases_link = output[0]

    m.put()

MAIN_PAGE_HTML = '''\
<html>
    <body>
        <form action = "%s" method = 'POST' enctype = 'mutipart/form-data'>

        <input type="button" value="Click me" onclick="msg()">
        # TODO: HAVE onclick = ____ send out the email
        </form>
    </body>
</html>

'''

class MREmailHandler(webapp2.RequestHandler):
    def get(self):
        print('Entered Get MREmailHandler')
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write(MAIN_PAGE_HTML)
#         self.response.out.write('<html><body>')
#         self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
#         self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
#             name="submit" value="Submit"> </form></body></html>""")
    def post(self):
        print('Entered Post MREmailHandler')



###MAP FUNCTION###
def send_email_map():
    #maybe need input data?
  """Word count map function."""
  print("Entered send map function")
  EmailHandler.run()
   
   
###REDUCE FUNCTION###    
def send_email_reduce(key, values):
  """Word count reduce function."""
  print("Entered send reduce function")
 
  
 

        
        

  