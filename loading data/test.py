dataframes = ['product_df', 'customer_df', 'employee_df', 'company_df', 'province_df', 'order_df',]
tables_to_create = [
    "PRODUCT",
    "CUSTOMER",
    "EMPLOYEE",
    "COMPANY",
    "PROVINCE",
    "ORDERS"
]
for df, table_name in zip(dataframes, tables_to_create):
    print(df, table_name)
for table_name, df in zip(tables_to_create, dataframes):
    print(table_name, df)