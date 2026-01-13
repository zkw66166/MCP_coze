#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""寻找增值税配置行号"""

with open('config/metrics_config.json', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '"vat_payable"' in line:
        print(f'Found "vat_payable" at line {i+1}')
        # Print next 10 lines to see aliases
        for j in range(1, 15):
            print(f'{i+1+j}: {lines[i+j].rstrip()}')
