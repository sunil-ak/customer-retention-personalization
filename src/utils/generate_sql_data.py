import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import os # Import the os module for file operations

# Initialize Faker and random seeds for deterministic, repeatable generation
fake = Faker()
Faker.seed(42)
random.seed(42)

sql_conn = None # Initialize to None

try:
    # --- Start: Fix for 'database is locked' error ---
    db_file = "/content/drive/MyDrive/capstone_project/capstone.db"
    db_journal_file = "/content/drive/MyDrive/capstone_project/capstone.db-journal"

    # Remove existing database files to ensure a clean start and prevent locking issues
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed existing database file: {db_file}")
    if os.path.exists(db_journal_file):
        os.remove(db_journal_file)
        print(f"Removed existing database journal file: {db_journal_file}")
    # --- End: Fix for 'database is locked' error ---

    # Connect to SQLite (creates or opens 'capstone.db')
    sql_conn = sqlite3.connect(db_file)
    cursor = sql_conn.cursor()

    # Enforce database relational constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("🚀 Starting initialization and table setup...")

    # =====================================================================
    # PHASE 0: DATABASE SCHEMA CREATION
    # =====================================================================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skus (
        sku TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        base_price REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        customer_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        buyer_tier TEXT CHECK(buyer_tier IN ('VIP', 'Regular')) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        action TEXT NOT NULL,
        sku TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES profiles(customer_id),
        FOREIGN KEY(sku) REFERENCES skus(sku)
    );
    """)
    sql_conn.commit()

    # Clear out old test runs to ensure clean data counts
    cursor.execute("DELETE FROM events;")
    cursor.execute("DELETE FROM profiles;")
    cursor.execute("DELETE FROM skus;")
    sql_conn.commit()


    # =====================================================================
    # PHASE 1: GENERATE EXACTLY 35 RANDOMIZED SKUs (Single Loop Pass)
    # =====================================================================
    print("📦 Generating 35 optimized SKUs...")
    categories = ["Running Gear", "Apparel", "Accessories", "Recovery"]
    sku_list = []
    sku_counter = 101

    while len(sku_list) < 35:
        sku = f"SKU-{sku_counter}"
        cat = random.choice(categories)
        prod_name = f"Generic {cat} Item {sku_counter}"
        base_price = round(random.uniform(15.00, 250.00), 2)

        cursor.execute(
            "INSERT INTO skus (sku, product_name, category, base_price) VALUES (?, ?, ?, ?)",
            (sku, prod_name, cat, base_price)
        )
        sku_list.append(sku)
        sku_counter += 1

    sql_conn.commit()
    print(f"   ↳ ✅ Successfully inserted {len(sku_list)} rows into 'skus' table.")


    # =====================================================================
    # PHASE 2: GENERATE 500 CUSTOMER PROFILES
    # =====================================================================
    print("👤 Generating 500 unique customer profiles...")
    customer_ids = []

    # Keep track of generated emails to ensure uniqueness
    generated_emails = set()

    for i in range(1, 501):
        cust_id = f"CUST-{i:03d}"  # Creates sequential strings like CUST-001, CUST-042
        name = fake.name()
        email = f"{name.lower().replace(' ', '.')}@example.net"

        # Ensure email is unique, regenerate if needed
        while email in generated_emails:
            name = fake.name()
            email = f"{name.lower().replace(' ', '.')}@example.net"
        generated_emails.add(email)

        buyer_tier = random.choices(["VIP", "Regular"], weights=[0.25, 0.75])[0]  # 25% VIP ratio

        cursor.execute(
            "INSERT INTO profiles (customer_id, name, email, buyer_tier) VALUES (?, ?, ?, ?)",
            (cust_id, name, email, buyer_tier)
        )
        customer_ids.append(cust_id)

    sql_conn.commit()
    print(f"   ↳ ✅ Successfully inserted {len(customer_ids)} rows into 'profiles' table.")


    # =====================================================================
    # PHASE 3: GENERATE 1,500 CHRONOLOGICAL CONVERSION FUNNEL EVENTS
    # =====================================================================
    print("⏳ Simulating 1,500 ordered chronological timeline events...")
    TOTAL_TARGET_EVENTS = 1500
    current_event_count = 0
    base_start_date = datetime(2026, 8, 1, 9, 0, 0) # Start data timeline: August 1st, 2026

    while current_event_count < TOTAL_TARGET_EVENTS:
        # Pick a random customer and item for this simulated browsing session
        customer_id = random.choice(customer_ids)
        sku = random.choice(sku_list)

        # Establish a random starting date in August for this user session
        session_start_time = base_start_date + timedelta(
            days=random.randint(0, 25),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # Choose how far down the purchase funnel the session progresses
        # (60% browse only, 25% abandon cart, 15% complete checkout)
        funnel_depth = random.choices(["view_only", "abandon_cart", "purchase"], weights=[0.60, 0.25, 0.15])[0]

        session_events = []

        # Event Step 1: Always starts with a page view
        session_events.append(("Web Page View", session_start_time))

        # Event Step 2: Add to Cart (Happens 2 to 7 minutes after viewing)
        if funnel_depth in ["abandon_cart", "purchase"]:
            cart_time = session_start_time + timedelta(minutes=random.randint(2, 7))
            session_events.append(("Add to Cart", cart_time))

            # Event Step 3: Checkout Success (Happens 5 to 12 minutes after adding to cart)
            if funnel_depth == "purchase":
                checkout_time = cart_time + timedelta(minutes=random.randint(5, 12))
                session_events.append(("Checkout Success", checkout_time))

        # Write the sequential session steps directly into the table
        for action, timestamp in session_events:
            if current_event_count >= TOTAL_TARGET_EVENTS:
                break  # Break clean right at 1,500 rows

            current_event_count += 1
            event_id = f"EVT-{current_event_count:04d}"
            iso_timestamp = timestamp.isoformat() + "Z"

            cursor.execute(
                "INSERT INTO events (event_id, customer_id, timestamp, action, sku) VALUES (?, ?, ?, ?, ?)",
                (event_id, customer_id, iso_timestamp, action, sku)
            )

    sql_conn.commit()
    print(f"   ↳ ✅ Enforced funnel logic. Inserted exactly {current_event_count} ordered rows into 'events' table.")


    # =====================================================================
    # DATA VALIDATION SANITY CHECK
    # =====================================================================
    print("\n📊 RUNNING STRATIFIED ARCHITECTURE INSPECTION:")

    # 1. Total Rows Check
    cursor.execute("SELECT COUNT(*) FROM skus")
    print(f"🔹 Total SKUs Row Count     : {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM profiles")
    print(f"🔹 Total Profiles Row Count : {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM events")
    print(f"🔹 Total Events Row Count   : {cursor.fetchone()[0]}")

    # 2. Funnel Alignment Verification Query
    cursor.execute("""
        SELECT customer_id, sku, action, timestamp
        FROM events
        WHERE customer_id = (SELECT customer_id FROM events WHERE action = 'Checkout Success' LIMIT 1)
          AND sku = (SELECT sku FROM events WHERE action = 'Checkout Success' LIMIT 1)
        ORDER BY timestamp ASC;
    """)

    print("\n🔍 Verification: Sequential Timeline Validation for a Single Converted User Session:")
    for row in cursor.fetchall():
        print(f"   • Cust ID: {row[0]} | SKU: {row[1]} | Action: {row[2]:<20} | Time: {row[3]}")

    print("\n🎉 Master structured data initialization complete!")

finally:
    if sql_conn:
        sql_conn.close()
