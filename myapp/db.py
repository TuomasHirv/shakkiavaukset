"""Module handles the sqlite integration"""
import sqlite3
from flask import g

def get_connection():
    """Gets the connection to the database"""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
    """Used to add,delete or alter information in the database"""
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    """Gets the id of the last inserted item"""
    return g.last_insert_id

def query(sql, params=None):
    """Used to get infomation from the database"""
    if params is None:
        params = []

    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
