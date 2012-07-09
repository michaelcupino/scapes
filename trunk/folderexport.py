import jinja2
import os
import webapp2
from csvfolderexporter import CsvFolderExporter
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from scapesmailman import ScapesMailman

# TODO: Find out if we can have only one reference of this
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class FolderExportRequestHandler(webapp2.RequestHandler):

  @login_required
  def get(self):
    """GET Request"""

    requesterAddress = users.get_current_user().email()
    mailman = ScapesMailman()
    mailman.addRecipientAddress(requesterAddress)

    folderResourceID = self.request.get("resourceID")
    requesterUserID = users.get_current_user().user_id()
    csvFolderExporter = CsvFolderExporter(folderResourceID, requesterUserID)
    csvFolderExporter.addListener(mailman)
    csvFolderExporter.run()

    templateValues = {
      'recipientsAddresses': mailman.getRecipientsAddresses()
    }
    template = jinja_environment.get_template('templates/folderexport.html')
    self.response.out.write(template.render(templateValues))

