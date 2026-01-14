
import sqlite3
import json
import os
import sys

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.deepseek_client import DeepSeekClient

def get_schema_info(db_path):
    """Read database schema including table names and column names."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema = {}
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        # Skip system tables
        if table_name.startswith('sqlite_') or table_name in ['financial_metrics', 'business_glossary']:
            continue
            
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        col_list = []
        for col in columns:
            col_list.append(col[1]) # name
            
        schema[table_name] = col_list
        
    conn.close()
    return schema

def generate_mappings(schema_info):
    """Use LLM to generate synonyms for tables and specific fields."""
    client = DeepSeekClient()
    
    # We focus on key tables for financial queries
    target_tables = ['invoices', 'account_balances', 'income_statements', 'balance_sheets', 
                     'cash_flow_statements', 'tax_reports', 'hr_salary_data', 'tax_returns_income']
    
    prompt_content = f"""
    Analyze the following SQLite database schema and generate a JSON mapping of synonyms (aliases) for key tables, columns, and column values.
    
    Schema:
    {json.dumps({k:v for k,v in schema_info.items() if k in target_tables}, indent=2)}
    
    Task:
    1. For each TABLE, provide a list of Chinese synonyms (e.g., 'invoices' -> ['发票', '开票']).
    2. For key COLUMNS (especially those determining types/categories), provide synonyms.
    3. Crucially, strictly define VALUE mappings for specific discriminator columns:
       - For `invoices.invoice_type`, map 'INPUT' to ['进项', '采购', '进货', '购买', '购入']
       - For `invoices.invoice_type`, map 'OUTPUT' to ['销项', '销售', '出货', '卖出', '开给客户']
       - For `account_balances.direction`, map 'debit' to ['借方', '借项']
       - For `account_balances.direction`, map 'credit' to ['贷方', '贷项']
    
    Format properly as JSON:
    {{
        "tables": {{
            "table_name": ["alias1", "alias2"]
        }},
        "value_mappings": {{
            "table.column.VALUE": ["alias1", "alias2"]
        }}
    }}
    
    Only return valid JSON. Do not return code blocks.
    """
    
    messages = [
        {"role": "system", "content": "You are a database expert. Output strictly valid JSON."},
        {"role": "user", "content": prompt_content}
    ]
    
    print("🤖 Invoking LLM to generate mappings...")
    response = client.chat_completion(messages, stream=False)
    
    # Extract JSON
    try:
        content = response.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"❌ JSON Parse Error: {e}")
        print(content)
        return None

if __name__ == "__main__":
    db_path = 'd:/MyProjects/MCP_coze/database/financial.db'
    output_path = 'd:/MyProjects/MCP_coze/config/schema_mappings.json'
    
    print("📊 Reading Schema...")
    schema = get_schema_info(db_path)
    
    print("🧠 Generating Mappings...")
    mappings = generate_mappings(schema)
    
    if mappings:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=4, ensure_ascii=False)
        print(f"✅ Saved mappings to {output_path}")
    else:
        print("❌ Failed to generate mappings.")
