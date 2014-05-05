import webapp2

from google.appengine.api import users
from service import config
from pipeline.document_revisions_pipeline import DocumentRevisionsPipeline

class DocumentRevisionsMRHandler(webapp2.RequestHandler):
  """Handler that starts the DocumentRevisionsPipeline, which sends an email to
  the current user containing a list of revision export links for the given
  document.
  """
  
  @config.decorator.oauth_aware
  def get(self, documentId):
    # If SCAPES is not allowed to access a user's Google Drive, then the user
    # is asked to give authorization to SCAPES.
    if not config.decorator.has_credentials():
      authUrl = config.decorator.authorize_url()
      self.response.write('<a href=' + authUrl + '>' + authUrl + '</a>')
      return
    
    toEmail = users.get_current_user().email()
    pipeline = DocumentRevisionsPipeline(toEmail, documentId,
        config.decorator.get_credentials().to_json())

    pipeline.start()
    self.response.write(('Map reduce job has been started. List of revisions '
        'will sent to %s.' % toEmail))

