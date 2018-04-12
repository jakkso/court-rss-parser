"""
Contains Config
"""
from os import path


class Config:
    """
    Acts as a container for configuration settings / secrets for sending email.  Used by Feed.
    """
    sender = 'example_gmail_address@gmail.com'
    pw = 'example_app_specific_password'
    host = 'smtp.gmail.com'
    port = '587'
    database = path.join(path.dirname(__file__), 'data.db')
