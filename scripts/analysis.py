import pandas as pd
from influxdb import InfluxDBClient
from sklearn.ensemble import IsolationForest
from prophet import Prophet

# 连接InfluxDB
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('metrics')

# 查询数据
results = client.query('SELECT * FROM cpu_usage')
points = list(results.get_points())

# 转换为DataFrame
df = pd.DataFrame(points)

# 数据清洗
df.dropna(inplace=True)
df = df[df['value'] >= 0]

# 异常检测
model = IsolationForest(contamination=0.01)
model.fit(df[['value']])
df['anomaly'] = model.predict(df[['value']])

# 时间序列预测
df['timestamp'] = pd.to_datetime(df['time'])
df_prophet = df[['timestamp', 'value']].rename(columns={'timestamp': 'ds', 'value': 'y'})
prophet_model = Prophet()
prophet_model.fit(df_prophet)
future = prophet_model.make_future_dataframe(periods=60)
forecast = prophet_model.predict(future)

# 保存预测结果
forecast.to_csv('forecast.csv', index=False)
