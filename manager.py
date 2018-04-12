"""
This module contains an interactive menu script, instead of the standard cli
program that uses flags to do things, intended to be more user friendly.
"""

import os
import sqlite3
import sys

from configuration import Config
from feed import Feed


def top_menu():
    """
    Creates top level menu
    :return: None
    """
    valid = draw_menu('Main Menu',
                      'Run program',
                      'User management',
                      'Search phrase management',
                      'Exit',
                      num_option=True)
    choice = input()
    while choice not in valid:
        draw_menu('Main Menu',
                  'Run program',
                  'User management',
                  'Search phrase management',
                  'Exit',
                  num_option=True)
        choice = input()
    if choice == '1':
        run_parser()
    elif choice == '2':
        user_management()
    elif choice == '3':
        search_phrase_management()
    elif choice == '4':
        exit_program()


def user_management():
    """
    Creates the user management menu
    :return: None
    """
    def list_users():
        """
        Prints out list of current users
        :return: None
        """
        users = Feed(Config.database).get_users()
        if users:
            clear_screen()
            for user in users:
                name, email_address = user
                print(f'{name} - {email_address}')
            input('Press enter to continue')
            user_management()
        else:
            input('No users found, press enter to continue')
            top_menu()

    def add_user():
        """
        Adds user to database
        :return: None
        """
        clear_screen()
        name = input('Enter full name: ')
        email_address = input('Enter email address: ').lower()
        if name == '' or email_address == '':
            input('Blank name or email addresses aren\'t allowed.  Press enter to continue')
            user_management()
        try:
            Feed(Config.database).add_user(name.strip(), email_address.strip())
        except sqlite3.IntegrityError:
            print(f'{email_address} already in database!')
            input('Press enter to continue')
        user_management()

    def add_users_from_file():
        """
        Adds line-separated file of csv names and email addresses to database
        :return: None
        """
        clear_screen()
        print('Create a text file, where each line consists of a users\'s '
              'full name and the user\'s email address, separated by a comma')
        print('Save this file into the same directory as the program file')
        filename = input('Type the full name of the file: ')
        if filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
            with open(filename) as file:
                for line in file:
                    if line.strip():
                        name, email_address = line.split(',')
                        name, email_address = name.strip(), email_address.strip()
                        try:
                            Feed(Config.database).add_user(name, email_address)
                            print(f'Adding {name} - {email_address}')
                        except sqlite3.IntegrityError:
                            print(f'{email_address} already in database!')
            input('Press enter to continue')
            user_management()
        else:
            input('File not found!  Press enter to continue')
            user_management()

    def remove_user():
        """
        Prints users from a dictionary, in order to prevent user error when
        inputting email addresses
        :return: None
        """
        clear_screen()
        users = Feed(Config.database).get_users()
        if users:
            clear_screen()
            user_dict = {i[0] + 1: i[1] for i in enumerate(users)}
            for num, user in user_dict.items():
                print(f'{num}) {user[0]} - {user[1]}')
            print('Press enter with blank input to cancel')
            try:
                choice_ = int(input('User number to delete: '))
            except ValueError:
                input('Canceled, press enter to continue')
                user_management()
            else:
                Feed(Config.database).remove_user(user_dict[choice_][1])
                user_management()
        else:
            input('No users found, press enter to continue')
            user_management()

    valid = draw_menu('User Management',
                      'List users',
                      'Add user',
                      'Add users from file',
                      'Remove user',
                      'Return to main menu',
                      num_option=True)
    choice = input()
    while choice not in valid:
        draw_menu('User Management',
                  'List users',
                  'Add user',
                  'Add users from file',
                  'Remove user',
                  'Return to main menu',
                  num_option=True)
        choice = input()
    if choice == '1':
        list_users()
    elif choice == '2':
        add_user()
    elif choice == '3':
        add_users_from_file()
    elif choice == '4':
        remove_user()
    elif choice == '5':
        top_menu()


def search_phrase_management():
    """
    Creates search phrase management menu
    :return: None
    """

    def add_phrase(email_address):
        """
        Adds a single phrase to user associated with email_address
        :param email_address: str
        :return: None
        """
        clear_screen()
        phrase = input(f'Type search phrase to add: ')
        Feed(Config.database).add_search_term(email_address, phrase.upper())
        search_phrase_management()

    def add_phrases_from_file(email_address):
        """
        Adds phrases from text file
        :param email_address: str
        :return: None
        """
        clear_screen()
        print('Create a text file where each line is a separate search phrase')
        print('Save this file into the same directory as the program file')
        filename = input('Type the full name of the file: ').strip()
        if filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
            with open(filename) as file:
                for line in file:
                    Feed(Config.database).add_search_term(email_address, line.strip().upper())
            print(filename)
            input('pause')
            search_phrase_management()
        else:
            input('File not found!  Press enter to continue')
            search_phrase_management()

    def remove_phrase(email_address):
        """
        Removes phrase from user, constructs a dictionary and prints from that
        to ensure that the phrase is exact (Eliminates user input error)
        :param email_address: str
        :return: None
        """
        clear_screen()
        terms = Feed(Config.database).get_search_terms(email_address)
        if not terms:
            input('No terms found!')
            search_phrase_management()
        else:
            phrase_dict = {i[0] + 1: i[1] for i in enumerate(terms)}
            for num, item in phrase_dict.items():
                print(f'{num}) {item}')
            print('Press enter with blank input to cancel')
            choice_ = int(input('Phrase number to delete: '))
            try:
                ans = phrase_dict[choice_]
                Feed(Config.database).remove_search_term(email_address, term=ans)
                search_phrase_management()
            except ValueError:
                input('Canceling')
                search_phrase_management()

    def search_phrase_menu(users):
        """
        :param users: list of 2-tuple, users names and email addresses.
        Draws the search_phrase_management menu
        :return: None
        """
        clear_screen()
        user_dict = {i[0] + 1: i[1] for i in enumerate(users)}
        print('User selection')
        for num, user in user_dict.items():
            print(f'{num}) {user[0]} - {user[1]}')
        try:
            print('Press enter with blank input to return to main menu')
            email_address = user_dict[int(input('User to manage: '))][1]
            terms = Feed(Config.database).get_search_terms(email_address)
            valid_ = draw_menu('Search Phrase Management',
                               'Print current search terms',
                               'Add search term',
                               'Add search terms from file',
                               'Remove term',
                               'Return to main menu',
                               num_option=True)
            choice_ = input()
            while choice_ not in valid_:
                valid_ = draw_menu('Search Phrase Management',
                                   'Print current search terms',
                                   'Add search term',
                                   'Add search terms from file',
                                   'Remove term',
                                   'Return to main menu',
                                   num_option=True)
                choice_ = input()
            if choice_ == '1':
                if terms:
                    draw_menu(f'Search phrases for {email_address}',
                              *terms,
                              continue_=True)
                else:
                    input('No search phrases found.  Press enter to continue')
                search_phrase_management()
            elif choice_ == '2':
                add_phrase(email_address)
            elif choice_ == '3':
                add_phrases_from_file(email_address)
            elif choice_ == '4':
                remove_phrase(email_address)
            elif choice_ == '5':
                top_menu()
        except ValueError:
            top_menu()

    users = Feed(Config.database).get_users()
    if users:
        search_phrase_menu(users)
    else:
        input('No users found, press enter to continue')
        top_menu()


def draw_menu(menu_name, *args, num_option=None, continue_=None, clear=True):
    """
    :param menu_name: str, printed out to tell user what menu they're using
    :param args: strings, Printed out, used to draw menu
    :param num_option: If selected, will print out statement
    :param continue_: bool, if selected, will insert an input() statement to
    pause execution
    :param clear: Bool, if set to false, will not clear screen
    :return: list of numbers, used to validate input
    """
    if clear:
        clear_screen()
    nums = []
    print(menu_name)
    for num, arg in enumerate(args):
        print(f'{num + 1}) {arg}')
        nums.append(str(num + 1))
    if continue_:
        input('Press enter to continue')
    if num_option:
        print('Enter number option and press enter ')
    return nums


def run_parser():
    """
    Calls Feed.refresh then returns to main menu
    :return: None
    """
    clear_screen()
    print('Running...')
    Feed(Config.database).refresh()
    top_menu()


def clear_screen():
    """
    Clears the screen
    :return: None
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def exit_program():
    """
    Exits program
    :return: None
    """
    clear_screen()
    print('Exiting...')
    sys.exit(0)


if __name__ == '__main__':
    Feed(Config.database).create_tables()
    top_menu()
