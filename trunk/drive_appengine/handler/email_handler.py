import webapp2
from google.appengine.api import mail

class EmailHandler(webapp2.RequestHandler):
  """The EmailHandler handles email requests and sends an email from the
  scapes robot account.
  """
  
  def get(self):
    """Sends an email."""
    message = mail.EmailMessage(
        sender='Scapes Robot <robot@scapes-uci.appspotmail.com>',
        subject='Getting through the first sprint')

    message.to = 'Tristan Biles <tbawaz@gmail.com>'
    message.body = 'Dear Tristan:\n\n' + 'Finally getting this to work!'

    message.send()
    self.response.write('Details of the email message will be here. Hopefully '
        'the email will have been sent!')
