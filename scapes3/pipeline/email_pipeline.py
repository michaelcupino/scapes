from google.appengine.api import mail
from mapreduce import base_handler

class EmailPipeline(base_handler.PipelineBase):
  """A pipeline that sends an email.
  
  Args:
    toEmail: The email address reciever of this message.
  """
  
  def run(self, toEmail):
    message = mail.EmailMessage()
    message.sender = 'robot@scapes-uci.appspotmail.com'
    message.to = toEmail
    message.subject = 'Hello from SCAPES'
    message.body = ('This message was sent from the EmailPipeline map reduce '
        'job.')
    message.send()

