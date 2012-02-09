import cgi
import datetime
import urllib
import webapp2
import jinja2
import os
import gdata.gauth
import gdata.docs.client
import ConfigParser
import difflib
import string

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from google.appengine.ext import db
from google.appengine.api import users

from google.appengine.ext.webapp.util import run_wsgi_app, login_required

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


class DocumentTag(db.Model):
  author = db.UserProperty()
  documentID = db.StringProperty()
  content = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)


class DocumentTagger(webapp2.RequestHandler):
  def post(self):
    # TODO(someone?): Look into parents/ancestors. Maybe we can use this
    # instead of a documentID row.
    documentTag = DocumentTag()

    if users.get_current_user():
      documentTag.author = users.get_current_user()

    documentTag.content = self.request.get('content')
    documentTag.documentID = "insert documentID Here"
    documentTag.put()

    url = self.request.headers.get('Referer')
    self.redirect(url)


class Fetcher(webapp2.RequestHandler):
  @login_required
  def get(self):
    current_user = users.get_current_user()

    scopes = SETTINGS['SCOPES']
    oauth_callback = 'http://%s/step2' % self.request.host
    consumer_key = SETTINGS['CONSUMER_KEY']
    consumer_secret = SETTINGS['CONSUMER_SECRET']
    request_token = gdocs.get_oauth_token(scopes, oauth_callback,
        consumer_key, consumer_secret)

    request_token_key = 'request_token_%s' % current_user.user_id()
    gdata.gauth.ae_save(request_token, request_token_key)

    approvalPageUrl = request_token.generate_authorization_url()

    templateValues = {
      'approvalPageUrl': approvalPageUrl,
    }
    template = jinja_environment.get_template('templates/step1.html')
    self.response.out.write(template.render(templateValues))


class FetchRevision(webapp2.RequestHandler):
  @login_required
  def get(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

    feed = gdocs.GetResources(uri='/feeds/default/private/full/-/document')

    templateValues = {
      'entries': feed.entry,
    }
    template = jinja_environment.get_template('templates/step3.html')
    self.response.out.write(template.render(templateValues))


class RequestRevision(webapp2.RequestHandler):
  @login_required
  def get(self):
    # TODO(dani): Statistics Summary
    
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token
    id = self.request.get('id')
    
    # TODO(jordan): Figure out how to catch exception with invalid resource
    resource = gdocs.GetResourceById(id)
    resourceTitle = resource.title.text
    revisions = gdocs.GetRevisions(resource)
    
    acl = gdocs.GetResourceAcl(resource)

    previousText = "";
    valuesOfRevisions = []
    originalAuthor = None
    differentAuthor = False
    
    for revision in revisions.entry:
      # TODO(someone?): Maybe make this download into a separate function
      # because the client's browser timesout if this takes too long
      revisionText = gdocs.DownloadRevisionToMemory(
          revision, {'exportFormat': 'txt'})
      revisionText = string.split(revisionText, '\n')
      revisionWordCount = 0
      revisionTitle = revision.title.text
      
      for line in revisionText:
        line = line.split()
        revisionWordCount = revisionWordCount + len(line)
      
      currentDiff = ""
      # TODO(dani): Playing with Google API Last Edit
      lastEdit = revision.updated
      for line in difflib.context_diff(previousText, revisionText):
        currentDiff += line
      author = revision.author[0].email.text
      if originalAuthor is None:
        originalAuthor = author
      elif author != originalAuthor:
        differentAuthor = True
      elif differentAuthor and originalAuthor == author:
        #TODO: Move to template values eventually
        self.response.out.write("Flag as author other author <br />")
      revisionValues = {
        'currentDiff': currentDiff,
        'author': author,
        'lastEdit': lastEdit,
        'revisionTitle': revisionTitle,
        'revisionWordCount' : revisionWordCount,
      }  
      valuesOfRevisions.append(revisionValues)
      previousText = revisionText

    # Document Tags
    # TODO(someone?): Look into parents/ancestors. Maybe we can use this
    # instead of a documentID row.
    documentTagQuery = DocumentTag.all()
    documentTags = documentTagQuery.fetch(10)

    templateValues = {
      'acl': acl,
      'documentTags': documentTags,
      'valuesOfRevisions': valuesOfRevisions,
      'revisionCount': len(revisions.entry),
      'resourceTitle': resourceTitle,
    }
    template = jinja_environment.get_template('templates/step4.html')
    self.response.out.write(template.render(templateValues))


class RequestRawRevision(webapp2.RequestHandler):
  @login_required
  def get(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token
    id = self.request.get('id')

    # TODO(jordan): Figure out how to catch exception with invalid resource
    resource = gdocs.GetResourceById(id)
    revisions = gdocs.GetRevisions(resource)

    for revision in revisions.entry:
      # TODO(someone?): Maybe make this download into a separate function
      # because the client's browser timesout if this takes too long
      revisionText = gdocs.DownloadRevisionToMemory(revision)
      self.response.out.write(revisionText)
      self.response.out.write("\n\n\n")


class RequestTokenCallback(webapp2.RequestHandler):
  @login_required
  def get(self):
    current_user = users.get_current_user()

    # Authorize the request token to be an access token
    request_token_key = 'request_token_%s' % current_user.user_id()
    request_token = gdata.gauth.AeLoad(request_token_key)
    gdata.gauth.authorize_request_token(request_token, self.request.uri)

    # Create the long lived access token from the request token
    gdocs.auth_token = gdocs.get_access_token(request_token)
    access_token = request_token

    # Store the access token
    access_token_key = 'access_token_%s' % current_user.user_id()
    gdata.gauth.ae_save(access_token, access_token_key)

    # TODO(someone?): Find out what webap2.redirect does
    webapp2.redirect('step3')
    template = jinja_environment.get_template('templates/step2.html')
    self.response.out.write(template.render())


class MainPage(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render())


class CanvasPlayground(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('templates/canvas.html')
    self.response.out.write(template.render())

class GoogleWebmasterVerify(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('google910e6da758dc80f1.html')
    self.response.out.write(template.render())

# TODO(mcupino): Maybe find out how to have the GoogleWebmasterVerify
# automatically route to the html page?
app = webapp2.WSGIApplication([('/', MainPage),
    ('/canvas', CanvasPlayground),
    ('/google910e6da758dc80f1.html', GoogleWebmasterVerify),
    ('/step1', Fetcher),
    ('/step2', RequestTokenCallback),
    ('/step3', FetchRevision),
    ('/step4', RequestRevision),
    ('/tagDocument', DocumentTagger),
    ('/raw', RequestRawRevision)],
    debug=True)
