import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp.util import login_required
from model.file_metadata import FileMetadata
from pipeline.scapes_analysis_pipeline import ScapesAnalysisPipeline
from 
from service import config

class IndexHandler(webapp2.RequestHandler):
  """The main page that users will interact with, which presents users with
  the ability to upload new data or run MapReduce jobs on their existing data.
  """

  template_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"),
                                    autoescape=True)
  
  @login_required
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
    
  @config.decorator.oauth_required
  def post(self):
    http = config.decorator.http()
    folder_id = self.request.get("scapes_folder_id")
    if self.request.get("scapes_folder"):
      print "\n"+"*"*100, type(http), "\n", folder_id, "*" * 100
      mapper_data_id = scapes_generate_blobstore_record(http, folder_id)
      pipeline = ScapesAnalysisPipeline(mapper_data_id)

    pipeline.start()
    self.redirect(pipeline.base_path + "/status?root=" + pipeline.pipeline_id)
    
