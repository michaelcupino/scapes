from google.appengine.api import mail
from mapreduce import base_handler

class EmailPipeline(base_handler.PipelineBase):
  """A pipeline that sends an email.
  
  Args:
    toEmail: The email address reciever of this message.
    subject: The subject of this message.
    body: The body of this message.
  """
  
  def run(self, toEmail, subject, body):
    message = mail.EmailMessage()
    message.sender = 'robot@scapes-uci.appspotmail.com'
    message.to = toEmail
    message.subject = subject
    message.body = str(body)
    message.send()

