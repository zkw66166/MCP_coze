import os

base_dir = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版\财务报表"

def list_files():
    print(f"Listing: {base_dir}")
    if os.path.exists(base_dir):
        files = os.listdir(base_dir)
        for f in files:
            print(f"File: {f}")
            print(f"Repr: {repr(f)}")
            print(f"Bytes: {f.encode('utf-8')}")

if __name__ == "__main__":
    list_files()
