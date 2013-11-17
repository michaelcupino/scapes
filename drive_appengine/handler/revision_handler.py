import pprint
import random
import webapp2
from service import config
import scapes_file_drive
import scapes_revision_drive

class RevisionHandler(webapp2.RequestHandler):
  """The RevisionHandler handles revision requests and gives a response with a
  list of revisions for a specific document.
  """

  @config.decorator.oauth_required
  def get(self):
    """Gets the list of revisions"""

    http = config.decorator.http()
    variables = {
      'url': config.decorator.authorize_url(),
      'has_credentials': config.decorator.has_credentials()
    }

    # TODO(PythonNut) get service and http from config
    file_id = scapes_file_drive.retrieve_all_files(http)
    num = len(file_id)
    revisions = scapes_revision_drive.retrieve_revisions(http,
        random.choice(file_id)['id'])

    text = pprint.pformat(revisions, width = 20)
    text = text.replace("u'","'")
    self.response.write("<h1>" + str(num) + " Documents!</h1><br>\
        <pre>" + text + "</pre>")
