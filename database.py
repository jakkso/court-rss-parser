"""
This module contains a single class, Database, which handles connections and
queries to the sqlite database
"""
import sqlite3


class Database:
    """
    This class uses sqlite to create a database for usage with a rss
    feed search.  Methods written handle adding & removing users and their
    associated search terms from the database.
    """
    def __init__(self, database):
        """
        :param database: str database file
        """
        self._database = database
        self._connection = sqlite3.connect(self._database)
        self._connection.execute('PRAGMA foreign_keys=ON')
        self.cursor = self._connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f'{exc_type} - {exc_val} {exc_tb}')

    def __repr__(self):
        return f"{self.__class__.__name__}({self._database})"

    def __str__(self):
        return f"<{self.__class__.__name__} using {self._database}>"

    def create_tables(self):
        """
        Creates table users if not present.  Used to initialize the database.
        :return: None
        """
        self.cursor.execute('CREATE TABLE IF NOT EXISTS users '
                            '(id INTEGER PRIMARY KEY, '
                            'name TEXT, '
                            'email_address TEXT UNIQUE)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS search_terms '
                            '(id INTEGER PRIMARY KEY, '
                            'term TEXT NOT NULL,'
                            'user_id INTEGER NOT NULL,'
                            'FOREIGN KEY(user_id) REFERENCES users(id))')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS issues '
                            '(id INTEGER PRIMARY KEY,'
                            'url TEXT UNIQUE NOT NULL,'
                            'html TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS user_issues '
                            '(id INTEGER PRIMARY KEY,'
                            'user_id INTEGER,'
                            'issue_id INTEGER,'
                            'FOREIGN KEY(user_id) REFERENCES users(id),'
                            'FOREIGN KEY (issue_id) REFERENCES issues(id))')

    def add_user(self, name, email_address):
        """
        Adds name & email address to database then commits changes.
        Re-raises if email_address already in database
        :param name: str
        :param email_address: str
        :return: None
        """
        self.cursor.execute('INSERT INTO users(name, email_address) '
                            'VALUES (?,?)', (name, email_address),)
        self._connection.commit()

    def remove_user(self, email_address):
        """
        Removes user from database, based upon email address, as well as
        all user searches
        :param email_address: str
        :return: None
        """
        self.cursor.execute('DELETE FROM search_terms WHERE user_id in '
                            '(SELECT id FROM users u WHERE u.email_address = ?)',
                            (email_address,))
        self.cursor.execute('DELETE FROM user_issues WHERE user_id IN '
                            '(SELECT id FROM users u WHERE u.email_address = ?)',
                            (email_address,))
        self.cursor.execute('DELETE FROM users WHERE email_address = ?',
                            (email_address,))
        self._connection.commit()

    def get_users(self):
        """
        :return: List of 2 tuples made up of each name & email address
        """
        self.cursor.execute('SELECT name, email_address FROM users')
        return self.cursor.fetchall()

    def add_search_term(self, email_address, search_term):
        """
        Adds terms to search_terms based on email_address
        :param email_address: str
        :param search_term: str
        :return: None
        """
        self.cursor.execute('INSERT INTO search_terms(term, user_id) '
                            'SELECT ?, id FROM users WHERE email_address = ?',
                            (search_term, email_address))
        self._connection.commit()

    def remove_search_term(self, email_address, term):
        """
        Removes search_term when associated with email_address
        :param email_address: str
        :param term: str
        :return: None
        """
        self.cursor.execute('DELETE FROM search_terms WHERE user_id IN '
                            '(SELECT id FROM users u WHERE u.email_address = ?)'
                            ' AND term = ?',
                            (email_address, term))
        self._connection.commit()

    def get_search_terms(self, email_address):
        """
        If email address absent from database, raises ValueError.
        :param email_address: str
        :return: list of search terms associated with email_address
        """
        self.cursor.execute('SELECT term FROM search_terms JOIN users u ON'
                            ' search_terms.user_id = u.id '
                            'AND u.email_address = ?', (email_address,))
        return [item[0] for item in self.cursor.fetchall()]

    def add_url_html(self, url, html=None):
        """
        adds url to issues table, re-raises if url already in table
        :param url: str
        :param html: str the html from each court roll issue
        :return: None
        """
        if html:
            self.cursor.execute('INSERT INTO issues(url, html) VALUES (?,?)',
                                (url, html))
        else:
            self.cursor.execute('INSERT INTO issues(url) VALUES (?)', (url,))
        self._connection.commit()

    def get_urls(self):
        """
        :return: list of URLs already in database
        """
        self.cursor.execute('SELECT url FROM issues')
        return [item[0] for item in self.cursor.fetchall()]

    def add_user_issue(self, email_address, url):
        """
        Handles associating which user is tied to which issue
        :param email_address: str
        :param url: str issue url
        :return: None
        """
        self.cursor.execute('SELECT id FROM users WHERE email_address = ?',
                            (email_address,))
        user_id = self.cursor.fetchone()
        if user_id is None:
            raise ValueError('Invalid Email address')
        user_id, = user_id
        self.cursor.execute('SELECT id from issues WHERE url = ?', (url,))
        issue_id = self.cursor.fetchone()
        if issue_id is None:
            raise ValueError('Invalid URL')
        issue_id, = issue_id
        self.cursor.execute('INSERT INTO user_issues(user_id, issue_id)'
                            ' VALUES (?,?)', (user_id, issue_id))
        self._connection.commit()

    def get_user_issues(self, email_address):
        """
        :param email_address: str
        :return: list of URLs connected to that email address
        """
        self.cursor.execute('SELECT url from issues WHERE id IN '
                            '(SELECT issue_id FROM user_issues '
                            'WHERE user_id is (SELECT id FROM users '
                            'WHERE email_address is ? ))', (email_address,))

        return [item[0] for item in self.cursor.fetchall()]
