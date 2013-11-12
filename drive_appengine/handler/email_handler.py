import webapp2

class EmailHandler(webapp2.RequestHandler):
  """The EmailHandler handles email requests and sends an email from the
  scapes robot account.
  """
  
  def get(self):
    """Sends an email."""
    # TODO(tbawaz): Send a hardcoded email.

    self.response.write('Details of the email message will be here.')
