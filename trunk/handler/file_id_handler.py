import webapp2
from service import config
import file_core
import revision_core
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb,db

import webapp2

DEFAULT_FOLDER_NAME = 'default_folder'


# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def folder_key(title,folder_name=DEFAULT_FOLDER_NAME):
    """Constructs a Datastore key for a folder entity with folder_name."""
    #parameter order is reversed because of kwargs necessities :(
    return ndb.Key('Folder', folder_name,'File',title)


class File(ndb.Model):
    """Models an individual File entry with author, content and date."""
    author = ndb.UserProperty()
    title = ndb.StringProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class FileIDHandler(webapp2.RequestHandler):
  """prints out the files in a google drive folder
  """
        
  @config.decorator.oauth_required
  def get(self):
    http = config.decorator.http()
    variables = {
      'url': config.decorator.authorize_url(),
      'has_credentials': config.decorator.has_credentials()
    }

    self.file_id = file_core.retrieve_all_files(http)
    self.ids_string = self.documents_in_folder('0B8tE36D1lgLVYWRFSkJBVnZOY00')
    print(self.ids_string)
    
    parent_folder = 'file_ids'
    title = 'file_ids'
    file = File(content = self.ids_string,
                title = 'file_ids')
    file_list = []
    file_list.append(file)
    a='a'
    for i in range(10):
        file_list.append(File(content = 'blah',
                              title = a))
        a+='a'
        
    
    for item in file_list:
        item.put()
    if users.get_current_user():
      file.author = users.get_current_user()
    
    file_id = File.query(File.title=='file_ids')
#     file_id.filter(ndb.GenericProperty('title') != 'fileids')
    for item in file_id:
        print(item)
    
    x = File.query()
    for item in x:
      item.key.delete()
    query_params = {'title': title}
    
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
        
        
