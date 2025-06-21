import sqlite3
import pandas as pd

# Load your CSV
df = pd.read_csv("Inventory_English.csv")

# Standardize column names to match the RAG app
df.columns = ["Brand", "Product", "Package_Size", "Price_per_Pack", "In_Stock", "Shelf"]

# Connect to SQLite
conn = sqlite3.connect("inventory.db")

# Save the CSV data as a table in SQLite
df.to_sql("products", conn, if_exists="replace", index=False)

print("✅ Inventory loaded into SQLite database (inventory.db)")
conn.close()
