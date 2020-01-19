#basically the python quick start from google's api documentation
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

scopes = ['https://www.googleapis.com/auth/spreadsheets']

def creds():
	creds = None
	if os.path.exists('Sheets/token.pickle'):
		with open('Sheets/token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'Sheets/credentials.json', scopes)
			creds = flow.run_local_server(port=0)
	# Save the credentials for the next run
	with open('Sheets/token.pickle', 'wb') as token:
		pickle.dump(creds, token)
	return(creds)