import argparse
import sys
from core.client import OdooClient
from core.importer import ExcelImporter

def main():
    parser = argparse.ArgumentParser(description="Modular Odoo DB Hydrator (Using Native Load API)")
    parser.add_argument("--url", default="http://localhost:8069", help="Odoo Server URL")
    parser.add_argument("--db", default="ai_pf_db_clean", help="Target Database Name")
    parser.add_argument("--user", default="admin", help="Odoo Username")
    parser.add_argument("--password", default="admin", help="Odoo Password")
    parser.add_argument("--model", required=True, help="Target Odoo Model (e.g., purchase.order)")
    parser.add_argument("--file", required=True, help="Path to the Excel file")
    
    args = parser.parse_args()
    
    # 1. Initialize Client and Authenticate
    client = OdooClient(url=args.url, db=args.db, username=args.user, password=args.password)
    if not client.authenticate():
        sys.exit(1)
        
    # 2. Parse Excel File
    importer = ExcelImporter(file_path=args.file)
    fields, data_rows = importer.parse_for_load()
    
    if not fields or not data_rows:
        print("❌ Import aborted: Excel file is empty or unreadable.")
        sys.exit(1)
        
    # 3. Push to Odoo via native `load()`
    client.load_data(model_name=args.model, fields=fields, data_rows=data_rows)

if __name__ == '__main__':
    main()
