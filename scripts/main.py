import time
import json
from init import setup_influxdb
from data import get_data
from anomaly_detection import detect_anomaly
from prediction import predict_usage, plot_forecast
from decision_making import make_decision

# 历史数据
cpu_usage_history = []
memory_usage_history = []

def main():
    # 初始化
    setup_influxdb()

    # 读取配置文件中的阈值
    with open('../config.json', 'r') as f:
        config = json.load(f)
        cpu_threshold = config['cpu_threshold']
        memory_threshold = config['memory_threshold']

    # 每分钟进行一次数据收集和分析
    while True:
        try:
            data = get_data()

            if "CPU Usage" in data and data["CPU Usage"]:
                metric_name = "CPU Usage"
                current_value = data[metric_name]
                cpu_usage_history.append(current_value)

                # 仅保留最近的三十个数据点
                if len(cpu_usage_history) > 30:
                    cpu_usage_history.pop(0)

                # 异常检测
                detect_anomaly(metric_name, cpu_usage_history, cpu_threshold)

                # 如果历史数据足够，进行预测分析
                if len(cpu_usage_history) >= 5:
                    forecast = predict_usage(metric_name, cpu_usage_history)
                    predicted_value = forecast['yhat'].iloc[-1]
                    print(f"Predicted {metric_name}: {predicted_value}")

                    # 决策
                    make_decision(metric_name, predicted_value)

            if "Memory Usage" in data and data["Memory Usage"]:
                metric_name = "Memory Usage"
                current_value = data[metric_name]
                memory_usage_history.append(current_value)

                # 仅保留最近的三十个数据点
                if len(memory_usage_history) > 30:
                    memory_usage_history.pop(0)

                # 异常检测
                detect_anomaly(metric_name, memory_usage_history, memory_threshold)

                # 如果历史数据足够，进行预测分析
                if len(memory_usage_history) >= 5:
                    forecast = predict_usage(metric_name, memory_usage_history)
                    predicted_value = forecast['yhat'].iloc[-1]
                    print(f"Predicted {metric_name}: {predicted_value}")

                    # 决策与执行
                    make_decision(metric_name, predicted_value)

        except Exception as e:
            print(f"Error during execution: {e}")

        time.sleep(60)  # 休眠60秒

if __name__ == '__main__':
    main()
