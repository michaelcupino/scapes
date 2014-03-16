import webapp2
from service import config
import file_core
import revision_core
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

def folder_key(folder_name=DEFAULT_FOLDER_NAME):
    """Constructs a Datastore key for a folder entity with folder_name."""
    return ndb.Key('Folder', folder_name)

class File(ndb.Model):
    """Models an individual File entry with author, content and date."""
    author = ndb.UserProperty()
    list_of_id = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
class FileIDHandler(webapp2.RequestHandler):
  """prints out the files in a google drive folder
  """
        
  @config.decorator.oauth_required
  def get(self):
    ##very similar to jonathan's work##
    http = config.decorator.http()
    variables = {
      'url': config.decorator.authorize_url(),
      'has_credentials': config.decorator.has_credentials()
    }

    self.file_id = file_core.retrieve_all_files(http)
    self.ids_string = self.documents_in_folder('0B8tE36D1lgLVYWRFSkJBVnZOY00')
    print(self.ids_string)
    
  def post(self):
    folder_name = self.request.get('folder_name', DEFAULT_FOLDER_NAME)
    file = File(parent=folder_key(folder_name))
    
    if users.get_current_user():
      file.author = users.get_current_user()

    file.list_of_id = self.ids_string
    file.put()

    query_params = {'folder_name': folder_name}
    
  def documents_in_folder(self,folder_id):
    '''retrieve all documents from the given folder id'''
    result = ''
    for item in self.file_id:
      try:
        if item['parents'][0]['id'] == folder_id:
          if item['mimeType'].endswith('folder'):
            result += self.documents_in_folder(item['id'])
          elif item['mimeType'].endswith('document'):
            result += item['id']
            result += '\n'
          else:
            pass
      except:
        pass
    return result
