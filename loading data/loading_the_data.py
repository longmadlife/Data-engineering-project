
import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine 
# password from environment var
pwd = 'Long1511@'
uid = 'Long'
server = "localhost"
database = "retail_data"
employee_df   = pd.read_csv('employyee_data.csv')
# Postgres
engine = create_engine(f'postgresql://{uid}:{pwd}@{server}:5432/retail_data')
def load(df, table_name):
    try: 
        rows_imported = 0
        print(f'importing rows {rows_imported} to {rows_imported + len(df)}... fro table {table_name}')
        # save df to postgres
        df.to_sql(f'stg_{table_name}', engine , if_exists= 'replace', index = False)
        rows_imported += len(df)
        print("data imported successful")
    except Exception as e:
        print("data load error: " + str(e))
load(employee_df, employee_df)