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

        approval_page_url = request_token.generate_authorization_url()

        message = """<a href="%s">
        For the 4th document on the Google Docs list, show revision 1 and revision 2</a>"""
        self.response.out.write(message % approval_page_url)


class RequestTokenCallback(webapp2.RequestHandler):

    @login_required
    def get(self):
        current_user = users.get_current_user()

        # TODO(someone?): Is it possible to keep the auth longer?
        request_token_key = 'request_token_%s' % current_user.user_id()
        request_token = gdata.gauth.ae_load(request_token_key)
        gdata.gauth.authorize_request_token(request_token, self.request.uri)

        gdocs.auth_token = gdocs.get_access_token(request_token)

        access_token_key = 'access_token_%s' % current_user.user_id()
        gdata.gauth.ae_save(request_token, access_token_key)

        # gdocs.GetDocList() is deprecated; gdocs.GetResources() is the new way
        # TODO(someone?): Find a way to make the user easily choose a doc to analyze
        feed = gdocs.GetResources()
        doc = feed.entry[3]
        revisions = gdocs.GetRevisions(doc)

        revision1 = revisions.entry[0]
        revision1Text = gdocs.DownloadRevisionToMemory(
            revision1, {'exportFormat': 'txt'})
        revision1TextList = string.split(revision1Text, '\n')

        revision2 = revisions.entry[1]
        revision2Text = gdocs.DownloadRevisionToMemory(
            revision2, {'exportFormat': 'txt'})
        revision2TextList = string.split(revision2Text, '\n')

        template = """<div>%s</div>"""

        # TODO(someone?): Make these things into templates
        self.response.out.write("<h2>Revision 1</h2>")
        self.response.out.write("<pre>")
        for line in difflib.context_diff([], revision1TextList):
            self.response.out.write(line)
        self.response.out.write("</pre>")

        self.response.out.write("<h2>Revision 2</h2>")
        self.response.out.write("<pre>")
        for line in difflib.context_diff(revision1TextList, revision2TextList):
            self.response.out.write(line)
        self.response.out.write("</pre>")

class Greeting(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
    def get(self):
        guestbook_name=self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(
            guestbook_key(guestbook_name)).order('-date')
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))


class Guestbook(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
    guestbook_name = self.request.get('guestbook_name')
    greeting = Greeting(parent=guestbook_key(guestbook_name))

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

class GoogleWebmasterVerify(webapp2.RequestHandler):
  def get(self):
      template = jinja_environment.get_template('google910e6da758dc80f1.html')
      self.response.out.write(template.render())

# TODO(mcupino): Maybe find out how to have the GoogleWebmasterVerify
# automatically route to the html page?
app = webapp2.WSGIApplication([('/', MainPage),
    ('/sign', Guestbook),
    ('/google910e6da758dc80f1.html', GoogleWebmasterVerify),
    ('/step1', Fetcher),
    ('/step2', RequestTokenCallback)],
    debug=True)
