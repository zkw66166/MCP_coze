#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open('config/metrics_config.json', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_table = False
for i, line in enumerate(lines):
    if '"tax_return_stamp_items": {' in line:
        in_table = True
        print(f'Enter table at {i+1}')
    
    if in_table:
        if '"tax_amount": {' in line:
            print(f'Found tax_amount at {i+1}')
            # Print aliases
            for j in range(1, 15):
                print(f'{i+1+j}: {lines[i+j].rstrip()}')
            break
        
        # Stop if we exit table (simple heuristic: look for next table or closing brace at high level)
        if '},' in line and line.strip() == '},':
             # Might be end of table, but safer to just let it run until tax_amount found
             pass
