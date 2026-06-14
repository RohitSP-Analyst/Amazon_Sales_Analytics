
import sys
import glob
import pandas as pd


def load_data(path=None):
    if path is None:
        files = sorted(glob.glob("output/amazon_products_*.csv"))
        if not files:
            raise FileNotFoundError("No scraped CSV found in output/. Run the spider first.")
        path = files[-1]
        print(f"Loading most recent file: {path}")

    df = pd.read_csv(path)
    return df


def clean(df):
    
    df = df.dropna(subset=["title", "price"])

    
    numeric_cols = ["price", "original_price", "discount_percent", "rating",
                     "review_count", "bought_last_month"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce")

    return df


def summarize(df):
    print("\n=== Dataset Overview ===")
    print(f"Total products: {len(df)}")
    print(f"Categories: {df['category'].unique().tolist()}")

    print("\n=== Price Stats by Category ===")
    print(df.groupby("category")["price"].agg(["mean", "median", "min", "max", "count"]).round(2))

    print("\n=== Average Rating & Review Count by Category ===")
    print(df.groupby("category")[["rating", "review_count"]].mean().round(2))

    print("\n=== Top 5 Highest-Discount Products ===")
    top_discount = df.sort_values("discount_percent", ascending=False).head(5)
    print(top_discount[["title", "category", "price", "original_price", "discount_percent"]])

    print("\n=== Top 5 Most-Reviewed Products (popularity proxy) ===")
    top_reviewed = df.sort_values("review_count", ascending=False).head(5)
    print(top_reviewed[["title", "category", "price", "rating", "review_count"]])

    print("\n=== Prime vs Non-Prime: Avg Price & Rating ===")
    print(df.groupby("is_prime")[["price", "rating"]].mean().round(2))

    
    print("\n=== Potential Issues / Research Angles ===")
    low_rating_high_price = df[(df["rating"] < 3.5) & (df["price"] > df["price"].median())]
    print(f"- {len(low_rating_high_price)} products are above-median price but rated < 3.5 "
          f"(potential overpricing / customer dissatisfaction issue)")

    high_discount_low_review = df[(df["discount_percent"] > 30) & (df["review_count"] < 50)]
    print(f"- {len(high_discount_low_review)} products have >30% discount but <50 reviews "
          f"(possible new/underperforming listings being pushed via discounting)")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    df = load_data(path)
    df = clean(df)
    summarize(df)

    
    out_path = "output/amazon_products_cleaned.csv"
    df.to_csv(out_path, index=False)
    print(f"\nCleaned dataset saved to: {out_path}")
