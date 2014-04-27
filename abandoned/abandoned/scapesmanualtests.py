from scapesres import ScapesResource
from scapesrev import ScapesRevision

from model.scapesdocument import ScapesDocument
from model.scapesdrive import ScapesDrive
from model.scapesfolder import ScapesFolder

import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required

class ScapesManualTests(webapp2.RequestHandler):
  def runFolderTests(self):
    folder = ScapesFolder("folder:0BzgGloh-1l4LYTlkZTQ4MDQtMjMxMC00MzE2LWJkNDgtYWVlN2VkZWIwMDRh")
    print folder.getDocumentsResourceIDs()

  def runDocumentTests(self):
    document = ScapesDocument("document:1sIKrGsH0XODRvB7rBLpAUo3p1gF1S-advzoD3c5S1FM")
    print document.getRevisionsSelfLinks()

  def runRevisionTests(self):
    # revision = ScapesRevision("https://docs.google.com/feeds/default/private/full/document%3A1sIKrGsH0XODRvB7rBLpAUo3p1gF1S-advzoD3c5S1FM/revisions/212")
    revision = ScapesRevision("https://docs.google.com/feeds/default/private/full/document%3A1a-yd_uRrkeJWlXBt7HRPbsyy7JrpYqepo7yzilo0KvI/revisions/185")
    print revision.getRevisionText()

  def runDriveTests(self):
    drive = ScapesDrive()

  def run(self):
    """This is the run method that manually runs other stuff"""
    
    print "Running ScapesFolder use case"
    #self.runFolderTests()
    print

    print "Running ScapesDocument use case"
    #self.runDocumentTests()
    print

    print "Running Revision use case"
    self.runRevisionTests()
    print

    #self.runDriveTests()
  
  @login_required
  def get(self):
    print "Running scapesmanualtests use cases"
    print
    self.run()
