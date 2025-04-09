import psycopg2
from tabulate import tabulate

# Database connection details
DB_CONFIG = {
    'NAME': 'db',       # Replace with your database name
    'USER': 'admin',    # Replace with your database username
    'PASSWORD': 'adminpass',  # Replace with your database password
    'HOST': 'localhost',          # Replace with your database host
    'PORT': '5432',               # Replace with your database port
}

# Table name to pretty-print
TABLE_NAME = 'myapp_stock'  # Replace with your table name

# Connect to the PostgreSQL database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG['NAME'],
            user=DB_CONFIG['USER'],
            password=DB_CONFIG['PASSWORD'],
            host=DB_CONFIG['HOST'],
            port=DB_CONFIG['PORT'],
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def fetch_table_names(conn):
    try:
        with conn.cursor() as cursor:
            # Query to get all table names
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public';
            """)
            tables = cursor.fetchall()
            return [table[0] for table in tables]  # Extract table names from the result
    except Exception as e:
        print(f"Error fetching table names: {e}")
        return None

# Pretty-print the table names
def pretty_print_table_names(table_names):
    if not table_names:
        print("No tables found in the database.")
        return
    print("Tables in the database:")
    for i, table_name in enumerate(table_names, start=1):
        print(f"{i}. {table_name}")


def fetch_table_data(conn, table_name):
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]  # Get column names
            return columns, rows
    except Exception as e:
        print(f"Error fetching data from the table: {e}")
        return None, None

# Pretty-print the table data
def pretty_print_table(columns, rows):
    if not rows:
        print("No data found in the table.")
        return
    print(tabulate(rows, headers=columns, tablefmt="pretty"))

conn = connect_to_db()
if conn:
    table_names = fetch_table_names(conn)
    # if table_names:
    #     pretty_print_table_names(table_names)
    columns, rows = fetch_table_data(conn, TABLE_NAME)
    if columns and rows:
        pretty_print_table(columns, rows)

    conn.close()