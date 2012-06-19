import logging
from google.appengine.api import mail

class FunClass():
  def notify(self, firingInfo):
    """This gets called when the folder is done being analyzed"""

    message = mail.EmailMessage()
    message.sender = "SCAPES Robot <robot@scapes-uci.appspotmail.com>"
    message.subject = "folderResourceID"
    #message.subject = firingInfo["folderResourceID"]
    message.to = "michaelcupino@gmail.com"
    message.body = "The analysis for the folder is complete"
    message.send()

    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Yay, done analyzing %s!!!!!!!!" % firingInfo["folderResourceID"])
