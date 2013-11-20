import webapp2
import csv
import tempfile
from google.appengine.api import mail

class EmailHandler(webapp2.RequestHandler):
  """The EmailHandler handles email requests and sends an email from the
  scapes robot account.
  """
  


  def get(self):
    """Sends an email."""

    # TODO(tbawaz): Send a hardcoded email.
	
    
    csvFile = tempfile.TemporaryFile()
    writer = csv.writer(csvFile)
    values = [['Date', 'Time']]
    writer.writerows(values)
    csvFile.seek(0)
    csvFileBytes = csvFile.read()  # <--- this is what you're looking for
    csvFile.close()
	
    mail.send_mail("Scapes Robot <robot@scapes-uci.appspotmail.com>",
              to="Tristan Biles <tbawaz@gmail.com>",
              subject="Getting through the first sprint",
              body="""
	Testing the mail.send_mail() function over the mail.EmailMessage()
	""", attachments = [("csvTempFile",csvFileBytes)])
    
    self.response.write('Email has been successfully sent. Making sure CSV1 sends as well')

    
