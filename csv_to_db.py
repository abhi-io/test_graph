import pandas as pd
from sqlalchemy import create_engine

# Replace these variables with your actual database details
db_username = 'testuserPassw0rd'
db_password = 'Passw0rd'
db_host = '127.0.0.1'
db_port = '5002'
db_name = 'main_module'
csv_file_path = 'historic_articles.csv' 
# Read CSV file
data = pd.read_csv(csv_file_path)

# Create database connection
engine = create_engine(f'postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

# Insert data into the database
# Replace 'your_table_name' with the actual table name you want to insert data into
data.to_sql('news_articles', engine, if_exists='append', index=False)
