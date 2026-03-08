import xmlrpc.client

url = "http://localhost:8069"
db = "ai_pf_db_clean"
username = "admin"
password = "admin"
uid = 2

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Search for product.product external IDs
ext_ids = models.execute_kw(db, uid, password, 'ir.model.data', 'search_read',
    [[('model', '=', 'product.product')]],  # domain
    {'fields': ['name', 'module', 'res_id']} # fields
)

print("Product Variants External IDs:")
for record in ext_ids:
    if 'widget' in record['name'] or '__import__' in record['module']:
        print(f"ID: {record['module']}.{record['name']} -> product.product({record['res_id']})")
