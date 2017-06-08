import os
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

RDB_HOST = 'localhost'
RDB_PORT = 28015

# Datbase is todo and table is notes
PROJECT_DB = 'todo'
PROJECT_TABLE = 'notes'

# Set up db connection client
db_connection = r.connect(RDB_HOST,RDB_PORT)


# Function is for cross-checking database and table exists
def db_setup(table):
    try:
        r.db_create(PROJECT_DB).run(db_connection)
        print('Database setup completed.')
    except RqlRuntimeError:
        try:
            r.db(PROJECT_DB).table_create(table).run(db_connection)
            print('Table creation completed')
        except:
            print('Table already exists.Nothing to do')

db_setup("notes")
