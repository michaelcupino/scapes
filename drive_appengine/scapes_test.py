#/usr/bin/env python
import httplib2
import pprint

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow

# Copy your credentials from the console
CLIENT_ID = '551548476927-h19sqjvvej0du0f6a487u0iac6u3dh7k.apps.googleusercontent.com'
CLIENT_SECRET = 'Lu7PouJg0QSxYzaWoJUl_eqD'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Path to the file to upload
FILENAME = 'document.txt'

# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + authorize_url
code = raw_input('Enter verification code: ').strip()
#code = "4/1lDr85ZH4CnHTofVYh3AXb5TWw5Y.MoHnu-2zyIYbmmS0T3UFEsOGgyWJhAI"
credentials = flow.step2_exchange(code)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

from scapes_file_drive import retrieve_all_files
print retrieve_all_files(drive_service)
