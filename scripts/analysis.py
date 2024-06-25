import pandas as pd
from influxdb import InfluxDBClient

# 连接 InfluxDB
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('metrics')

# 查询数据（假设使用 node_cpu_seconds_total）
results = client.query('SELECT * FROM node_cpu_seconds_total')
points = list(results.get_points())

# 转换为 DataFrame
df = pd.DataFrame(points)

# 数据清洗
df.dropna(inplace=True)
df = df[df['value'] >= 0]

# 选择列
# df = df[['time', 'cpu', 'instance', 'mode', 'value']]

# # 将 time 列转换为 datetime 类型
# df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)

# # 设置索引
# df.set_index('time', inplace=True)

# # 计算每个 instance 每分钟的 increase 值
# df = df.groupby(['instance', 'cpu', 'mode']).resample('1T').mean().diff().reset_index()

# # 过滤掉不需要的 mode
# idle_df = df[df['mode'] == 'idle']
# total_df = df.groupby(['time', 'instance'])['value'].sum().reset_index()

# # 合并 idle 和 total
# merged_df = pd.merge(total_df, idle_df, on=['time', 'instance'], suffixes=('_total', '_idle'))

# # 计算 CPU 使用率
# merged_df['cpu_usage'] = (1 - (merged_df['value_idle'] / merged_df['value_total'])) * 100

# # 准备写入 InfluxDB 的数据
# json_body = []
# for _, row in merged_df.iterrows():
#     json_body.append({
#         "measurement": "cpu_usage",
#         "tags": {
#             "instance": row['instance']
#         },
#         "time": row['time'],
#         "fields": {
#             "cpu_usage": row['cpu_usage']
#         }
#     })

# # 写入数据到 InfluxDB
# client.write_points(json_body)

print("CPU Usage data written to InfluxDB.")
