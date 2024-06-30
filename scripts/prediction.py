# predict.py 用于预测未来指标数据

from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt

def predict_usage(metric_name, history):
    df = pd.DataFrame(history, columns=['y'])
    df['ds'] = pd.date_range(start='2023-01-01', periods=len(history), freq='T')
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=60, freq='T')
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def plot_forecast(metric_name, history, forecast):
    plt.figure(figsize=(10, 6))
    plt.plot(pd.date_range(start='2023-01-01', periods=len(history), freq='T'), history, label='Historical Data')
    plt.plot(forecast['ds'], forecast['yhat'], label='Predicted Data', color='blue')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='blue', alpha=0.2)
    plt.title(f'Forecast for {metric_name}')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # 稳定的数据
    stable_values = [11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12]
    print("Predicting with stable data:")
    forecast_stable = predict_usage("Stable Metric", stable_values)
    plot_forecast("Stable Metric", stable_values, forecast_stable)

    # 包含异常点的数据
    abnormal_values = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 100, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    print("Predicting with data containing an anomaly:")
    forecast_abnormal = predict_usage("Anomaly Metric", abnormal_values)
    plot_forecast("Anomaly Metric", abnormal_values, forecast_abnormal)

    # 缓慢增大的数据
    gradually_increasing_values = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    print("Predicting with gradually increasing data:")
    forecast_increasing = predict_usage("Increasing Metric", gradually_increasing_values)
    plot_forecast("Increasing Metric", gradually_increasing_values, forecast_increasing)

    # 超过阈值的数据
    threshold_exceeding_values = [11, 15, 20, 25, 30, 35, 45, 55, 60, 11, 15, 20, 25, 30, 35, 45, 11, 15, 20, 25, 30, 35, 45, 11, 15, 20, 25, 30, 35, 45]
    print("Predicting with data exceeding the threshold:")
    forecast_threshold = predict_usage("Threshold Metric", threshold_exceeding_values)
    plot_forecast("Threshold Metric", threshold_exceeding_values, forecast_threshold)


