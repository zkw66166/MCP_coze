#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库中的数据"""

import sqlite3

conn = sqlite3.connect('database/tax_incentives.db')
c = conn.cursor()

# 测试LIKE搜索
c.execute('SELECT COUNT(*) FROM tax_incentives WHERE project_name LIKE ?', ('%高新%',))
print('LIKE搜索"高新":', c.fetchone()[0])

c.execute('SELECT COUNT(*) FROM tax_incentives WHERE qualification LIKE ?', ('%高新%',))
print('LIKE搜索"高新"(认定条件):', c.fetchone()[0])

c.execute('SELECT COUNT(*) FROM tax_incentives WHERE project_name LIKE ?', ('%小微%',))
print('LIKE搜索"小微":', c.fetchone()[0])

c.execute('SELECT COUNT(*) FROM tax_incentives WHERE qualification LIKE ?', ('%小微%',))
print('LIKE搜索"小微"(认定条件):', c.fetchone()[0])

# 查看一些示例
print('\n示例数据:')
c.execute('SELECT tax_type, project_name FROM tax_incentives LIMIT 10')
for row in c.fetchall():
    print(f'  [{row[0]}] {row[1][:50]}')

conn.close()
