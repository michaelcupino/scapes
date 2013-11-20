import webapp2
from service import config
import scapes_file_drive
import scapes_revision_drive

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

    self.file_id = scapes_file_drive.retrieve_all_files(http)
    output = self.list_by_field('id')
    string_output  = ''#temporary, testing purposes
    
    for item in output:
      string_output += '<pre>'
      string_output += item
      string_output += '</pre>'
    self.response.write(string_output)

  def list_by_field(self,field_name):
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
           --oops, can't return, guess I'll just print for now
       (Ill add error handling later, but I'm not sure how to go about that atm) '''
    result = [item[field_name] for item in self.file_id]
    return result
        
        
        