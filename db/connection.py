#connection.py
import sqlite3




def get_connection():
    return sqlite3.connect("datos.db")  # nombre del archivo de tu BD
