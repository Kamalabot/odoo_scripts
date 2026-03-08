import xmlrpc.client
import sys

class OdooClient:
    """Wrapper for Odoo XML-RPC API, optimized for the `load` method."""
    
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        self.uid = None
        
    def authenticate(self):
        """Authenticates with the Odoo server."""
        print(f"🔗 Connecting to Odoo at {self.url} (DB: {self.db})...")
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                print(f"✅ Authenticated successfully! User ID: {self.uid}")
                return True
            else:
                print("❌ Authentication failed. Check your DB name, username, and password.")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def load_data(self, model_name, fields, data_rows):
        """
        Uses Odoo's native `load` method.
        This is exactly what the web UI uses when importing CSV/Excel.
        It natively handles External IDs (id), Relational Many2One (parent_id/id),
        and One2Many (order_line/product_id).
        
        :param model_name: Odoo technical model name (e.g., 'purchase.order')
        :param fields: List of exact column headers (e.g., ['id', 'partner_id/id', 'order_line/product_id/id'])
        :param data_rows: List of lists, where each inner list is a row of values matching the `fields` order.
        """
        if not self.uid:
            print("❌ Cannot load data. Not authenticated.")
            return None
            
        print(f"🚀 Sending {len(data_rows)} rows to `{model_name}` using Odoo `load()`...")
        try:
            # The 'load' method signature:
            # execute_kw(db, uid, password, model, 'load', [fields, data_rows])
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model_name, 'load',
                [fields, data_rows]
            )
            
            # The result is a dict with 'ids' (success) and 'messages' (errors)
            if result.get('messages'):
                print("⚠️  Import completed with warnings/errors:")
                for msg in result.get('messages', []):
                    print(f"   [!] Row {msg.get('record', 'Unknown')}: {msg.get('message')}")
                    
            if result.get('ids'):
                print(f"✅ Successfully loaded {len(result['ids'])} records!")
                return result['ids']
            else:
                print("❌ No records were created.")
                return []
                
        except Exception as e:
            print(f"❌ Fatal error during load: {e}")
            return None
