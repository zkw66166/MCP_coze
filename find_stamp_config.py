#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""寻找tax_return_stamp_items配置行号"""

with open('config/metrics_config.json', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '"tax_return_stamp_items": {' in line:
        print(f'Found table definition at line {i+1}')
        # Print next 20 lines
        for j in range(1, 25):
            print(f'{i+1+j}: {lines[i+j].rstrip()}')
