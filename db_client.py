import os
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError






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
            print('Table already exists. Nothing to do')
