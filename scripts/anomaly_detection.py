import numpy as np
from sklearn.ensemble import IsolationForest
import requests
from datetime import datetime
import json

# 从配置文件读取阈值
with open('../config.json', 'r') as f:
    config = json.load(f)
    cpu_threshold = config['cpu_threshold']
    memory_threshold = config['memory_threshold']
    disk_threshold = config['disk_threshold']

def log_anomaly(metric_name, value, reason):
    log_message = f"{datetime.utcnow().isoformat()}: Anomaly detected in {metric_name}: {value}. Reason: {reason}"
    
    # 记录到文件
    with open('anomalies.log', 'a') as log_file:
        log_file.write(log_message + '\n')
    
    print(log_message)

    # 发送警报到 AlertManager
    alert = {
        "labels": {
            "alertname": "AnomalyDetection",
            "severity": "critical"
        },
        "annotations": {
            "summary": f"Anomaly detected in {metric_name}",
            "description": f"The value of {metric_name} is {value}, which has been detected as an anomaly due to {reason}."
        }
    }

    try:
        response = requests.post('http://localhost:9093/api/v2/alerts', json=[alert])
        response.raise_for_status()
        print(f"Alert sent successfully: Status Code {response.status_code} - {response.reason}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send alert: {e}")

def detect_anomaly(metric_name, values, threshold):
    values = np.array(values).reshape(-1, 1)

    # 基于模型的异常检测 bug : 边缘点
    if len(values) >= 30:
        try:
            model = IsolationForest(contamination=0.1)
            predictions = model.fit_predict(values) 
            anomalies = values[predictions == -1]
            if len(anomalies) > 0:
                for anomaly in anomalies:
                    log_anomaly(metric_name, anomaly[0], reason="outlier detection")
        except Exception as e:
            print(f"Error during model-based anomaly detection: {e}")

    # 基于阈值的异常检测
    for value in values:
        if value > threshold:
            log_anomaly(metric_name, value[0], reason="threshold exceeded")

    # 异常增长检测
    growth_threshold = 20  # 20%的增长阈值
    for i in range(1, len(values)):
        if values[i] > values[i - 1] * (1 + growth_threshold):
            log_anomaly(metric_name, values[i][0], reason="abnormal growth")

# 示例测试
if __name__ == '__main__':
    # 稳定的数据
    stable_values = [11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12]
    print("Testing with stable data:")
    detect_anomaly("Stable Metric", stable_values, threshold=50)

    # 包含异常点的数据
    abnormal_values = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 100, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    print("Testing with data containing an anomaly:")
    detect_anomaly("Anomaly Metric", abnormal_values, threshold=50)

    # 缓慢增大的数据
    gradually_increasing_values = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    print("Testing with gradually increasing data:")
    detect_anomaly("Increasing Metric", gradually_increasing_values, threshold=50)

    # 超过阈值的数据
    threshold_exceeding_values = [11, 15, 20, 25, 30, 35, 45, 55, 60, 11, 15, 20, 25, 30, 35, 45, 11, 15, 20, 25, 30, 35, 45, 11, 15, 20, 25, 30, 35, 45]
    print("Testing with data exceeding the threshold:")
    detect_anomaly("Threshold Metric", threshold_exceeding_values, threshold=50)
