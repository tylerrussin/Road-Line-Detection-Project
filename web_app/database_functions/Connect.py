import psycopg2

def connect(DATABASE, USERNAME, PASSWORD, HOST):
    """ Connect to the PostgreSQL database server """
    elephantsql_client = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')

        # Connect to ElephantSQL-hosted PostgreSQL
        elephantsql_client = psycopg2.connect(dbname=DATABASE, user=USERNAME, password=PASSWORD, host=HOST)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    return elephantsql_client