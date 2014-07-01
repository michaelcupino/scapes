import webapp2

from service import config

class AuthRedirectHandler(webapp2.RequestHandler):
  """Handler that redirects the user to authorize SCAPES to use the drive api.
  """
  
  @config.decorator.oauth_aware
  def get(self):
    if config.decorator.has_credentials():
      self.redirect('/')
    else:
      self.redirect(config.decorator.authorize_url())

