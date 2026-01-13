import json
import sqlite3
import sys
import os

# Add project root to path
sys.path.append('d:/MyProjects/MCP_coze')

def verify_json_integrity(filepath):
    """Verify that the JSON file is valid and can be loaded."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ JSON is valid: {filepath}")
        return data
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error in {filepath}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def verify_cash_flow_aliases(config_data):
    """Check if specific aliases exist in the config."""
    aliases_to_check = [
        "销售货物和服务收到的现金", 
        "其他经营活动收到的现金",
        "经营活动产生的现金流量净额",
        "处置固定资产、无形资产和其他长期资产收回的现金净额",
        "期末现金及现金等价物余额"
    ]
    
    cf_fields = config_data.get('tables', {}).get('cash_flow_statements', {}).get('fields', {})
    
    all_aliases = set()
    for field_name, field_data in cf_fields.items():
        all_aliases.update(field_data.get('aliases', []))
        
    print("\n🔍 Verifying Aliases:")
    for alias in aliases_to_check:
        if alias in all_aliases:
            print(f"  ✅ Found: {alias}")
        else:
            print(f"  ❌ Missing: {alias}")

if __name__ == "__main__":
    filepath = 'd:/MyProjects/MCP_coze/config/metrics_config.json'
    data = verify_json_integrity(filepath)
    if data:
        verify_cash_flow_aliases(data)
