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
