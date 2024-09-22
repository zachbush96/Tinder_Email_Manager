# Email Manager Application

This project is a Python Flask-based web application that allows users to manage their Gmail inbox effectively. It provides features to view, delete, and unsubscribe from emails based on the sender. The frontend interface is styled like a card swipe application, making it visually intuitive to navigate through your emails.

## Features

- **View Emails**: Emails are displayed as swipeable cards with sender, subject, and total count of emails from the sender.
- **Delete Emails**: Swipe left on a card to delete individual emails.
- **Unsubscribe**: Coming soon! Pull 'unsubscribe' links from the email body and place an 'Unsubscribe' button on the card.
- **Delete All Emails from Sender**: Allows deleting all emails from a particular sender with a single click.
- **Speed Optimization**: Lazy loading and prefetching are implemented to speed up the front-end.
- **Email Images**: Pulls images from the email HTML body to be displayed on the front-end cards.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/email-manager.git
2. Navigate to the project directory:
   ```bash
   cd email-manager

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows use `venv\Scripts\activate`

4. Install the dependencies:
   ```bash
   pip install -r requirements.txt

5. Set up environment variables for Flask:
   ```bash
   export SECRET_KEY='your-secret-key'
   export GOOGLE_CLIENT_ID='your-google-client-id'
   export GOOGLE_CLIENT_SECRET='your-google-client-secret'
   export REDIRECT_URI='your-redirect-uri'

6. Run the Flask application:
   ```bash
   flask run

7. Open your browser and go to http://localhost:5000 to access the application.

##Configuration
Set the following environment variables:
```SECRET_KEY: ```Your secret key for Flask session management.
```GOOGLE_CLIENT_ID: ```Your Google OAuth client ID.
```GOOGLE_CLIENT_SECRET: ```Your Google OAuth client secret.
```REDIRECT_URI: ```Redirect URI configured in your Google Cloud project.

##Usage
Login: Click on the login button to authenticate with your Google account.
View Emails: Swipe through the email cards to view your emails.
Delete Email: Swipe left on a card or click the dislike button to delete an individual email.
Delete All from Sender: Click the "Delete All from Sender" button to remove all emails from a particular sender.

##To-Do List
 - [ ] Pull images from email HTML body and display on the front-end card.
 - [ ] Add ability to read complete email from the email body within the card front-end.
 - [ ] Pull 'unsubscribe' links from the email body.
 - [ ] Place 'Unsubscribe' button on the card.
 - [ ] Add the ability to 'Erase All' from a particular sender's email address.
 - [ ] Speed up the front-end with lazy loading and prefetching.
 - [ ] Implement server-side rendering for improved performance.
 - [ ] Add better icons to the front-end.
 - [ ] Display inbox type and other relevant tags on the card.

##Dependencies
Flask
Authlib
Google API Python Client
BeautifulSoup
Other dependencies listed in requirements.txt


