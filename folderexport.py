import webapp2
from gfolderanalyzer import GFolderAnalyzer
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from mailman import FunClass

class FolderExportRequestHandler(webapp2.RequestHandler):

  @login_required
  def get(self):
    """GET Request"""

    folderResourceID = self.request.get("resourceID")
    requesterUserID = users.get_current_user().user_id()

    mailman = FunClass()

    folderAnalyzer = GFolderAnalyzer(folderResourceID, requesterUserID)
    folderAnalyzer.addListener(mailman)
    folderAnalyzer.analyze()

    self.response.out.write("We will send out an email when we're finished")

