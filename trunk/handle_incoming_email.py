import email
import logging
import webapp2
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class LogSenderHandler(InboundMailHandler):
  def receive(self, mail_message):
    logging.info("Received a message from: " + mail_message.sender)

app = webapp2.WSGIApplication([LogSenderHandler.mapping()],
    debug=True)
