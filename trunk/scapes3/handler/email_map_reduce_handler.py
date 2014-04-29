import webapp2

from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from pipeline.email_pipeline import EmailPipeline

class EmailMapReduceHandler(webapp2.RequestHandler):
  """Proof of concept handler that starts a map reduce job that sends an email.
  """
  
  @login_required
  def get(self):
    toEmail = users.get_current_user().email()
    pipeline = EmailPipeline(toEmail)
    pipeline.start()
    self.response.write(('Map reduce job has been started. Email will be sent '
        'soon.'))

