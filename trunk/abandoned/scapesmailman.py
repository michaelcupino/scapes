from google.appengine.api import mail

class ScapesMailman():
  """This class deals with sending out e-mail messages when something should be
  notified"""

  def __init__(self):
    """Initializes the object"""

    self.recipientsAddresses = []
    self.scapesRobotAddress = "SCAPES Robot <robot@scapes-uci.appspotmail.com>"

  def notify(self, firingInfo):
    """This gets called when the folder is done being analyzed"""

    folderTitle = firingInfo["folderTitle"]
    folderCsvExportFile = firingInfo["folderCsvExportFile"]
    for recipientAddress in self.recipientsAddresses:
      message = mail.EmailMessage()
      message.sender = self.scapesRobotAddress
      message.subject = "SCAPES Folder Analysis Finished: " + folderTitle
      message.to = recipientAddress
      message.body = "Attached is " + folderTitle + ".csv"
      message.attachments = [("" + folderTitle + ".csv", folderCsvExportFile)]
      message.send()

  def addRecipientAddress(self, address):
    """Add a recpient to list of e-mail addresses being notified"""

    self.recipientsAddresses.append(address)

  def getRecipientsAddresses(self):
    """Gets the recipients addresses"""

    return self.recipientsAddresses
