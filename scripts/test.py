# TEST用于查询对应数据

import pandas as pd
from influxdb import InfluxDBClient

# 连接InfluxDB
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('metrics')

# 查询所有measurements
measurements = client.query('SHOW MEASUREMENTS')
measurements_list = list(measurements.get_points())

# 打印所有measurements
print("Measurements in 'metrics' database:")
for measurement in measurements_list:
    print(measurement['name'])

# 检查是否存在 'xxx' measurement
if any(measurement['name'] == 'node_cpu_usage' for measurement in measurements_list):
    # 查询数据
    results = client.query('SELECT * FROM node_cpu_usage')
    points = list(results.get_points())

    # 转换为DataFrame
    df = pd.DataFrame(points)

    # 查看数据
    print("DataFrame head:\n", df.head())
    print("DataFrame info:\n", df.info())
else:
    print("measurement 不存在")
