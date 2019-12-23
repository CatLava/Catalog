# Readme for this document

This Web application is for a development and not approved for production
The application is configured to run on a local host vagrant machine in a contained
environment.
The file contains all the necessary components to run but the following packages
are required to successfully run the application with Python 2.
## Required environment
This web application is set up in a vagrant VM envirnoment that encapsulates all the necessary dependencies to function. More details can be seen here
https://www.vagrantup.com/

### Packages Required:
Flask, sqlalchemy, httplib2, json, requests, oauth2client and sqllite
Below steps will have this app fully functioning

1. Run the catalog_database.py to create the database catalog.db
The database will create three tables, one of users, another for
junkyard main items, and the last table for main item additional additions

2. Afterwards populate the database and run pop_items.py. There is only one
user ID, so those should be uneditable unless that user logs in.

3. Now the web app can be run with application.py

Command line orders, with these three commands the application is up and operational with sample data:
./catalog_database.py
./pop_items.py
./application.py


### Navigating the web app.
The premise of the web app is a junkyard repository
visit http://localhost:5000 to see the main page welcoming to the
Junkyard. At this point, the user can choose to signin or browse the public facing website
There is a full implementation of CRUD options that only can occur
if they can login and verify. There are various checks of login_session.
Hitting login will automatically add the user to the database with their
gplus ID.

The authentication method is integrated with google API.
The login will create the user if there are not recognized in the
database.
### Issues:
This web application is bare bones and is no shape to handle a high
magnitude of requests. Checks and safety protocols are weak but in place.

Enjoy this web application and please report any bugs

JSON endpoints
'/catalog/JSON'
'/catalog/<int:item_id>/JSON'

#### Future Plans :
Future plans for this application is personal implementation on AWS servers

#### Acknowledgements:
Inspiration and guidance for this application was provided by Udacity Full stack course and all their contributors.
