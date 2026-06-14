import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv("output/sales_transactions.csv")

engine = create_engine("mysql+pymysql://root:Rohit%403260@localhost/amazon_analytics")
df.to_sql("sales", engine, if_exists="replace", index=False)
pd.read_csv("output/dim_products.csv").to_sql("dim_products", engine, if_exists="replace", index=False)
pd.read_csv("output/dim_customers.csv").to_sql("dim_customers", engine, if_exists="replace", index=False)
print("Done! Rows inserted:", len(df))