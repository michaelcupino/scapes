#/usr/bin/env python
import httplib2
import pprint
import webbrowser
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow

with open("client_secrets.json") as f:
    import json
    data          = json.loads(f.read())
    CLIENT_ID     = data["web"]["client_id"]
    CLIENT_SECRET = data["web"]["client_secret"]

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
# REDIRECT_URI = 'http://localhost:8080/oauth2callback'
REDIRECT_URI = 'http://localhost:8080/oauth2callback'

# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
webbrowser.open(authorize_url)
print 'Go to the following link in your browser: ' + authorize_url

code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

from scapes_file_drive import retrieve_all_files
print retrieve_all_files(drive_service)
