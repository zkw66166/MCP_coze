
import os

css_path = r'D:\MyProjects\MCP_coze\frontend\src\components\CompanyProfile.css'
org_css_path = r'D:\MyProjects\MCP_coze\frontend\src\components\OrgTree.css'

def fix_css():
    # Read original CSS - try to recover content
    try:
        with open(css_path, 'rb') as f:
            content = f.read()
        
        # Heuristic: if lots of null bytes, might be utf-16 le/be or just corruption
        # Let's try to decode as utf-8 ignoring errors first, then replace nulls
        text = content.decode('utf-8', errors='ignore')
        text = text.replace('\x00', '') # Remove null bytes
        
        # Check if OrgTree styles are already effectively there (but maybe corrupted previously)
        # We'll truncate before the appended "corruption" if we can find where it started
        # The original file ended around line 441.
        
        # Let's just strip whitespace and ensure we have one copy of OrgTree styles
        if ".org-tree-container" in text:
            # It's there, but maybe bad? Let's remove it and re-append to be safe
            text = text.split(".org-tree-container")[0]
        
    except Exception as e:
        print(f"Error reading main CSS: {e}")
        return

    # Read OrgTree CSS
    try:
        with open(org_css_path, 'r', encoding='utf-8') as f:
            org_css = f.read()
    except Exception as e:
        # Fallback if org_css file issues, though we just wrote it
        print(f"Error reading OrgTree CSS: {e}")
        # manual fallback string if needed, but file should exist
        return

    # Combine
    final_css = text.strip() + "\n\n" + org_css
    
    # Write back
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(final_css)
    
    print("Successfully fixed and merged CSS files.")

if __name__ == "__main__":
    fix_css()
