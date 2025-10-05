"""
Test script to verify Supabase connection with SSL certificate
"""
import sys
sys.path.insert(0, '/Users/aravindh.s03/Desktop/ARAVINDH/Personal/Agam Organics/backend')

# This import will trigger ssl_setup
from app.db.database import get_db

try:
    db = get_db()
    print("✅ Supabase client created successfully")
    
    # Test a simple query
    result = db.table("products").select("*").limit(1).execute()
    print(f"✅ Database query successful!")
    print(f"   Data: {result.data}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
