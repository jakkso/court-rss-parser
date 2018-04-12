#! /usr/bin/python3.6
"""
This module contains the CLI functionality for the project.
"""
import argparse
import sqlite3

from configuration import Config
from feed import Feed


def main():
    """
    Handles CLI interactions
    :return: None
    """
    with Feed(Config.database) as feed:
        feed.create_tables()
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='Used to add user.  Type --name, '
                        'followed by the name surrounded by quotes, like so: '
                        '--name "John User".  Must be used with --email.')
    parser.add_argument('--email', help='Type --email, followed by the email'
                        ' address, like so: --email john.user@email.com'
                        '  Must be used to add or remove a user and to add '
                        ' or remove search terms.')
    parser.add_argument('-d', '--delete',
                        help='Deletes email from database')
    parser.add_argument('-uf', '--users_from_file', help='Add users from text'
                        ' file.  Text file should be a line-separated list of'
                        ' users, with names separated from email addresses by'
                        ' a comma')

    parser.add_argument('--add_term', help='Search term to add.  Use with --email'
                        ' to add a search term to the user associated with '
                        ' the email address.')
    parser.add_argument('-t', '--terms_from_file', help='Add search terms '
                        'from file.  Must be used with --email')
    parser.add_argument('-g', '--get_terms', help='Get all search terms '
                        'associated with a user.  Use email address to search,'
                        ' be sure to use lowercase.')
    parser.add_argument('-r', '--remove_term', help='Removes search term '
                        'from user.  Must be used with --email')

    parser.add_argument('-l', '--list_users', action='store_true',
                        help='Prints out list of users and their email '
                        'addresses')
    parser.add_argument('--start', action='store_true',
                        help='Runs the program, refreshing the rss feed and '
                        'sending emails, if needed')
    args = parser.parse_args()

    if args.list_users:
        list_users()
    if args.delete:
        delete_user(args=args)
    if args.users_from_file:
        add_users_from_file(args=args)
    if args.get_terms:
        get_terms(args=args)
    if args.email:
        email(args=args)
    if args.start:
        start()
    if not [arg for arg in args.__dict__ if args.__dict__[arg]]:
        parser.print_help()


def list_users():
    """
    :return: None
    """
    users = Feed(Config.database).get_users()
    if users:
        print('\nCurrent Users')
        print('+' * 80)
        print('Name -- Email Address')
        for user in users:
            name, email_address = user
            print(f'{name} -- {email_address}')
        print('+' * 80)
    else:
        print('No users in database')


def delete_user(args):
    """
    :param args: parser.parse_args() namespace
    :return: None
    """
    answer = input('Are you sure? (y/n)  ')
    if answer == 'y':
        Feed(Config.database).remove_user(args.delete)
    else:
        print('Canceled')


def add_users_from_file(args):
    """
    Reads file and adds users from info found therein.
    :param args: parser.parse_args() namespace
    :return: None
    """
    with open(args.users_from_file) as file:
        for line in file:
            name, email_address = line.split(',')
            add_user(name, email_address.strip().lower())


def get_terms(args):
    """
    :param args: parser.parse_args() namespace
    :return: None
    """
    try:
        terms = Feed(Config.database).get_search_terms(args.get_terms)
        if terms:
            print(f'Search terms associated with {args.get_terms}:')
            for term in terms:
                print(term)
        else:
            print(f'No search terms associated with {args.get_terms}')
    except ValueError:
        print(f'{args.email} not in database!')


def email(args):
    """
    --email flag is used with several different options.  This is split off
    to make it easier to read
    :param args: parser.parse_args() namespace
    :return: None
    """
    if args.name:
        add_user(name=args.name, email_address=args.email)

    if args.add_term:
        Feed(Config.database).add_search_term(email_address=args.email,
                                              search_term=args.add_term.upper())
    if args.terms_from_file:
        with open(args.terms_from_file) as file:
            for line in file:
                Feed(Config.database).add_search_term(email_address=args.email,
                                                      search_term=line.strip().upper())
    if args.remove_term:
        Feed(Config.database).remove_search_term(email_address=args.email,
                                                 term=args.remove_term)


def add_user(name, email_address):
    """
    :param name: str
    :param email_address: str
    :return: None
    """
    try:
        Feed(Config.database).add_user(name, email_address)
        print(f'Adding {name} & {email_address}')
    except sqlite3.IntegrityError:
        print(f'{email_address} already in database!')


def start():
    """
    Calls the table creation and refresh methods.
    :return: None
    """
    print('Running...')
    with Feed(Config.database) as feed:
        feed.refresh()


if __name__ == '__main__':
    main()
    input()
