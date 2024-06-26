import pandas as pd
from influxdb import InfluxDBClient
from datetime import datetime, timedelta

# 连接 InfluxDB
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('metrics')

# 计算查询时间范围：过去五分钟的数据
end_time = datetime.utcnow()
start_time = end_time - timedelta(minutes=5)

print(f"查询时间范围：从 {start_time} 到 {end_time}")

# 查询 CPU 时间数据，按每分钟查询并计算 CPU 利用率
cpu_utilization_list = []
for i in range(5):
    # 每分钟的时间范围
    query_start = end_time - timedelta(minutes=i+1)
    query_end = end_time - timedelta(minutes=i)

    # 构建查询语句
    query = f'''
    SELECT SUM("value") AS total_cpu_time, MAX("time") AS query_time
    FROM "node_cpu_seconds_total"
    WHERE "instance" = 'node-exporter:9100'
    AND time > '{query_start.strftime('%Y-%m-%dT%H:%M:%SZ')}' AND time <= '{query_end.strftime('%Y-%m-%dT%H:%M:%SZ')}'
    '''

    # 执行查询
    results = client.query(query)
    points = list(results.get_points())

    if points:
        total_cpu_time = points[0]['total_cpu_time']
        query_time = points[0]['query_time']

        # 查询 idle 模式的 CPU 时间
        query_idle = f'''
        SELECT SUM("value") AS idle_cpu_time
        FROM "node_cpu_seconds_total"
        WHERE "instance" = 'node-exporter:9100' AND "mode" = 'idle'
        AND time > '{query_start.strftime('%Y-%m-%dT%H:%M:%SZ')}' AND time <= '{query_end.strftime('%Y-%m-%dT%H:%M:%SZ')}'
        '''
        results_idle = client.query(query_idle)
        points_idle = list(results_idle.get_points())
        
        if points_idle:
            idle_cpu_time = points_idle[0]['idle_cpu_time']

            # 计算 CPU 利用率
            cpu_utilization = (total_cpu_time - idle_cpu_time) / total_cpu_time * 100
            cpu_utilization_list.append(cpu_utilization)
            print(f"第 {i+1} 分钟的 CPU 利用率: {cpu_utilization}%")

# 输出每分钟的 CPU 利用率列表
print("每分钟的 CPU 利用率列表:")
print(cpu_utilization_list)
