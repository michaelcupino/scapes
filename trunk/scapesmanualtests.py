from scapesfolder import ScapesFolder
from scapesres import ScapesResource
from scapesdocument import ScapesDocument
from scapesrev import ScapesRevision
from scapesdrive import ScapesDrive
import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required

class ScapesManualTests(webapp2.RequestHandler):
  def runFolderTests(self):
    folder = ScapesFolder("folder:0B-iFCM0alu9_NGE1MTcyNTktOWQxYS00N2UwLTk2YzMtY2IxZTg5MWY5N2Uw")
    print folder.getDocumentsResourceIDs()

  def runDocumentTests(self):
    document = ScapesDocument("document:15FIAabxIpb1OVkZth3vz75PxjsWm6Smxki-7uEXwZuU")
    print document.getRevisionsSelfLinks()

  def runRevisionTests(self):
    revision = ScapesRevision("https://docs.google.com/feeds/default/private/full/document%3A15FIAabxIpb1OVkZth3vz75PxjsWm6Smxki-7uEXwZuU/revisions/59")
    print revision.revisionText

  def runDriveTests(self):
    drive = ScapesDrive()

  def run(self):
    """This is the run method that manually runs other stuff"""
    
    self.runFolderTests()
    self.runDocumentTests()
    self.runRevisionTests()
    #self.runDriveTests()
  
  @login_required
  def get(self):
    print "Running scapesmanualtests"
    self.run()
