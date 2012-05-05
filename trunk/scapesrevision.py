import ConfigParser
import gdata.docs.client
import gdata.gauth
import jinja2
import os
import string
import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Configure gdata
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
SETTINGS = {
  'APP_NAME': config.get('gdata_settings', 'APP_NAME'),
  'CONSUMER_KEY': config.get('gdata_settings', 'CONSUMER_KEY'),
  'CONSUMER_SECRET': config.get('gdata_settings', 'CONSUMER_SECRET'),
  'SCOPES': [config.get('gdata_settings', 'SCOPES')]
}

gdocs = gdata.docs.client.DocsClient(source = SETTINGS['APP_NAME'])

class RequestARevision(webapp2.RequestHandler):
  def doAuthToken(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

  @login_required
  def get(self):
    self.doAuthToken()

    revision = gdocs.GetRevisionBySelfLink(self.request.get('revisionLink'))
    revisionText = gdocs.DownloadRevisionToMemory(
        revision, {'exportFormat': 'txt'})
    revisionText = string.split(revisionText, '\n')
    revisionWordCount = 0
    revisionTitle = revision.title.text

    for line in revisionText:
      line = line.split()
      revisionWordCount = revisionWordCount + len(line)

    # TODO(dani): Playing with Google API Last Edit
    lastEdit = revision.updated
    linesAdded = 0
    linesDeleted = 0
    linesChanged = 0

    # TODO(mcupino): Find out how to pass on a previous text from each ajax call
    ##for line in difflib.context_diff(previousText, revisionText):
    ##  currentDiff += line
    ##  if line.startswith('+ '):
    ##    linesAdded += 1
    ##  elif line.startswith('- '):
    ##    linesDeleted += 1
    ##  elif line.startswith('! '):
    ##    linesChanged += 1

    author = revision.author[0].email.text
    # TODO(mcupino): Find out how to pass on flaged value from each ajax call
    ##if not flagged:
    ##  if originalAuthor is None:
    ##    originalAuthor = author
    ##  elif author != originalAuthor:
    ##    differentAuthor = True
    ##  elif differentAuthor and originalAuthor == author:
    ##    #TODO: Move to template values eventually
    ##    self.response.out.write("Flag as author other author <br />")
    ##    flagged = True

    # TODO(mcupino): Find out how to pass on a previous text from each ajax call
    # previousText = revisionText

    # TODO(dani): Statistics Summary
    # Lines Added

    templateValues = {
      'revisionLink': self.request.get('revisionLink'),
      'author': author,
      'lastEdit': lastEdit,
      'revisionTitle': revisionTitle,
      'revisionWordCount': revisionWordCount,
      'linesAdded': linesAdded,
      'linesDeleted': linesDeleted,
      'linesChanged': linesChanged
    }
    template = jinja_environment.get_template('templates/requestARevision.html')
    self.response.out.write(template.render(templateValues))
