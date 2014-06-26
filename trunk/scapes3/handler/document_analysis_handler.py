import webapp2

from google.appengine.api import users
from pipeline.document_analysis_pipeline import DocumentAnalysisPipeline
from service import config

class DocumentAnalysisHandler(webapp2.RequestHandler):
  """Handler that starts the DocumentAnalysisPipeline.
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
    pipeline = DocumentAnalysisPipeline(toEmail, documentId,
        config.decorator.get_credentials().to_json())
    pipeline.start()
    self.response.write(('Document analysis has started. List of character '
        'diffs will be sent to %s, but not yet implemented.' % toEmail))

