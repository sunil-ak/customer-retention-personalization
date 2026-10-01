import sqlite3
import chromadb
from datetime import datetime, timedelta

class CustomerDataOrchestrator:
    def __init__(self, sql_db_path: str, chroma_persist_path: str):
        """
        Initializes the data paths and establishes connection clients for the 
        Polyglot Persistence Layer.
        """
        self.sql_db_path = sql_db_path
        self.chroma_path = chroma_persist_path
        
        # Initialize the persistent ChromaDB client once
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        
        # Pre-load collections to avoid repeatedly calling get_collection
        self.tickets_coll = self.chroma_client.get_collection("support_tickets")
        self.reviews_coll = self.chroma_client.get_collection("customer_reviews")
        print("🔗 Polyglot Orchestrator connected cleanly to SQL and Chroma engines.")

    def get_clean_customer_story(self, customer_id: str) -> dict:
        """
        Executes an explicit, ID-linked structured RAG extraction across SQL and 
        Vector engines. Enforces clean data constraints of 1 ticket/review per SKU.
        """
        # 1. CONNECT TO SQLITE (Structured Data Pass)
        conn = sqlite3.connect(self.sql_db_path)
        cursor = conn.cursor()
        
        # Fetch Profile Attributes
        cursor.execute("SELECT name, email, buyer_tier FROM profiles WHERE customer_id = ?;", (customer_id,))
        profile_row = cursor.fetchone()
        if not profile_row:
            conn.close()
            return None
            
        profile_dict = {
            "customer_id": customer_id,
            "name": profile_row[0],
            "email": profile_row[1],
            "buyer_tier": profile_row[2]
        }
        
        # Fetch Chronological Event Timeline
        cursor.execute("""
            SELECT e.timestamp, e.action, e.sku, s.product_name, s.category, s.base_price
            FROM events e
            JOIN skus s ON e.sku = s.sku
            WHERE e.customer_id = ?
            ORDER BY e.timestamp ASC;
        """, (customer_id,))
        
        events_list = []
        checkout_skus = set()
        for row in cursor.fetchall():
            events_list.append({
                "timestamp": row[0],
                "action": row[1],
                "sku": row[2],
                "product_name": row[3],
                "product_category": row[4],
                "price": row[5]
            })
            if row[1] == "Checkout Success":
                checkout_skus.add(row[2])
                
        conn.close()
        
        # 2. QUERY CHROMADB (Unstructured Data Pass with Unique Constraints)
        # Fetch and process support tickets
        ticket_results = self.tickets_coll.get(where={"customer_id": customer_id})
        seen_ticket_skus = set()
        clean_tickets = []
        
        if ticket_results and ticket_results['documents']:
            for doc, meta, t_id in zip(ticket_results['documents'], ticket_results['metadatas'], ticket_results['ids']):
                target_sku = meta.get('sku')
                
                # Enforce: Only look at purchased items + restrict to ONE ticket per product
                if target_sku in checkout_skus and target_sku not in seen_ticket_skus:
                    seen_ticket_skus.add(target_sku)
                    
                    days_open = meta.get('days_open', 5)
                    open_date = (datetime(2026, 9, 2) - timedelta(days=days_open)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    
                    clean_tickets.append({
                        "ticket_id": t_id,
                        "sku": target_sku,
                        "log_text": doc,
                        "ticket_opened_date": open_date,
                        "days_open": days_open,
                        "status": "Unresolved" if days_open > 2 else "Resolved",
                        "issue_category": meta.get('issue_category', 'General')
                    })
                    
        # Fetch and process customer reviews
        review_results = self.reviews_coll.get(where={"customer_id": customer_id})
        seen_review_skus = set()
        clean_reviews = []
        
        if review_results and review_results['documents']:
            for doc, meta, r_id in zip(review_results['documents'], review_results['metadatas'], review_results['ids']):
                target_sku = meta.get('sku')
                
                # Enforce: Restrict to ONE unique review comment per product
                if target_sku in checkout_skus and target_sku not in seen_review_skus:
                    seen_review_skus.add(target_sku)
                    
                    clean_reviews.append({
                        "review_id": r_id,
                        "sku": target_sku,
                        "log_text": doc,
                        "rating": meta.get('rating', 3),
                        "sentiment_tier": meta.get('sentiment', 'Neutral')
                    })

        # Return the aggregated payload object
        return {
            "profile": profile_dict,
           # "clickstream_events": events_list,
            "support_tickets": clean_tickets,
            "customer_reviews": clean_reviews
        }
