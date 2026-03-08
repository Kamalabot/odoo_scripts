import pandas as pd
import math
import sys

class ExcelImporter:
    """Handles Excel file reading and parsing for Odoo."""
    
    def __init__(self, file_path):
        self.file_path = file_path
        
    def _clean_value(self, val):
        """
        Sanitizes weird pandas NaN/NaT values into empty strings or standard Python types
        that Odoo's `load` method expects. In `load`, empty string '' means "no value".
        """
        if pd.isna(val):
            return ""
        if isinstance(val, float) and math.isnan(val):
            return ""
        # Convert everything else to string, as Odoo's load method is built to parse 
        # string inputs (just like a CSV file). Odoo handles the type casting internally.
        if isinstance(val, (int, float)):
             # Ensure floats like 1.0 that are meant to be ids or qtys are handled cleanly
             if val == int(val):
                 return str(int(val))
        return str(val).strip()

    def parse_for_load(self):
        """
        Reads the Excel file and transforms it into the `fields` and `data_rows` lists
        required by Odoo's `load()` method.
        """
        print(f"📂 Parsing Excel file: {self.file_path}")
        try:
            # Read all columns as strings to prevent Pandas from mangling IDs
            df = pd.read_excel(self.file_path, dtype=str)
            
            # Drop rows that are entirely empty
            df = df.dropna(how='all')
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            sys.exit(1)
            
        # Extract headers (fields)
        fields = df.columns.tolist()
        
        # Extract data rows
        data_rows = []
        for index, row in df.iterrows():
            cleaned_row = [self._clean_value(row[col]) for col in fields]
            data_rows.append(cleaned_row)
            
        print(f"📋 Found {len(fields)} columns and {len(data_rows)} target rows.")
        return fields, data_rows
