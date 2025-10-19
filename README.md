# Note App

This app is a project for the University of Helsinki course TKT20019 Databases and Web Programming. It closely follows the guidelines set in the course and mimics the structure and style of the course's [example app](https://github.com/pllk/huutokauppa/). It's a simple Python, Flask and SQLite web app for creating notes and sharing them with others.

## Functions

* User can create an account and log in to the application.
* User can add, edit and delete notes.
* User can see notes they have created and notes shared with them.
* User can search notes by keyword.
* App has a user page that displays statistics and notes created by the user.
* User can select one or more classifications for notes (for example work, personal, priority).
* User can share notes with other users who can then comment on the notes.

## Operation/installation

We'll go through the venv operation of the app. After cloning the repository locally, set up venv and install the dependencies (only Flask for now) in the app folder in terminal (Linux/Mac):

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the database tables:

```
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

You can start the app with:

```
python3 app.py
```

Then go to http://localhost:5000 in your browser to operate the app. Macs sometimes hog port 5000 for Airdrop in which case turn off Airdrop Receiver in settings.

When you want to stop just press **CTRL + C**, and you can restart it with the same **python3 app.py** command. If you want to deactivate venv just run the **deactivate** command. You can clear the database by deleting database.db and rerunning its creation.
