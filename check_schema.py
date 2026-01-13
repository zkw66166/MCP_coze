#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('database/financial.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(tax_return_stamp_items)")
print(f'=== tax_return_stamp_items Columns ===')
for row in cursor.fetchall():
    print(row[1])
conn.close()
