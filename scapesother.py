import ConfigParser
import gdata.docs.client
import gdata.gauth
import jinja2
import os
import webapp2
import diff_match_patch.diff_match_patch

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
gdiff = diff_match_patch.diff_match_patch()


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


class FetchCollection(webapp2.RequestHandler):
  @login_required
  def get(self):
    access_token_key = 'access_token_%s' % users.get_current_user().user_id()
    access_token = gdata.gauth.AeLoad(access_token_key)
    gdocs.auth_token = access_token

    feed = gdocs.GetResources(uri='/feeds/default/private/full/-/folder')

    folders = []
    for entry in feed.entry:
      folder = {
        'title': entry.title.text,
        'id': entry.resource_id.text
      }
      folders.append(folder)

    templateValues = {
      'entries': "",
      'folders': folders
    }
    template = jinja_environment.get_template('templates/collections.html')
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

    revisionLinks = []
    for revision in revisions.entry:
      revisionLink = revision.GetSelfLink().href
      revisionLinks.append(revisionLink)

    templateValues = {
      'revisionLinks': revisionLinks,
    }
    template = jinja_environment.get_template('templates/raw.html')
    self.response.out.write(template.render(templateValues))


class RequestARawRevision(webapp2.RequestHandler):
  @login_required
  def get(self):
    revision = gdocs.GetRevisionBySelfLink(self.request.get('revisionLink'))
    revisionLink = gdocs.DownloadRevisionToMemory(revision)
    self.response.out.write(revisionLink)


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
    user = users.get_current_user()
    if user:
      template = jinja_environment.get_template('templates/indexUser.html')
      templateValues = {
        'nickname': user.nickname(),
        'logoutLink': users.create_logout_url(self.request.uri),
      }
    else:
      template = jinja_environment.get_template('templates/indexNoUser.html')
      templateValues = {
        'loginLink': users.create_login_url(self.request.uri),
      }
    self.response.out.write(template.render(templateValues))
    
class TestNaren(webapp2.RequestHandler):
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
    template = jinja_environment.get_template('templates/TestNaren.html')
    self.response.out.write(template.render(templateValues))

class TestTristan(webapp2.RequestHandler):
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
    template = jinja_environment.get_template('templates/TestTristan.html')
    self.response.out.write(template.render(templateValues))
    
class TestFoster(webapp2.RequestHandler):
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
    template = jinja_environment.get_template('templates/TestFoster.html')
    self.response.out.write(template.render(templateValues))
    
class TestHelio(webapp2.RequestHandler):
  @login_required
  def get(self):
    current_user = users.get_current_user()
    
    scopes = SETTINGS['SCOPES']
    oauth_callback = 'http://%s/step2' % self.request.host
    consumer_key = SETTINGS['CONSUMER_KEY']
    consumer_secret = SETTINGS['CONSUMER_SECRET']
    request_token = gdocs.get_oauth_token(
        scopes, oauth_callback, consumer_key, consumer_secret)
    
    request_token_key = 'request_token_%s' % current_user.user_id()
    gdata.gauth.ae_save(
        request_token, request_token_key)
    
    approvalPageUrl = request_token.generate_authorization_url()
    
    templateValues = {
        'approvalPageUrl': approvalPageUrl,}
    template = jinja_environment.get_template('templates/TestHelio.html')
    self.response.out.write(template.render(templateValues))
    
class TestJonathan(webapp2.RequestHandler):
  @login_required
  def get(self):
    import scapesrevisiondrive
    current_user = users.get_current_user()
    
    scopes = SETTINGS['SCOPES']
    oauth_callback = 'http://%s/step2' % self.request.host
    consumer_key = SETTINGS['CONSUMER_KEY']
    consumer_secret = SETTINGS['CONSUMER_SECRET']
    request_token = gdocs.get_oauth_token(
        scopes, oauth_callback, consumer_key, consumer_secret)
    
    request_token_key = 'request_token_%s' % current_user.user_id()
    gdata.gauth.ae_save(
        request_token, request_token_key)
    
    approvalPageUrl = request_token.generate_authorization_url()
    
    templateValues = {
        'approvalPageUrl': approvalPageUrl,}
    template = jinja_environment.get_template('templates/TestJonathan.html')
    
    self.response.out.write(template.render(templateValues))
    
class GoogleWebmasterVerify(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('google910e6da758dc80f1.html')
    self.response.out.write(template.render())
