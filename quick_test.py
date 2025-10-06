#!/usr/bin/env python3
"""
Quick test to verify the SQLite Row fix works
"""

def test_database_access():
    """Test database access with sqlite3.Row objects"""
    from db import db_manager
    
    print("Testing database access...")
    
    try:
        db_manager.connect()
        
        # Test the query that was causing issues
        summary_query = '''
            SELECT 
                COUNT(*) as total_items,
                SUM(CASE WHEN quantity <= reorder_level THEN 1 ELSE 0 END) as low_stock_items,
                COUNT(DISTINCT category) as total_categories,
                COUNT(DISTINCT supplier) as total_suppliers
            FROM items
        '''
        result = db_manager.execute_query(summary_query)
        
        if result:
            summary = result[0]
            print(f"✅ Query executed successfully")
            print(f"   Total items: {summary[0]}")
            print(f"   Low stock items: {summary[1]}")
            print(f"   Total categories: {summary[2]}")
            print(f"   Total suppliers: {summary[3]}")
            
            # Test accessing by column name (should work with sqlite3.Row)
            print(f"   By name - Total items: {summary['total_items']}")
            
        else:
            print("❌ No results returned")
        
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database_access()