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
    subject = 'Hello from SCAPES'
    body = 'This message was sent from the EmailPipeline map reduce job.'
    pipeline = EmailPipeline(toEmail, subject, body)
    pipeline.start()
    self.response.write(('Map reduce job has been started. An email will be '
        'sent to %s.' % toEmail))

