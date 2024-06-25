import requests

# 查看所有数据库
response = requests.get('http://localhost:8086/query', params={'q': 'SHOW DATABASES'})
print(response.json())

# 查看数据库中的表
db_name = 'metrics'
response = requests.get('http://localhost:8086/query', params={'q': 'SHOW MEASUREMENTS', 'db': db_name})
print(response.json())

# 查询具体表中的数据
table_name = 'node_cpu_seconds'
response = requests.get('http://localhost:8086/query', params={'q': f'SELECT * FROM {table_name} LIMIT 5', 'db': db_name})
print(response.json())
