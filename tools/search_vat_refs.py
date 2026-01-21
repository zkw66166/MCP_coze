import json

def find_refs():
    with open('config/metrics_config.json', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    found = False
    for i, line in enumerate(lines):
        if 'vat_returns' in line or 'vat_return_items' in line:
            print(f"Line {i+1}: {line.strip()}")
            found = True
            
    if not found:
        print("No references found.")

if __name__ == "__main__":
    find_refs()
