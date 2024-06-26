import pandas as pd
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
from prophet import Prophet
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import requests
import json

# 读取配置文件
with open('../config.json', 'r') as f:
    config = json.load(f)

grafana_api_key = config['grafana_api_key']
grafana_url = config['grafana_url']

# 连接 InfluxDB
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('metrics')

# 计算查询时间范围：过去五分钟的数据
end_time = datetime.utcnow()
start_time = end_time - timedelta(minutes=5)

print(f"查询时间范围：从 {start_time} 到 {end_time}")

# 查询 CPU 时间数据，按每分钟查询并计算 CPU 利用率
cpu_utilization_list = []
query_times = []

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
            query_times.append(query_end)
            print(f"第 {i+1} 分钟的 CPU 利用率: {cpu_utilization}%")

# 输出每分钟的 CPU 利用率列表
print("每分钟的 CPU 利用率列表:")
print(cpu_utilization_list)

# 如果获取到足够的 CPU 利用率数据，进行预测和告警
if len(cpu_utilization_list) == 5:
    cpu_usage_df = pd.DataFrame({
        'ds': query_times,
        'y': cpu_utilization_list
    })

    print("DataFrame for Prophet:")
    print(cpu_usage_df)

    # 使用 Prophet 进行时间序列预测
    model = Prophet()
    model.fit(cpu_usage_df)

    # 创建未来数据框，预测下一分钟
    future = model.make_future_dataframe(periods=1, freq='T')
    print("Future DataFrame for Prophet prediction:")
    print(future)

    # 进行预测
    forecast = model.predict(future)
    print("Prophet forecast:")
    print(forecast)

    # 获取预测值
    predicted_cpu_usage_prophet = forecast['yhat'].iloc[-1]
    print(f"Predicted CPU usage by Prophet: {predicted_cpu_usage_prophet}")

    # 使用 scikit-learn 进行线性回归预测
    cpu_usage_df['time_numeric'] = cpu_usage_df['ds'].apply(lambda x: x.value)
    X = cpu_usage_df[['time_numeric']]
    y = cpu_usage_df['y']
    model_lr = LinearRegression()
    model_lr.fit(X, y)
    predicted_cpu_usage_lr = model_lr.predict([[future['ds'].iloc[-1].value]])[0]
    print(f"Predicted CPU usage by Linear Regression: {predicted_cpu_usage_lr}")

    # 平均预测结果
    predicted_cpu_usage = (predicted_cpu_usage_prophet + predicted_cpu_usage_lr) / 2
    print(f"Average predicted CPU usage: {predicted_cpu_usage}")

    # 设定告警阈值
    threshold = 40  # 示例阈值，按你的需求设置

    # 判断是否超过阈值
    if predicted_cpu_usage > threshold:
        print(f"告警: CPU 使用率超过阈值 {threshold}%, 预测值为 {predicted_cpu_usage}%")

        # 创建告警规则的 JSON 数据
        alert_rule = {
            "name": "High CPU Usage Alert",
            "rules": [
                {
                    "alert": "High CPU Usage",
                    "expr": f"{predicted_cpu_usage} > {threshold}",
                    "for": "1m",
                    "labels": {
                        "severity": "critical"
                    },
                    "annotations": {
                        "summary": "CPU usage is above threshold",
                        "description": f"CPU usage is predicted to be {predicted_cpu_usage}%, which is above the threshold of {threshold}%."
                    }
                }
            ]
        }

        # 发送 POST 请求到 Grafana API 创建告警规则
        response = requests.post(grafana_url, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {grafana_api_key}"
        }, data=json.dumps(alert_rule))

        if response.status_code == 200:
            print("告警规则创建成功")
        else:
            print(f"告警规则创建失败: {response.content}")
    else:
        print("CPU 使用率未超过阈值，无需创建告警")

    # 可视化预测结果
    fig1 = model.plot(forecast)
    plt.title('CPU Usage Forecast')
    plt.xlabel('Time')
    plt.ylabel('CPU Usage')
    plt.show()
    
else:
    print("未检索到足够的数据，请检查查询和数据源。")
