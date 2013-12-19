import webapp2
import csv
import tempfile
import logging
from google.appengine.api import mail

class EmailHandler(webapp2.RequestHandler):
  """The EmailHandler handles email requests and sends an email from the
  scapes robot account.
  """
  


  def get(self):
    """Sends an email."""

    # TODO(tbawaz): Send a hardcoded email.
	
    
    csvFile = tempfile.TemporaryFile() #makes a temp file
    writer = csv.writer(csvFile) # makes the temp file a csv file
    values = [['Date', 'Time']]
    writer.writerows(values)
    csvFile.seek(0)
    csvFileBytes = csvFile.read()  # <--- this is what you're looking for
    csvFile.close()
	
    mail.send_mail(sender = "Scapes Robot <robot@scapes-uci.appspotmail.com>",
              to = "Tristan Biles <tbawaz@gmail.com>",
              subject = "Getting through the first sprint",
              body = """
				Testing the mail.send_mail() function over the mail.EmailMessage()
				""", 
				attachments = [("csvTempFilee",csvFileBytes)])
    
    self.response.write('Email has been successfully sent. Making sure CSV1 sends as well')
    logging.info("value of my csv is %s", csvFileBytes)