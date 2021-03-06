## Court Roll Parser

#### Description
This program makes use of an sqlite3 database, using python, along with several python libraries, to parse an RSS feed
and send email alerts to users based on search phrases.

##### Note on using command prompt in Windows
This program uses the command line as an interface.  Most people have not used this type of interface much, but it is
quite powerful and not as difficult to use as one might assume.  Once you have downloaded the program, open the folder
it is located in and, while holding the `shift` key, right click.  In the menu that opens, look for an option labeled
`open cmd here`.  That should open a command prompt in the correct location.


#### Installation


##### Windows Installation
Windows does not include python in its default installation, so you'll have to install it.
These instructions assume that you're using Windows Vista or newer as this program will not work with 
older versions of Windows.


<b>Python Installation</b> 

Download [this](https://www.python.org/ftp/python/3.6.3/python-3.6.3-amd64.exe) file and run it.
When installing, be sure to select the 'Add Python 3.6 to PATH' option, which will make running python programs
easier when using the command line, and then finish installing python, using the standard / recommended options.  
I've linked you to a slightly older version of python (The version that I'm using) but newer versions should work. 
I would not recommend that install v3.7, as it's a beta version.

Next open a command prompt and type `python -V`, if python was installed correctly it will print `Python 3.6.3` 
as a response.  If it spits an error, it's likely that either the PATH variable was not set correctly or it was
not installed correctly.

<b>Program Installation</b>

Go to [this](https://github.com/jakkso/court-rss-parser) address and download the repository to wherever is
convenient, but it must be in a folder to which you can read or write.


Python includes a [package manager](https://en.wikipedia.org/wiki/Pip_(package_manager)) 
called [`pip`](https://pypi.python.org/pypi/pip) that allows easy installation of libraries and programs written 
in python.  If you navigate to the program directory, you'll see a file called `requirements.txt`, which is a list
of the libraries that this program uses.  We are going to use `pip` to install them.  Open a command prompt and 
type `py -m pip install -r requirements.txt`.  This command uses pip to install the libraries in `requirements.txt`

<b>Configuration</b>

Next, use `notepad` or another plain text editor to open `configuration.py`.  This file contains the configuration values for 
the program.  In order for the email functionality to work correctly you need to input the correct values in the 
various fields. 
 
 * `sender` is the email address that will send the alerts 
 * `pw` is the password for that account 
 * `host` is the server from which the emails will be sent
 * `port` is the port number that you use to connect to your outgoing mail server
 * `database` is the location of the database file.  By default, the database file will be located in the same 
 directory as the config file.
 
 When you add your sending email address and password, they need to be enclosed in quotes.  I have left the values 
 that gmail uses in `host` and `port`. Due to infosec, you might want to use your own email address, or one setup 
 specifically for this purpose. I do not know how your firm's email system works, so you'll have to talk to IT.
 If you decide to use gmail, you'll need to enable 
 [app-specific passwords](https://support.google.com/mail/answer/185833?hl=en), generate one, and replace 
 `app_specific_password` with the password generated by google.

#### Tutorial

I've written 2 separate command line interfaces, one more suitable for scripting and the other much more user friendly.
The first tutorial covers the user friendly version, the second the traditional command line interface type program.


##### User-Friendly Interface

Open a command prompt in the program directory, and type `py manager.py`, which launches the program.  
In general, you'll navigate around the program by typing number of the option you want and pressing `enter`.  

In the first screen, you see a menu heading, followed by 4 options. 

* `Run Program` Runs the rss feed parser, sending emails to users if search phrases are in the court roll. 
* `User management` Allows you to view current users in the database, as well as add and remove users.
* `Search phrase management` allows you to view, add, and remove search phrases associated with individual users.

If you run the program without adding any users, it will download all the issued court rolls, without sending 
alerts.  I would recommend you do this prior to adding any users / search phrases, as you would probably not want 
to send alerts to people about old court roll issues.

##### Traditional CLI

Open a command prompt and input each command exactly as typed.  Once again, adding a bunch of users and search terms,
and running the program will sending emails about court roll issues from the last year, which might annoy your 
colleagues.

With that said, let's add an example user:

* `py cliy.py --name 'John Smith' --email johnsmith@email.com`
* This will add John Smith and his email address to the database
* Note the quotes around `'John Smith'` - They are required when adding anything that has a space in it

Next, let's give John a few search phrases:

* `py cli.py --email johnsmith@email.com --add_term 'Example Law Firm & Associates'` 
* `py cli.py --email johnsmith@email.com --add_term 'A452A0`
* `py cli.py --email johnsmith@email.com --add_term 'Lord Judge Smith'`

This seems pretty tedious to add each one, item by item.  That's why there's an option to add search terms from a plain
text file.  Using `notepad`, make a new file, with new search phrase is on its own line.  
Then, save as `john_smith_terms.txt`.

Next, type in the following command and run it:

* `py cli.py --email johnsmith@email.com --terms_from_file john_smith_terms.txt`

Next, let's check that the terms were added:

* `py cli.py --get_terms johnsmith@email.com `

Which will print out the search terms associated with `johnsmith@email.com`

Let's say that you want to remove a term from John.  

* `py cli.py --email johnsmith@email.com --remove_term 'A452A0'`

Then we'll confirm that the term was removed:
 * `py cli.py --get_terms johnsmith@email.com `
 
 Okay, now that we have John setup correctly, let's talk about adding more users.  Rather than typing out each user and
 email address into the command prompt, we can load them from a text file, much like the search terms.  Using `notepad`, 
 make another text file, except this time each line will be the user's name and email separated by a comma, like so:
 `Jane Smith, janesmith@email.com`.  Save the file as `example_user_file.txt`.  
 
 To load that file into the database, use this command:
 
 * `py cliy.py --users_from_file example_user_file.txt`
 
 Which will read from the file and add the users to the database.  Let's see how many users are in the database:
 
 * `py cli.py --list_users`
 
 Which prints out the users and their email addresses.  Let's say that you want to remove a user from the database:
 
 * `py cli.py --delete johnsmith@email.com`
 
 Which will prompt you: `Are you sure? (y/n)  ` Inputting `y` and pressing enter will delete the user, along with any
 search terms associated with them.  Inputting anything else will cancel.
 
 Alright, now we know how to interact with the database, how to make it actually run? At this point your database 
 does not have any URLs in it.  If you input any users or search terms into the database and did not remove them, now 
 would be the time to just delete the database.  The program will automatically recreate it when next run.  
 
 Next run:
 
 * `py cliy.py --start`
 
 Since we're running this from an empty database, it will run for a few minutes, downloading every issue to the database,
 After it finishes running, it would be a good time to add users and search terms for each user.
 

Once the database is built and ready to run, simply run the `py cli.py --start` command each day after the new issue is 
published and emails will be sent, if any search terms are found.

### License

MIT License, see LICENSE.txt
