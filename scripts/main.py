import time
from init import setup_influxdb
from data import get_data
from anomaly_detection import detect_anomaly
from prediction import predict_usage
from decision_making import make_decision

def main():
    # 初始化
    setup_influxdb()

    # 每分钟调用一次数据收集和分析函数
    while True:
        try:
            # 收集数据
            get_data()

            # 检测异常
            metric_name = "CPU Usage"
            history = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            detect_anomaly(metric_name, history)


            # 预测分析
            forecast = predict_usage(metric_name, history)
            predicted_value = forecast['yhat'].iloc[-1]
            print(f"Predicted {metric_name}: {predicted_value}")

            # 决策与执行
            make_decision(metric_name, predicted_value)

        except Exception as e:
            print(f"Error during execution: {e}")

        time.sleep(60)  # 休眠60秒

if __name__ == '__main__':
    main()
