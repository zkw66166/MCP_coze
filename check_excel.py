import pandas as pd

df = pd.read_excel('data_source/税收优惠政策一览表(coze).xlsx')
print('总行数:', len(df))
print('\n列名:')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print('\n前3行数据:')
print(df.head(3))
