"""
This is very similar to the db.py from the example app, credit there.
"""
import sqlite3
from flask import g

def get_connection():
    """Opening sqlite3 connection."""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    """Writing to db."""
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    """Last inserted row id."""
    return g.last_insert_id

def query(sql, params=[]):
    """Reading db."""
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
