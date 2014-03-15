import webapp2
from service import config
import file_core
import revision_core

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
    print("SCAPES 3 STSDTA")
    
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
        
        
