import pandas as pd
from influxdb import InfluxDBClient

# 连接 InfluxDB
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('metrics')

# 查询 node_cpu_seconds_total 数据
query = '''
SELECT *
FROM "node_cpu_seconds_total"
WHERE time > now() - 10m
ORDER BY time DESC
LIMIT 1000
'''

# 获取数据
results = client.query(query)
points = list(results.get_points())

# 转换为 DataFrame
df = pd.DataFrame(points)

# 保存到 CSV 文件
csv_file = 'node_cpu_seconds_total.csv'
df.to_csv(csv_file, index=False)

print(f"Data has been written to {csv_file}")
