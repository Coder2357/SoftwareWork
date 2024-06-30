import time
from init import setup_influxdb
from data import get_data

def main():
    # 先运行初始化脚本
    setup_influxdb()
    
    # 无限循环，每分钟调用一次数据收集函数
    while True:
        try:
            get_data()
        except Exception as e:
            print(f"Error during data collection: {e}")
        time.sleep(60)  # 休眠60秒

if __name__ == '__main__':
    main()
