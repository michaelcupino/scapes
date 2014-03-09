import webapp2
from service import config
import file_core
import revision_core

class FileIDHandler(webapp2.RequestHandler):
  """prints out the files in a google drive folder
  """
        
  @config.decorator.oauth_required
  def get(self):
    """print out documents in a folder"""

    ##very similar to jonathan's work##
    http = config.decorator.http()
    variables = {
      'url': config.decorator.authorize_url(),
      'has_credentials': config.decorator.has_credentials()
    }

    self.file_id = file_core.retrieve_all_files(http)
    output = self.list_by_field('modifiedDate')
    string_output  = ''
    
    for item in output:
      string_output += '<pre>'
      string_output += item
      string_output += '</pre>'
    self.response.write(string_output)

  def list_by_field(self,field_name,second_field = None):
    '''downloadUrl': 
       'etag':
       'fileSize':
       'id': 
       'kind': 
       'lastModifyingUser': {'displayName'
                             'isAuthenticatedUser':
                             'kind': 
                             'permissionId': 
                             'picture': {'url': }},
       'lastModifyingUserName': 
       'md5Checksum': 
       'mimeType': 
       'modifiedDate':
       'originalFilename': 
       'pinned': 
       'published': 
       'selfLink': 
       
       This is the template for a response object. This function takes in a fieldname and returns a list of all the responses with just that field
           --oops, can't return, guess I'll just print for now '''
      
    if second_field != None and field_name == 'lastModifyingUser':
      if second_field == 'picture':
        result = [item[field_name][second_field]['url'] for item in self.file_id]
      else:
        result = [item[field_name][second_field] for item in self.file_id]
    else:
      result = [item[field_name] for item in self.file_id]
    return result
        
        
        
