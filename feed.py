"""
Contains Feed, which handles parsing the rss feed and User, which handles messaging
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from bs4 import BeautifulSoup
import feedparser as fp
from jinja2 import Environment, PackageLoader, select_autoescape
from requests import get

from configuration import Config
from database import Database


class Feed(Database):
    """
    Uses Database's methods in conjunction with its own to parse feed url,
    fetching and parsing page to plain text, searching each text for specific
    terms and email the correct users if the terms are found.
    """
    URL = 'feed://www.scotcourts.gov.uk/feeds/court-of-session-court-rolls'

    def new_urls(self):
        """
        Gets new URLs, adds to database then yields url
        :yield: str, url
        """
        page = fp.parse(self.URL)['entries']
        return [item['link'] for item in page if item['link'] not in
                self.get_urls()]

    def refresh(self):
        """
        Iterates through new_urls, downloading then searching through resulting text.
        Note: text and search terms are upper case, to simplify things.
        """
        new_urls = self.new_urls()
        for url in new_urls:
            print(f'Adding {url}')
            html, text = self._downloader(url)
            self.add_url_html(url, html)
            for user in self.users():
                hits = self._text_search(text.upper(), user, url)
                if hits:
                    print(f'Sending alert to {user.name}')
                    user.send_email(hits, url)

    def users(self):
        """
        :yield: User obj containing name, email address and list of
        search_terms
        """
        users = self.get_users()
        for user in users:
            name, email_address = user
            search_terms = self.get_search_terms(email_address)
            yield User(name, email_address, search_terms)

    def _text_search(self, text, user, url):
        """
        Searches through text for any of the user's search terms, if found,
        sends email.
        :param text: str, block of text from Court Roll Issue
        :param user: User obj
        :param url: str Court Roll Issue URL
        :return: search term hits
        """
        search_term_hits = []
        for term in user.search_terms:
            if term in text:
                search_term_hits.append(term)
                self.add_user_issue(user.email_address, url)
        return search_term_hits

    @staticmethod
    def _downloader(url):
        """
        Uses BeautifulSoup to extract a block of text through which to search
        :param url: str
        :return: tuple, html and plain text of Court Roll issue downloaded
        """
        soup = BeautifulSoup(get(url).content, 'html.parser')
        selection = soup.select('.courtRollContent')[0]
        html, text = selection.prettify(), selection.get_text()
        return html, text


class User:
    """
    Object containing a person's name, email address and list of search terms
    associated with them, As well as a methods used to send an email to them
    """
    __slots__ = ['name', 'email_address', 'search_terms']

    def __init__(self, name, email_address, search_terms):
        """
        :param name: str person's name
        :param email_address: str person's email address
        :param search_terms: list, search terms associated with this person
        """
        self.name = name
        self.email_address = email_address
        self.search_terms = search_terms

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}'," \
               f" '{self.email_address}', '{self.search_terms}'))"

    def __str__(self):
        return f'<User: {self.name}>'

    def send_email(self, search_term_hits, url):
        """
        Sends email message to a user.email_address containing the url &
        search term hits
        :param search_term_hits: list of search terms that were present in
        the issue searched
        :param url: str, url to a court roll issue
        :return: None
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Court Roll Notification'
        msg['From'] = Config.sender
        msg['To'] = self.email_address
        msg.attach(MIMEText(self._render_text(search_term_hits, url), 'plain'))
        msg.attach(MIMEText(self._render_html(search_term_hits, url), 'html'))
        server = smtplib.SMTP(host=Config.host, port=Config.port)
        server.starttls()
        server.login(user=Config.sender, password=Config.pw)
        server.sendmail(Config.sender, self.email_address, msg.as_string())
        server.quit()

    def _render_text(self, search_term_hits, url):
        """
        Renders Text message for email
        :param search_term_hits: list of search_terms
        :param url: str
        :return: text-formatted email message
        """
        env = Environment(
            loader=PackageLoader('message', 'templates'),
            autoescape=select_autoescape(['.txt'])
        )
        template = env.get_template('base.txt')
        return template.render(name=self.name,
                               search_terms=search_term_hits,
                               url=url)

    def _render_html(self, search_term_hits, url):
        """
        Renders HTML message for email
        :param search_term_hits: list of search_terms
        :param url: str
        :return: HTML-formatted email message
        """
        env = Environment(
            loader=PackageLoader('message', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('base.html')
        return template.render(name=self.name,
                               search_terms=search_term_hits,
                               url=url)
