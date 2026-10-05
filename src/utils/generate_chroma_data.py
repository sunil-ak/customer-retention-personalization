import sqlite3
import random
import chromadb
import os

import sys

try:
    # Works if running as a saved script
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback if running in a notebook, REPL, or executable freeze
    PROJECT_ROOT = os.getcwd() 

# 1. Setup Storage Paths

db_path = os.path.join(PROJECT_ROOT, "storage", "capstone.db")
chroma_path = os.path.join(PROJECT_ROOT, "storage", "chroma_db")

if not os.path.exists(db_path):
    raise FileNotFoundError(f"Missing SQLite file at {db_path}. Run your SQL script first.")

sql_conn = sqlite3.connect(db_path)
cursor = sql_conn.cursor()

# Initialize ChromaDB persistent storage client
chroma_client = chromadb.PersistentClient(path=chroma_path)
tickets_collection = chroma_client.get_or_create_collection(name="support_tickets")
reviews_collection = chroma_client.get_or_create_collection(name="customer_reviews")

# Clear collections to ensure clean data counts on re-runs
try:
    tickets_collection.delete(where={"status": "Unresponsive"})
    tickets_collection.delete(where={"status": "Resolved"})
    reviews_collection.delete(where={"sentiment": "Negative"})
    reviews_collection.delete(where={"sentiment": "Positive"})
except Exception:
    pass

# Extract all verified customer purchases from SQLite
cursor.execute("""
    SELECT DISTINCT e.customer_id, e.sku, s.product_name
    FROM events e
    JOIN skus s ON e.sku = s.sku
    WHERE e.action = 'Checkout Success';
""")
all_purchases = cursor.fetchall()  # List of tuples: (customer_id, sku, product_name)

# =====================================================================
# TEXT TEMPLATE LIBRARIES
# =====================================================================
ticket_templates = [
    {"type": "Defective", "text": "My order arrived broken. The {prod} looks defective. I opened a ticket but haven't received a response in {days} days."},
    {"type": "Damaged", "text": "The packaging for {prod} was ripped and the item inside is damaged. Need an exchange immediately."},
    {"type": "Delayed Delivery", "text": "Where is my order? The tracking for {prod} shows it has been stuck in transit for {days} days."}
]

negative_review_templates = [
    "Terrible experience. The {prod} is completely defective and falling apart. Support has ignored me for {days} days.",
    "Very disappointed with the quality of {prod}. Arrived damaged and nobody is replying to my help requests.",
    "Extremely frustrated. Shipping was delayed significantly for my {prod}. Customer service won't answer."
]

positive_review_templates = [
    "Absolutely loving my new {prod}! Incredible build quality and lightning-fast shipping.",
    "Highly recommend this item. The {prod} exceeded my expectations. Fantastic value.",
    "Great purchase! Works perfectly out of the box and matches the description."
]

# State trackers to isolate customer-SKU combinations across our loops
ticketed_pairs = set()      # Stores unique tuple pairs: (customer_id, sku)
negative_review_pairs = set() # Stores unique tuple pairs: (customer_id, sku)

# =====================================================================
# LOOP 1: GENERATE 350 SUPPORT TICKETS
# =====================================================================
print("🎫 Loop 1: Generating 350 Support Tickets...")
t_docs, t_metadatas, t_ids = [], [], []
uniq_tkt_combo = set()
for t in range(1, 351):
    ticket_id = f"TKT-{t:05d}"
    cust_id, sku, prod_name = random.choice(all_purchases)
    if cust_id+sku in uniq_tkt_combo:
      continue
    uniq_tkt_combo.add(cust_id+sku)
    days_open = random.randint(3, 7)
    status = random.choices(["Unresponsive", "Resolved"], weights=[0.25, 0.75])[0]
    chosen_tmpl = random.choice(ticket_templates)

    # Track this combination to prevent it from sliding into positive reviews later
    ticketed_pairs.add((cust_id, sku))

    t_docs.append(chosen_tmpl["text"].format(prod=prod_name, days=days_open))
    t_ids.append(ticket_id)
    t_metadatas.append({
        "customer_id": cust_id,
        "ticket_id": ticket_id,
        "sku": sku,
        "days_open": days_open,
        "status": status,
        "issue_category": chosen_tmpl["type"]
    })

tickets_collection.add(documents=t_docs, metadatas=t_metadatas, ids=t_ids)


# =====================================================================
# LOOP 2: GENERATE 120 NEGATIVE REVIEWS
# =====================================================================
print("📉 Loop 2: Generating 120 Negative Product Reviews...")
neg_docs, neg_metadatas, neg_ids = [], [], []

uniq_rev_combo = set()

for n in range(1, 121):
    review_id = f"REV-NEG-{n:05d}"
    cust_id, sku, prod_name = random.choice(all_purchases)
    if cust_id+sku in uniq_rev_combo:
      continue
    uniq_rev_combo.add(cust_id+sku)
    days_open = random.randint(3, 6)

    # Track this combination so Loop 3 can actively avoid it
    negative_review_pairs.add((cust_id, sku))

    neg_docs.append(random.choice(negative_review_templates).format(prod=prod_name, days=days_open))
    neg_ids.append(review_id)
    neg_metadatas.append({
        "customer_id": cust_id,
        "review_id": review_id,
        "sku": sku,
        "rating": random.randint(1, 2),
        "sentiment": "Negative"
    })

reviews_collection.add(documents=neg_docs, metadatas=neg_metadatas, ids=neg_ids)


# =====================================================================
# LOOP 3: GENERATE 480 POSITIVE REVIEWS (With Explicit Exclusion Check)
# =====================================================================
print("🌟 Loop 3: Generating 480 Conflict-Free Positive Reviews...")
pos_docs, pos_metadatas, pos_ids = [], [], []

for p in range(1, 481):
    review_id = f"REV-POS-{p:05d}"

    # Filter our purchase list to find a clean option for this specific loop execution
    clean_options = [
        row for row in all_purchases
        if (row[0], row[1]) not in ticketed_pairs
        and (row[0], row[1]) not in negative_review_pairs
    ]

    # Defensive Fallback: If no pure options exist globally, relax constraints to keep script safe
    if clean_options:
        cust_id, sku, prod_name = random.choice(clean_options)
    else:
        cust_id, sku, prod_name = random.choice(all_purchases)

    pos_docs.append(random.choice(positive_review_templates).format(prod=prod_name))
    pos_ids.append(review_id)
    pos_metadatas.append({
        "customer_id": cust_id,
        "review_id": review_id,
        "sku": sku,
        "rating": random.randint(4, 5),
        "sentiment": "Positive"
    })

reviews_collection.add(documents=pos_docs, metadatas=pos_metadatas, ids=pos_ids)

sql_conn.close()

#drive.flush_and_unmount()
print(f"\n🎉 Success! Stored {tickets_collection.count()} tickets and {reviews_collection.count()} total reviews smoothly.")
