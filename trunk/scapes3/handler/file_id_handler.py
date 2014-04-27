import webapp2
from service import config
import file_core
import revision_core
import cgi
import pickle
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb,db

import webapp2

class File(ndb.Model):
    """Models an individual File entry with author, content and date."""
    author = ndb.UserProperty()
    title = ndb.StringProperty()
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

# class FileIDHandler(webapp2.RequestHandler):
#   """prints out the files in a google drive folder
#   """
        
#   @config.decorator.oauth_required
#   def get(self):
#     http = config.decorator.http()
#     variables = {
#       'url': config.decorator.authorize_url(),
#       'has_credentials': config.decorator.has_credentials()
#     }

#     self.file_id = file_core.retrieve_all_files(http)
#     self.ids_string = self.documents_in_folder('0B8tE36D1lgLVYWRFSkJBVnZOY00')
    
#     parent_folder = 'file_ids'
#     title = 'file_ids'  
    
#     file_query = File.query(File.title=='file_ids')
#     item_found = False
#     for item in file_query:
#       item.content = self.ids_string
#       item_found = True
#     if not item_found:
#       file = File(content = self.ids_string,
#                 title = 'file_ids')
#       if users.get_current_user():
#         file.author = users.get_current_user()
#       file.put()

#     query_params = {'title': title}
    
def documents_in_folder(http, folder_id):
  '''retrieve all documents from the given folder id'''
  result = ''
  file_id = file_core.retrieve_all_files(http)
  for item in file_id:
    try:
      if item['parents'][0]['id'] == folder_id:
        if item['mimeType'].endswith('folder'):
          result += documents_in_folder(item['id'])
        elif item['mimeType'].endswith('document'):
          result += item['id']
          # also pickle the http variable
          # ASCII 30 is the record sep. ASCII 31 is the form sep
          result += chr(30) + pickle.dumps(http,0).replace("\n",chr(31))
          result += '\n'
    except: pass
  return result
