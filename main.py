#TODO:
# - [x] Pull images from Email HTML Body and use that in the front-end card
# - [ ] Add ability to read complete email from the email body within the card front-end
# - [ ] Pull 'unsubscribe' links from the email body
# - [ ] Place 'Unsubscribe' Button on the card
# - [x] Add the ability to 'Erase All' from a particular sender email address 
# 			- NOTES: https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list\
#       - NOTES: Query Parameters, 'q' accepts string, like "from:someuser@example.com" and returns emails from that sender
# - [x] Speed up the front end 
#				- [x] Pull email / image data in the initial page load, then send a simple POST request to the server if the user selects to unsubscribe/erase all/delete_individual
#				- [ ] Server Side Rendering?
#       - [x] Lazy Loading with Prefetching
# - [x] Better icons on the front end
# - [ ] Better tags on the front end (currently "Email", "gmail", "Unsubscribe"[if applicable].) It should display the inbox type the mail is in, and possible other stuff
# - [x] Ability to see how many emails from a particualr sender are in the inbox, shown on the card, maybe next to the senders name or next to the "Delete All" Button

import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, current_app, request
from authlib.integrations.flask_client import OAuth
from flask.app import T_template_test
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport import requests as google_auth_requests
from google.oauth2 import id_token
from functools import wraps
from bs4 import BeautifulSoup # For parsing HTML of the email
import base64
import re

def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    oauth = OAuth(app)
    
    app.oauth = oauth
    app.google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            #'scope': 'openid email profile https://www.googleapis.com/auth/gmail.modify',
						'scope' : 'openid email profile https://mail.google.com/',
						'access_type': 'offline',
						'prompt': 'consent',
        }
    )
    
    return app

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('REDIRECT_URI')
app = create_app(Config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def pull_images_from_email(email_body):
		image = []
		return image

def number_of_emails_from_sender(service, sender_email):
    results = service.users().messages().list(userId='me', q='from:' + sender_email).execute()
    messages = results.get('messages', [])
    current_app.logger.info(f'Number of emails from {sender_email}: {len(messages)}')
    return len(messages)

@app.errorhandler(Exception)
def handle_error(error):
    current_app.logger.error(f"An error occurred: {str(error)}")
    return jsonify(error=str(error)), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    #redirect_uri = url_for('authorize', _external=True)
    return app.google.authorize_redirect(redirect_uri = app.config['REDIRECT_URI'])

@app.route('/authorize')
def authorize():
    try:
        token = app.google.authorize_access_token()
        #current_app.logger.debug(f"Token Received: {token}")
			
        # Verify ID token
        id_info = id_token.verify_oauth2_token(
            token['id_token'], 
            google_auth_requests.Request(), 
            current_app.config['GOOGLE_CLIENT_ID']
        )
        
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        #Add missing fields manually to token
        token['client_id'] = current_app.config['GOOGLE_CLIENT_ID']
        token['client_secret'] = current_app.config['GOOGLE_CLIENT_SECRET']
        
        session['google_token'] = token
        if 'refresh_token' in token:
            session['refresh_token'] = token['refresh_token']
        else:
            current_app.logger.warning('No refresh token provided; check Google API settings.')
        

        #current_app.logger.debug(f"ID Token Verified: {token}")
        session['user_id'] = id_info['sub']
        #current_app.logger.debug(f"User ID: {id_info['sub']}")
        session['user_email'] = id_info['email']
        current_app.logger.debug(f"User Email: {id_info['email']}")
        
        return redirect(url_for('emails'))
    except Exception as e:
        current_app.logger.error(f"Authorization error: {str(e)}")
        return jsonify(error="Authorization failed"), 401

@app.route('/emails')
@login_required
def emails():
		return render_template('tinder.html')

@app.route('/tinder')
@login_required
def tinder():
    return render_template('tinder.html')

@app.route('/api/emails')
@login_required
def get_emails():
    try:
        #current_app.logger.debug('Fetching credentials from session.')
        google_token = session['google_token']
        #current_app.logger.debug(f"Session google_token: {google_token}")

        # Ensure all required fields are present
        if 'client_id' not in google_token:
            current_app.logger.debug("Client ID not in Google Token, adding from config")
            google_token['client_id'] = current_app.config['GOOGLE_CLIENT_ID']
        if 'client_secret' not in google_token:
            current_app.logger.debug("Client secret not in Google Token, adding from config")
            google_token['client_secret'] = current_app.config['GOOGLE_CLIENT_SECRET']
        if 'refresh_token' not in google_token:
            google_token['refresh_token'] = session.get('refresh_token')
            if google_token['refresh_token'] is None:
                #current_app.logger.error("No refresh token available. Reauthorization required.")
                google_token['refresh_token'] = "hehehe"          
			#return jsonify(error='No refresh token. Please reauthorize the application.'), 401
        if 'token_uri' not in google_token:
            google_token['token_uri'] = 'https://oauth2.googleapis.com/token'

        # Creating Credentials manually with required fields
        credentials = Credentials(
            google_token['access_token'],
            refresh_token=google_token['refresh_token'],
            token_uri=google_token['token_uri'],
            client_id=google_token['client_id'],
            client_secret=google_token['client_secret']
        )

        #current_app.logger.debug(f"Credentials: {credentials}")

        # Building the Gmail service
        service = build('gmail', 'v1', credentials=credentials)

        current_app.logger.debug('Calling Gmail API to fetch messages.')
        results = service.users().messages().list(userId='me', maxResults=35).execute()
        messages = results.get('messages', [])
        
        current_app.logger.debug(f'{len(messages)} messages fetched.')
        emails = []
        for message in messages:
            current_app.logger.debug(f'Fetching details for message ID: {message["id"]}')
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = {header['name'].lower(): header['value'] for header in msg['payload']['headers']} #Using this to pull subject, sender, date
            labels = msg.get('labelIds', [])  # Check if the message has the label "Unsubscribes"
            #current_app.logger.debug(f"Label IDs: {labels}") #Print the label IDs
            is_unsubscribes = 'Label_7490296533802130438' in labels 
            number_from_sender = number_of_emails_from_sender(service, headers['from'])
						#Featching the email body and extracing the iamges
            parts = msg['payload'].get('parts', [])
            images = []
            for part in parts:
               if part['mimeType'] == 'text/html':
                 body = part['body']['data']
                 html_content = base64.urlsafe_b64decode(body).decode('utf-8') # decode the base64 encoded HTML content
                 soup = BeautifulSoup(html_content, 'html.parser')
                 image_tags = soup.find_all('img')
                 for image_tag in image_tags:
                   image_url = image_tag['src']
                   images.append(image_url)
					
					
            emails.append({
                'id': msg['id'],
                'subject': headers.get('subject', 'No Subject'),
                'sender': headers.get('from', 'Unknown Sender'),
                'date': headers.get('date', 'Unknown Date'),
								'images': images,
								'count_from_sender': number_from_sender,
                'is_unsubscribes': is_unsubscribes  # Add the label information to the email data
            })
        
        current_app.logger.debug('Returning list of emails.')
        return jsonify(emails)
    except Exception as e:
        current_app.logger.error(f'Error fetching emails: {str(e)}')
        return jsonify(error='Failed to fetch emails'), 500

@app.route('/api/emails/<email_id>', methods=['DELETE'])
@login_required
def delete_email(email_id):
    try:
        #current_app.logger.debug('Fetching credentials from session.')
        google_token = session['google_token']
        #current_app.logger.debug(f"Session google_token: {google_token}")

        # Ensure all required fields are present
        if 'client_id' not in google_token:
            google_token['client_id'] = current_app.config['GOOGLE_CLIENT_ID']
        if 'client_secret' not in google_token:
            google_token['client_secret'] = current_app.config['GOOGLE_CLIENT_SECRET']
        if 'refresh_token' not in google_token:
            google_token['refresh_token'] = session.get('refresh_token')
            if google_token['refresh_token'] is None:
                #current_app.logger.error("No refresh token available. Reauthorization required.")
                google_token['refresh_token'] = "hehehe" # For some reason having ANYTHING in this field causes the app to work.
								#return jsonify(error='No refresh token. Please reauthorize the application.'), 401
        if 'token_uri' not in google_token:
            google_token['token_uri'] = 'https://oauth2.googleapis.com/token'

        # Creating Credentials manually with required fields
        credentials = Credentials(
            google_token['access_token'],
            refresh_token=google_token['refresh_token'],
            token_uri=google_token['token_uri'],
            client_id=google_token['client_id'],
            client_secret=google_token['client_secret']
        )

        #current_app.logger.debug(f"Credentials: {credentials}")

        # Building the Gmail service
        service = build('gmail', 'v1', credentials=credentials)

        #current_app.logger.debug(f'Attempting to delete email with ID: {email_id}')
        # Call the Gmail API to delete the message
        service.users().messages().delete(userId='me', id=email_id).execute()

        current_app.logger.debug(f'Successfully deleted email with ID: {email_id}')
        return jsonify(success=True, message=f'Email {email_id} deleted.')
    except Exception as e:
        current_app.logger.error(f'Error deleting email: {str(e)}')
        return jsonify(error=f'Failed to delete email {email_id}'), 500

@app.route('/api/emails/delete_all/<sender_email>', methods=['DELETE'])
@login_required
def delete_emails_from_sender(sender_email):
    try:
        google_token = session['google_token']
        if 'client_id' not in google_token:
            current_app.logger.debug("Client ID not in Google Token, adding from config")
            google_token['client_id'] = current_app.config['GOOGLE_CLIENT_ID']
        if 'client_secret' not in google_token:
            current_app.logger.debug("Client secret not in Google Token, adding from config")
            google_token['client_secret'] = current_app.config['GOOGLE_CLIENT_SECRET']
        if 'refresh_token' not in google_token:
            google_token['refresh_token'] = session.get('refresh_token')
            if google_token['refresh_token'] is None:
                # current_app.logger.error("No refresh token available. Reauthorization required.")
                google_token['refresh_token'] = "hehehe"
        if 'token_uri' not in google_token:
            google_token['token_uri'] = 'https://oauth2.googleapis.com/token'
        credentials = Credentials(
            google_token['access_token'],
            refresh_token=google_token['refresh_token'],
            token_uri=google_token['token_uri'],
            client_id=google_token['client_id'],
            client_secret=google_token['client_secret']
        )
        service = build('gmail', 'v1', credentials=credentials)
    except Exception as e:
        current_app.logger.error(f'Error initializing Gmail service: {str(e)}')
        return jsonify(error=f'Failed to initialize Gmail service for {sender_email}'), 500
    
    try:
        # Get message IDs of all emails from the specific sender
        results = service.users().messages().list(userId='me', q='from:' + sender_email).execute()
        messages = results.get('messages', [])
        message_ids = [message['id'] for message in messages]
        current_app.logger.debug(f'Message IDs: {message_ids}')
    except Exception as e:
        current_app.logger.error(f'Error fetching message IDs: {str(e)}')
        return jsonify(error=f'Failed to fetch emails from {sender_email}'), 500
    
    for message_id in message_ids:
        try:
            service.users().messages().trash(userId='me', id=message_id).execute()
            current_app.logger.debug(f'Successfully deleted message ID: {message_id}')
        except Exception as e:
            current_app.logger.error(f'Failed to delete message ID: {message_id}. Error: {str(e)}')
    
    return jsonify(success=True, message=f'Emails from {sender_email} deleted.')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
