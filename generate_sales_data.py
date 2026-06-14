import sys
import glob
import random
import datetime
import pandas as pd
import numpy as np

# ---- CONFIG ----
NUM_ORDERS = 5000          # number of order line-items to generate
START_DATE = datetime.date(2023, 1, 1)
END_DATE = datetime.date(2025, 12, 31)

REGIONS = {
    "East": ["New York", "Boston", "Philadelphia"],
    "West": ["Los Angeles", "San Francisco", "Seattle"],
    "Central": ["Chicago", "Dallas", "Austin"],
    "South": ["Miami", "Atlanta", "Houston"],
}

SEGMENTS = ["Consumer", "Corporate", "Home Office"]

FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer",
               "Michael", "Linda", "David", "Elizabeth", "Sara", "Aman",
               "Priya", "Rahul", "Neha", "Karan", "Riya", "Vikram"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
              "Miller", "Davis", "Sharma", "Patel", "Khan", "Gupta",
              "Singh", "Verma"]

# Map scraped "category" keywords -> business Category / Sub-Category
CATEGORY_MAP = {
    "laptop": ("Technology", "Computers"),
    "smartphone": ("Technology", "Phones"),
    "headphones": ("Technology", "Audio"),
    "wireless earbuds": ("Technology", "Audio"),
    "smart watch": ("Technology", "Wearables"),
    "tablet": ("Technology", "Computers"),
    "office chair": ("Furniture", "Chairs"),
    "desk": ("Furniture", "Tables"),
    "monitor": ("Technology", "Computer Accessories"),
    "keyboard": ("Technology", "Computer Accessories"),
    "printer": ("Technology", "Office Machines"),
    "kitchen appliance": ("Home & Kitchen", "Appliances"),
    "vacuum cleaner": ("Home & Kitchen", "Appliances"),
    "air fryer": ("Home & Kitchen", "Appliances"),
    "coffee maker": ("Home & Kitchen", "Appliances"),
    "running shoes": ("Apparel", "Footwear"),
    "backpack": ("Apparel", "Bags"),
    "fitness tracker": ("Technology", "Wearables"),
    "gaming console": ("Technology", "Gaming"),
    "camera": ("Technology", "Cameras"),
    "bluetooth speaker": ("Technology", "Audio"),
}


def load_products(path=None):
    if path is None:
        files = sorted(glob.glob("output/amazon_selenium_*.csv")) + \
                sorted(glob.glob("output/amazon_products_*.csv"))
        if not files:
            raise FileNotFoundError("No scraped product CSV found in output/.")
        path = files[-1]
        print(f"Using product catalog: {path}")

    df = pd.read_csv(path)
    df = df.dropna(subset=["title", "price"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    df = df[df["price"] > 0]
    return df.reset_index(drop=True)


def random_date(start, end):
    delta = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    products = load_products(path)

    # Build a product catalog with business category mapping
    catalog = []
    for idx, row in products.iterrows():
        kw = str(row["category"]).strip().lower()
        cat, subcat = CATEGORY_MAP.get(kw, ("General", "Misc"))
        catalog.append({
            "Product ID": f"PROD-{idx+1:04d}",
            "Product Name": row["title"][:80],
            "Category": cat,
            "Sub Category": subcat,
            "Unit Price": round(float(row["price"]), 2),
        })
    catalog_df = pd.DataFrame(catalog)
    print(f"Catalog built with {len(catalog_df)} products across "
          f"{catalog_df['Category'].nunique()} categories and "
          f"{catalog_df['Sub Category'].nunique()} sub-categories.")

    # Generate customers
    num_customers = 400
    customers = []
    for i in range(num_customers):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        region = random.choice(list(REGIONS.keys()))
        state_city = random.choice(REGIONS[region])
        customers.append({
            "Customer ID": f"CUST-{i+1:04d}",
            "Customer Name": name,
            "Segment": random.choice(SEGMENTS),
            "Region": region,
            "City": state_city,
            "State": region,  # simplified; could map to real states
            "Country": "United States",
        })
    customers_df = pd.DataFrame(customers)

    # Generate orders
    orders = []
    for i in range(NUM_ORDERS):
        product = catalog_df.sample(1).iloc[0]
        customer = customers_df.sample(1).iloc[0]

        order_date = random_date(START_DATE, END_DATE)
        ship_date = order_date + datetime.timedelta(days=random.randint(1, 7))

        quantity = random.randint(1, 6)
        # Discounts: simulate occasional promotions
        discount = random.choice([0, 0, 0, 0.05, 0.1, 0.15, 0.2, 0.3])

        unit_price = product["Unit Price"]
        gross_sales = unit_price * quantity
        sales = round(gross_sales * (1 - discount), 2)

        # Profit margin varies by category (simulate realistic margins)
        margin_lookup = {
            "Technology": 0.18,
            "Furniture": 0.12,
            "Home & Kitchen": 0.22,
            "Apparel": 0.30,
            "General": 0.15,
        }
        base_margin = margin_lookup.get(product["Category"], 0.15)
        
        margin = base_margin + np.random.normal(0, 0.08)
        profit = round(sales * margin, 2)

        orders.append({
            "Order ID": f"ORD-{i+1:06d}",
            "Order Date": order_date.isoformat(),
            "Ship Date": ship_date.isoformat(),
            "Customer ID": customer["Customer ID"],
            "Customer Name": customer["Customer Name"],
            "Segment": customer["Segment"],
            "Product ID": product["Product ID"],
            "Product Name": product["Product Name"],
            "Category": product["Category"],
            "Sub Category": product["Sub Category"],
            "Sales": sales,
            "Quantity": quantity,
            "Discount": discount,
            "Profit": profit,
            "Country": customer["Country"],
            "State": customer["State"],
            "City": customer["City"],
            "Region": customer["Region"],
        })

    orders_df = pd.DataFrame(orders)

    out_path = "output/sales_transactions.csv"
    orders_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(orders_df)} order records to {out_path}")

   
    catalog_df.to_csv("output/dim_products.csv", index=False, encoding="utf-8-sig")
    customers_df.to_csv("output/dim_customers.csv", index=False, encoding="utf-8-sig")
    print("Also saved output/dim_products.csv and output/dim_customers.csv")


if __name__ == "__main__":
    main()
