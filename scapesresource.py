import ConfigParser
import copy
import gdata.docs.client
import gdata.gauth
import jinja2
import os
import urllib
import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from scapesmodel import Revision

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

class RequestAResource(webapp2.RequestHandler):
  def doAuthToken(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

  @login_required
  def get(self):
    self.doAuthToken()

    #revision = gdocs.GetRevisionBySelfLink(self.request.get('revisionLink'))
    #revisionLink = gdocs.DownloadRevisionToMemory(revision)
    # Get revisions from resource link
    resourceSelfLink = urllib.unquote(self.request.get('resourceLink'))
    allRevisionsQuery = Revision.all()
    revisionsOfResourceQuery = allRevisionsQuery.filter("resourceLink = ",
        resourceSelfLink)

    # TODO: These two lines should only run if it's not stored in the database
    if True:
      resource = gdocs.GetResourceBySelfLink(resourceSelfLink)
      revisions = gdocs.GetRevisions(resource)

    originalAuthor = None
    differentAuthor = False
    flag = ""

    # Go through each revision and get necessary information
    for revision in revisions.entry:
      revisionLink = revision.GetSelfLink().href
      author = revision.author[0].email.text
      queryCopy = copy.deepcopy(revisionsOfResourceQuery)
      results = queryCopy.get()
      revisionText = None
      if (results is None):
        revisionText = gdocs.DownloadRevisionToMemory(
            revision, {'exportFormat': 'txt'})
        revisionStore = Revision(resourceLink=resourceSelfLink,
          revisionNumber=revisionLink, revisionDownloadedText=revisionText)
        revisionStore.put()
      else:
        revisionText = results.revisionDownloadedText
      if originalAuthor is None:
        originalAuthor = author
      elif author != originalAuthor:
        differentAuthor = True
      elif differentAuthor and originalAuthor == author:
        flag = "Interesting"
        break
    templateValues = {
      'resourceLink': self.request.get('resourceLink'),
      'resource': resource,
      'flag': flag
    }
    template = jinja_environment.get_template('templates/requestAResource.html')
    self.response.out.write(template.render(templateValues))
