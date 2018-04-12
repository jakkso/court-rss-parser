"""
This module contains unittests.
"""

import os
import sqlite3
import unittest

from database import Database
from feed import Feed

DB = 'test.db'
EMAIL = 'god_of_wine@iron_throne.com'
URL = 'www.bobby-b.com/god_of_wine.html'


class TestDatabase(unittest.TestCase):
    """
    Tests for Database class
    """

    def setUp(self):
        """
        if database file isn't in dir, creates database & tables
        :return: None
        """
        files = os.listdir(os.path.dirname(__file__))
        if DB not in files:
            Database(DB).create_tables()

    def tearDown(self):
        """
        Deletes database file
        :return: None
        """
        os.remove(DB)

    def test_table_creation(self):
        """
        gets list of names from sqlite_master table, ensures that user &
        search_terms are present in said list
        :return: None
        """
        with Database(DB) as data:
            data.cursor.execute('select name from sqlite_master')
            tables = [item[0] for item in data.cursor.fetchall()]
            self.assertIn('users', tables)
            self.assertIn('search_terms', tables)
            self.assertIn('issues', tables)
            self.assertIn('user_issues', tables)

    def test_add_user(self):
        """
        Adds user, confirms that user was added, confirms that adding
        duplicate email raises sql3.IntegrityError
        :return: None
        """
        with Database(DB) as data:
            data.add_user(name='jon snow',
                          email_address='jon@secret_targ.edu')
            data.cursor.execute('SELECT name FROM users')
            john = [item[0] for item in data.cursor.fetchall()]
            self.assertEqual(john[0], 'jon snow')
            self.assertEqual(len(john), 1)
            data.add_user(name='bobby b', email_address=EMAIL)
            data.cursor.execute('SELECT name FROM users')
            two_users = [item for item in data.cursor.fetchall()]
            self.assertEqual(2, len(two_users))
            with self.assertRaises(sqlite3.IntegrityError):
                data.add_user(name='bobby b', email_address=EMAIL)

    def test_add_search_term(self):
        """
        Adds user, adds search term, confirms that item was added correctly
        :return: None
        """
        with Database(DB) as data:
            data.add_user(name='bobby b', email_address=EMAIL)
            data.add_search_term(email_address=EMAIL,
                                 search_term='gods I was strong')
            data.cursor.execute('SELECT term FROM search_terms WHERE '
                                'user_id = ?', (1,))
            searches = data.cursor.fetchall()
            self.assertEqual(1, len(searches))
            self.assertEqual('gods I was strong', searches[0][0])

    def test_remove_user(self):
        """
        Adds user & a pair of searches, then removes the user,
         confirms that the user and searches were removed
        :return: None
        """
        with Database(DB) as data:
            data.add_user(name='bobby b', email_address=EMAIL)
            data.add_search_term(email_address=EMAIL,
                                 search_term='gods I was strong')
            data.add_search_term(email_address=EMAIL,
                                 search_term='breastplate stretcher')
            data.remove_user(email_address=EMAIL)
            data.cursor.execute('SELECT term FROM search_terms'
                                ' WHERE user_id = ?', (1,))
            searches = data.cursor.fetchall()
            self.assertEqual(0, len(searches))
            data.add_user(name='bobby b', email_address=EMAIL)
            data.add_url_html(URL)
            data.add_user_issue(email_address=EMAIL, url=URL)
            data.remove_user(EMAIL)
            data.cursor.execute('SELECT term FROM search_terms'
                                ' WHERE user_id = ?', (1,))
            searches = data.cursor.fetchall()
            self.assertEqual(0, len(searches))
            data.cursor.execute('SELECT * from user_issues')
            issues = data.cursor.fetchall()
            self.assertEqual(issues, [])

    def test_remove_search_term(self):
        """
        Adds user & pair of search terms, removes those search terms,
        confirming the removal, also confirming that int or str types
        are acceptable.
        :return: None
        """
        with Database(DB) as data:
            data.add_user(name='bobby b', email_address=EMAIL)
            data.remove_search_term(email_address=EMAIL,
                                    term='')
            data.add_search_term(email_address=EMAIL,
                                 search_term='gods I was strong')
            data.add_search_term(email_address=EMAIL,
                                 search_term='breastplate stretcher')
            data.remove_search_term(email_address=EMAIL,
                                    term='gods I was strong')
            data.cursor.execute('SELECT term FROM search_terms')
            searches = data.cursor.fetchall()
            self.assertEqual(len(searches), 1)
            data.remove_search_term(email_address=EMAIL,
                                    term='breastplate stretcher')
            data.cursor.execute('SELECT term FROM search_terms')
            searches = data.cursor.fetchall()
            self.assertEqual(len(searches), 0)

    def test_get_search_terms(self):
        """
        Adds user & pair of search terms, confirms that searching for terms
        with an invalid email address raises ValueError, then confirms the
        search terms were retrieved correctly.
        :return: None
        """
        with Database(DB) as data:
            data.add_user(name='bobby b', email_address=EMAIL)
            data.add_search_term(email_address=EMAIL,
                                 search_term='gods I was strong')
            data.add_search_term(email_address=EMAIL,
                                 search_term='breastplate stretcher')
            terms = data.get_search_terms(email_address=EMAIL)
            self.assertEqual(['gods I was strong', 'breastplate stretcher'],
                             terms)

    def test_get_users(self):
        """
        Adds a pair of users, confirms via get_users
        :return: None
        """
        with Database(DB) as data:
            data.add_user(name='bobby b', email_address=EMAIL)
            data.add_user(name='jon snow',
                          email_address='jon@secret_targ.edu')
            data.cursor.execute('SELECT name, email_address FROM users')
            users = data.cursor.fetchall()
            bobby, jon = users
            self.assertEqual(('bobby b', EMAIL), bobby)
            self.assertEqual(('jon snow', 'jon@secret_targ.edu'), jon)

    def test_add_url_text(self):
        """
        Adds url to issues, confirms it, confirms that it raises when
        identical url and None are added
        :return: None
        """
        with Database(DB) as data:
            data.add_url_html(url=URL, html='')
            data.cursor.execute('SELECT url FROM issues')
            url = data.cursor.fetchall()[0][0]
            self.assertEqual(URL, url)
            with self.assertRaises(sqlite3.IntegrityError):
                data.add_url_html(URL)
                data.add_url_html(None)

    def test_get_urls(self):
        """
        Confirms that empty database returns empty list, Adds URLs, then
        confirms that list of URLs present in database are returned as
        expected.
        :return: None
        """
        with Database(DB) as data:
            urls = data.get_urls()
            self.assertEqual([], urls)
            data.add_url_html(URL)
            data.add_url_html('google.com')
            urls = data.get_urls()
            self.assertIn(URL, urls)
            self.assertIn('google.com', urls)

    def test_add_user_issue(self):
        """
        Adds user & issue to database, confirms that invalid email and urls
        raise ValueError, confirms that the correct ids were inserted.
        :return: None
        """
        with Database(DB) as data:
            data.add_user('bobby b', EMAIL)
            data.add_url_html(URL)
            with self.assertRaises(ValueError):
                data.add_user_issue(email_address=EMAIL, url='')
                data.add_user_issue(email_address='', url=URL)
            data.add_user_issue(EMAIL, URL)
            data.cursor.execute('SELECT * from user_issues')
            user_issues = data.cursor.fetchone()
            self.assertEqual((1, 1, 1), user_issues)

    def test_get_user_issues(self):
        """
        adds three users, adds searches & user_issues for two, confirms urls
        retreived as what they should be.
        :return: None
        """
        with Database(DB) as data:
            data.add_user('bobby b', EMAIL)
            data.add_user('jon', 'jon@secret_targ.edu')
            data.add_user('dany', 'nutty_queen@astapor.net')
            data.add_url_html(URL)
            data.add_url_html('google.com')
            data.add_url_html('yahoo.com')
            data.add_user_issue(EMAIL, URL)
            data.add_user_issue(EMAIL, 'google.com')
            data.add_user_issue('jon@secret_targ.edu', 'yahoo.com')
            urls = data.get_user_issues(EMAIL)
            self.assertEqual([URL, 'google.com'], urls)
            urls = data.get_user_issues('jon@secret_targ.edu')
            self.assertEqual(['yahoo.com'], urls)
            urls = data.get_user_issues('nutty_queen@astapor.net')
            self.assertEqual(urls, [])


class TestFeed(unittest.TestCase):
    """
        Tests for Feed class
        """

    def setUp(self):
        """
        if database file isn't in dir, creates database & tables
        :return: None
        """
        files = os.listdir(os.path.dirname(__file__))
        if DB not in files:
            Database(DB).create_tables()

    def tearDown(self):
        """
        Deletes database file
        :return: None
        """
        os.remove(DB)

    def test_users(self):
        """
        Add user & some search terms, confirm that name, email and
        search_terms are correct
        :return: None
        """
        with Feed(DB) as feed:
            feed.add_user('bobby b', EMAIL)
            feed.add_search_term(EMAIL, 'WINE')
            feed.add_search_term(EMAIL, 'WARHAMMERS')
            for user in feed.users():
                self.assertEqual(user.name, 'bobby b')
                self.assertEqual(user.email_address, EMAIL)
                self.assertEqual(user.search_terms, ['WINE', 'WARHAMMERS'])

    def test_text_search(self):
        """
        Add
        :return: None
        """
        with Feed(DB) as feed:
            feed.add_user('bobby b', EMAIL)
            feed.add_search_term(EMAIL, 'WINE')
            feed.add_search_term(EMAIL, 'WARHAMMERS')
            feed.add_url_html('google.com')
            for user in feed.users():
                hits = feed._text_search('WINE and WARHAMMERS', user, 'google.com')
                self.assertEqual(['WINE', 'WARHAMMERS'], hits)
            issues = feed.get_user_issues(EMAIL)
            self.assertEqual(issues, ['google.com'])


if __name__ == '__main__':
    unittest.main()
