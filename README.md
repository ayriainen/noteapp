# Note App

This app is a project for the University of Helsinki course TKT20019 Databases and Web Programming. It closely follows the guidelines set in the course. It's a web app for creating notes and sharing them with others.


## Functions

* User can create an account and log in to the application.
* User can add, edit and delete notes.
* User can add images to notes.
* User can see notes they have created and notes shared with them.
* User can search notes by keyword.
* App has a user page that displays statistics and notes created by the user.
* User can select one or more classifications for notes (for example work, personal, priority).
* User can share notes with other users (read only).

## Installation

Install `flask` library:

```
$ pip install flask
```

Create the database tables and add initial data:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

You can start the app with:

```
$ flask run
```
