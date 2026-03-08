import xmlrpc.client
import sys

URL = 'http://localhost:8069'
DB = 'ai_pf_db_clean'
USER = 'admin'
PASS = 'admin'

def check_mapping():
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER, PASS, {})
    if not uid:
        print("Failed to authenticate.")
        return

    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    # Let's search for the external IDs of the products we just imported
    print("Searching ir.model.data for 'prod_widget_a'...")
    records = models.execute_kw(DB, uid, PASS, 'ir.model.data', 'search_read',
        [[['name', 'ilike', 'prod_widget_a']]],
        {'fields': ['module', 'name', 'model', 'res_id']}
    )
    
    for r in records:
        print(r)

if __name__ == '__main__':
    check_mapping()
