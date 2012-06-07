from scapesfolder import ScapesFolder
from scapesres import ScapesResource
from scapesdocument import ScapesDocument
from scapesrev import ScapesRevision
from scapesdrive import ScapesDrive

def runScapesResourceTests():
  resource = ScapesResource()
  print resource.resourceId

def runFolderTests():
  folder = ScapesFolder()
  folder.getDocuments()

def runDocumentTests():
  document = ScapesDocument()
  document.getRevisions()

def runRevisionTests():
  revision = ScapesRevision()
  revision.getRevisionText()

def runDriveTests():
  drive = ScapesDrive()

def run():
  """This is the run method that manually runs other stuff"""
  
  runScapesResourceTests()
  runFolderTests()
  runDocumentTests()
  runRevisionTests()
  runDriveTests()

print "Running scapesmanualtests"
run()
