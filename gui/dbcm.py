import sqlite3

class DBCM:
    '''Database context manager'''
    def __init__(self, db_name):
        '''Initialize the database name'''
        self.db_name = db_name

    def __enter__(self):
        '''Connect to SQLite database and return a cursor'''''
        self.conn = sqlite3.connect(self.db_name)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''Commit changes and close connection to the database'''
        self.conn.commit()
        self.conn.close()
