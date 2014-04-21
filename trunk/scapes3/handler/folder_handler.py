import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from model.file_model import File

class Folder(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('hi')

  def post(self):
    folder_name = self.request.get('folder_name', DEFAULT_FOLDER_NAME)
    file = File(parent=folder_key(folder_name))
    
    if users.get_current_user():
      file.author = users.get_current_user()

    file_content = self.request.get('file_content')
    file.list_of_id = file_content
    file.put()

    query_params = {'folder_name': folder_name}

DEFAULT_FOLDER_NAME = 'default_folder'

def folder_key(folder_name=DEFAULT_FOLDER_NAME):
    """Constructs a Datastore key for a folder entity with folder_name."""
    return ndb.Key('Folder', folder_name)

