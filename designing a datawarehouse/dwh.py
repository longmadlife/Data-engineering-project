# -*- coding: utf-8 -*-

import pandas as pd
import sqlite3
from os import curdir
from datetime import datetime

db_path = r"loading data\retail_data.db"
dwh_path = r"designing a datawarehouse\retail_dwh.db"

book = sqlite3.connect(db_path)
cur = book.cursor()
retail_dwh = sqlite3.connect(dwh_path)
dwcur = retail_dwh.cursor()

"""## Create DIM_DATE table"""
# Create dates
date = []
datee = pd.date_range(start='2020-01-01', end='2025-12-31', freq='D')
for i in range(len(datee)):
  date.append(datetime.strftime(datee[i], format='%Y-%m-%d'))
# create date_df
date_df = pd.DataFrame({'date': date})
date_df['date1'] = date_df['date']
date_df['date1'] = pd.to_datetime(date_df['date1'])

# Thêm cột month và year
date_df['month'] = date_df['date1'].dt.month
date_df['year'] = date_df['date1'].dt.year

# Thêm cột month_name
date_df['month_name'] = date_df['date1'].dt.strftime('%B')

# Thêm cột date_key
date_df['date_key'] = date_df['year'].astype(str) + date_df['month'].astype(str).str.zfill(2) + date_df['date1'].dt.day.astype(str).str.zfill(2)
date_df = date_df.drop('date1', axis=1)
date_df.head()

# Tạo bảng DIM_DATE
dwcur.execute('''
DROP TABLE IF EXISTS DIM_DATE;
''')

dwcur.execute('''
CREATE TABLE DIM_DATE (
    DATE_KEY    INT   NOT NULL  PRIMARY KEY,
    DATE        DATE  NOT NULL,
    MONTH       INT NOT NULL,
    YEAR        INT NOT NULL,
    MONTH_NAME  VARCHAR(50) NOT NULL
);
''')

# Đọc dữ liệu hiện có từ bảng 'CUSTOMER'
existing_data = pd.read_sql('SELECT * FROM DIM_DATE', retail_dwh)

# Loại bỏ các hàng trùng lặp khỏi DataFrame 'customer_df'
date_df = date_df[~date_df.apply(tuple,1).isin(existing_data.apply(tuple,1))]

# Insert data từ dataframe qua datawarehouse
date_df.to_sql('DIM_DATE', retail_dwh, if_exists='append', index=False)

"""# Create CUSTOMER_DIM table"""

# Tạo bảng CUSTOMER_DIM trong cơ sở dữ liệu retail_dwh
dwcur.execute('''
    CREATE TABLE IF NOT EXISTS CUSTOMER_DIM(
        CUSTOMER_ID CHAR(8),
        NAME VARCHAR(20),
        PROVINCE_CODE NVARCHAR(6),
        MIEN VARCHAR(5)
    )
''')
def insert_customer_dim():
# Lấy dữ liệu từ bảng customer và province trong cơ sở dữ liệu book
  cur.execute('''
    SELECT
        C1.CUSTOMER_ID,
        C1.NAME,
        C2.PROVINCE_CODE,
        C2.MIEN
    FROM CUSTOMER AS C1
    JOIN PROVINCE AS C2
    ON C1.PROVINCE_ID = C2.PROVINCE_ID
    ORDER BY CUSTOMER_ID
''')
  data = cur.fetchall()

# Chèn dữ liệu vào bảng CUSTOMER_DIM trong cơ sở dữ liệu dwh_book
  for row in data:
    dwcur.execute('INSERT INTO CUSTOMER_DIM VALUES (?, ?, ?, ?)', row)
insert_customer_dim()

"""#*CREATE EMPLOYEE_DIM TABLE*"""

# Tạo bảng EMPLOYEE_DIM trong cơ sở dữ liệu dwh_book
dwcur.execute('''
    CREATE TABLE IF NOT EXISTS EMPLOYEE_DIM(
        EMPLOYEE_ID CHAR(8),
        NAME VARCHAR(20),
        COMPANY VARCHAR(50)
    )
''')
def insert_employee_dim():
# Lấy dữ liệu từ bảng EMPLOYEE và COMPANY trong cơ sở dữ liệu book
  cur.execute('''
    SELECT
        C1.EMPLOYEE_ID,
        C1.NAME,
        C2.COMPANY
    FROM EMPLOYEE AS C1
    JOIN COMPANY AS C2
    ON C1.COMPANY_ID = C2.COMPANY_ID
    ORDER BY EMPLOYEE_ID
''')
  data = cur.fetchall()

# Chèn dữ liệu vào bảng EMPLOYEE_DIM trong cơ sở dữ liệu dwh_book
  for row in data:
    dwcur.execute('INSERT INTO EMPLOYEE_DIM VALUES (?, ?, ?)', row)
insert_employee_dim()

"""#*CREATE PRODUCT_DIM TABLE*"""

# Tạo bảng PRODUCT_DIM trong cơ sở dữ liệu dwh_book
dwcur.execute('''
    CREATE TABLE IF NOT EXISTS PRODUCT_DIM(
         PRODUCT_ID    CHAR(9)      PRIMARY KEY     NOT NULL,
         SKU           CHAR(20),
         TYPE          VARCHAR(50),
         NAME          NVARCHAR(100),
         RATING_AVERAGE         FLOAT,
         PRICE        INT
    )
''')
def insert_product_dim():
# Lấy dữ liệu từ bảng PRODUCT trong cơ sở dữ liệu book
  cur.execute('''
    SELECT *
    FROM PRODUCT
    ORDER BY PRODUCT_ID
''')
  data = cur.fetchall()

# Chèn dữ liệu vào bảng PRODUCT_DIM trong cơ sở dữ liệu dwh_book
  for row in data:
    dwcur.execute('INSERT INTO PRODUCT_DIM VALUES (?, ?, ?, ?, ?, ?)', row)
insert_product_dim()

"""#*CREATE ORDER_FACT TABLE*"""

# Tạo bảng ORDER_FACT trong cơ sở dữ liệu dwh_book
dwcur.execute('''
    CREATE TABLE IF NOT EXISTS ORDER_FACT(
         ORDER_NUMBER          CHAR(10)      PRIMARY KEY     NOT NULL,
         CUSTOMER_ID        CHAR(8),
         PRODUCT_ID         CHAR(9),
         EMPLOYEE_ID        CHAR(6),
         DATE               DATETIME,
         QUANTITY           INT,
         SKU                CHAR(20),
         PRODUCT_TYPE       VARCHAR(50),
         PRODUCT_NAME       NVARCHAR(100),
         PRICE              INT,
         DATE_KEY           INT
    )
''')

# Lấy dữ liệu từ các bảng trong cơ sở dữ liệu book
#cur.execute("ATTACH DATABASE dwh_path AS dwh")
cur.execute(f"ATTACH DATABASE '{dwh_path}' AS dwh")

def insert_order_fact():
  cur.execute('''
    SELECT
         O.ORDER_NUMBER,
         C.CUSTOMER_ID,
         P.PRODUCT_ID,
         E.EMPLOYEE_ID,
         O.DATE,
         O.QUANTITY,
         P.SKU,
         P.TYPE,
         P.NAME,
         P.PRICE,
         D.DATE_KEY
    FROM ORDERS O
    JOIN CUSTOMER C
    ON C.CUSTOMER_ID = O.CUSTOMER_ID
    JOIN PRODUCT P
    ON P.PRODUCT_ID = O.PRODUCT_ID
    JOIN EMPLOYEE E
    ON E.EMPLOYEE_ID = O.EMPLOYEE_ID
    JOIN dwh.DIM_DATE D
    ON D.DATE = O.DATE
    ORDER BY O.DATE;
''')
  data = cur.fetchall()

# Chèn dữ liệu vào bảng ORDER_FACT trong cơ sở dữ liệu dwh_book
  for row in data:
    dwcur.execute('INSERT INTO ORDER_FACT VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', row)
insert_order_fact()

retail_dwh.commit()

# Chạy thử
for row in cur.execute("SELECT * FROM ORDER_FACT ORDER BY DATE LIMIT 5"):
    print(row)