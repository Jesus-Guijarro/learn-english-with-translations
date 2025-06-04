import sqlite3
import os

def create_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "lists.db")
    return sqlite3.connect(db_path)