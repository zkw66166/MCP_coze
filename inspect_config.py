#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查配置结构，寻找增值税相关配置位置"""

from modules.metrics_loader import get_metrics_loader
import json

loader = get_metrics_loader()
config = loader.load_config()

print('=== 现有表配置 ===')
for table_name in config.get('tables', {}):
    print(f'- {table_name}')
    if 'tax' in table_name or 'vat' in table_name or 'return' in table_name:
        fields = config['tables'][table_name].get('fields', {})
        print(f'  Fields: {list(fields.keys())}')

print('\n=== 查找包含"税"的配置 ===')
for table_name, table_config in config.get('tables', {}).items():
    for field_name, field_config in table_config.get('fields', {}).items():
        aliases = field_config.get('aliases', [])
        for alias in aliases:
            if '增值税' in alias:
                print(f'Found "增值税" in {table_name}.{field_name}: {aliases}')
            if '印花税' in alias:
                print(f'Found "印花税" in {table_name}.{field_name}: {aliases}')

