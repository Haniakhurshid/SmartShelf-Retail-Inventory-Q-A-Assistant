import sqlite3

DB_FILE = "inventory.db"

def get_connection():
    return sqlite3.connect(DB_FILE)
