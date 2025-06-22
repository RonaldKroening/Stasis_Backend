import json
import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'dbname': 'db',
    'user': 'admin',
    'password': 'adminpass',
    'host': 'localhost',
    'port': '5432'
}


# with open('myapp_stock_db.json', 'r') as file:
#     data = json.load(file)

# conn = psycopg2.connect(**DB_CONFIG)
# cursor = conn.cursor()

# create_table_query = """
# CREATE TABLE IF NOT EXISTS stocks (
#     ticker TEXT PRIMARY KEY,
#     name TEXT,
#     description TEXT,
#     industry TEXT,
#     sector TEXT,
#     djia BOOLEAN,
#     sp500 BOOLEAN,
#     market_capitalization BIGINT,
#     basic_eps FLOAT,
#     diluted_eps FLOAT,
#     dividend_yield FLOAT,
#     free_cash_flow BIGINT,
#     net_income BIGINT,
#     pe_ratio FLOAT,
#     ps_ratio FLOAT,
#     profit_margin FLOAT,
#     revenues BIGINT,
#     total_equity BIGINT,
#     total_liabilities BIGINT,
#     last_updated DATE,
#     similarTo TEXT
# );
# """


# cursor.execute(create_table_query)

# # Insert data into the table
# insert_query = sql.SQL("""
# INSERT INTO stocks (
#     ticker, name, description, industry, sector, djia, sp500, 
#     market_capitalization, basic_eps, diluted_eps, dividend_yield, 
#     free_cash_flow, net_income, pe_ratio, ps_ratio, profit_margin, 
#     revenues, total_equity, total_liabilities, last_updated, similarTo
# ) VALUES (
#     %(ticker)s, %(name)s, %(description)s, %(industry)s, %(sector)s, %(djia)s, %(sp500)s, 
#     %(market_capitalization)s, %(basic_eps)s, %(diluted_eps)s, %(dividend_yield)s, 
#     %(free_cash_flow)s, %(net_income)s, %(pe_ratio)s, %(ps_ratio)s, %(profit_margin)s, 
#     %(revenues)s, %(total_equity)s, %(total_liabilities)s, %(last_updated)s, %(similar)s
# )
# ON CONFLICT (ticker) DO UPDATE SET
#     name = EXCLUDED.name,
#     description = EXCLUDED.description,
#     industry = EXCLUDED.industry,
#     sector = EXCLUDED.sector,
#     market_capitalization = EXCLUDED.market_capitalization,
#     basic_eps = EXCLUDED.basic_eps,
#     diluted_eps = EXCLUDED.diluted_eps,
#     dividend_yield = EXCLUDED.dividend_yield,
#     free_cash_flow = EXCLUDED.free_cash_flow,
#     net_income = EXCLUDED.net_income,
#     pe_ratio = EXCLUDED.pe_ratio,
#     ps_ratio = EXCLUDED.ps_ratio,
#     profit_margin = EXCLUDED.profit_margin,
#     revenues = EXCLUDED.revenues,
#     total_equity = EXCLUDED.total_equity,
#     total_liabilities = EXCLUDED.total_liabilities,
#     last_updated = EXCLUDED.last_updated,
#     similarTo = EXCLUDED.similarto;
# """)

# for entry in data:
#     cursor.execute(insert_query, entry)

# # Commit changes and close connection
# conn.commit()
# cursor.close()
# conn.close()

# print("Data successfully inserted into PostgreSQL database.")


# Connect to the database
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Select and print the first element
cursor.execute("SELECT * FROM stocks LIMIT 1;")
first_entry = cursor.fetchone()

# Display result
print("First entry in the table:", first_entry)

# Close the connection
cursor.close()
conn.close()
