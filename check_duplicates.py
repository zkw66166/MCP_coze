#!/usr/bin/env python
# -*- coding: utf-8 -*-
from modules.metrics_loader import get_metrics_loader

loader = get_metrics_loader()
config = loader.load_config()

print('=== 检查印花税额定义 ===')

# Check tables
for table, t_conf in config.get('tables', {}).items():
    for field, f_conf in t_conf.get('fields', {}).items():
        if '印花税额' in f_conf.get('aliases', []):
            print(f'Found in TABLES: {table}.{field}')

# Check item_queries
for q_name, q_conf in config.get('item_queries', {}).items():
    if '印花税额' in q_conf.get('aliases', []):
        print(f'Found in ITEM_QUERIES: {q_name}')
