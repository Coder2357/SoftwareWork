import json
from datetime import datetime
from influxdb_client import InfluxDBClient
from utils import query_prometheus, write_to_influxdb

prometheus_url = 'http://localhost:9090'

# InfluxDB 配置
with open('../config.json', 'r') as f:
    config = json.load(f)

influxdb_api_key = config['influxdb_api_key']
influxdb_org = config['influxdb_org']
influxdb_url = 'http://localhost:8086'
influxdb_bucket = 'metrics'

# 查询语句模板
promql_query_cpu_template = '(1-sum(rate(node_cpu_seconds_total{mode="idle"}[1m]))by(instance)/sum(rate(node_cpu_seconds_total[1m]))by(instance))*100'
promql_query_mem_template = '(1-(node_memory_Buffers_bytes+node_memory_Cached_bytes+node_memory_MemFree_bytes)/node_memory_MemTotal_bytes)*100'
promql_query_disk_template = '(1-(node_filesystem_avail_bytes{fstype="ext4"})/(node_filesystem_size_bytes{fstype="ext4"}))*100'
promql_query_net_receive_template = 'irate(node_network_receive_bytes_total{instance="node-exporter:9100",job="node"}[1m])*8/1024'
promql_query_net_transmit_template = 'irate(node_network_transmit_bytes_total{instance="node-exporter:9100",job="node"}[1m])*8/1024'

def get_metric(promql_query_template):
    query_time = datetime.utcnow().isoformat() + 'Z'
    promql_query = promql_query_template
    metric_value = query_prometheus(prometheus_url, promql_query, query_time)
    if metric_value is not None:
        print(f"Current metric value: {metric_value}")
    return metric_value

def get_data():
    try:
        print("Data collection started...")
        client = InfluxDBClient(url=influxdb_url, token=influxdb_api_key, org=influxdb_org)

        # CPU 使用率
        print("Collecting CPU utilization data...")
        cpu_usage = get_metric(promql_query_cpu_template)
        if cpu_usage is not None:
            write_to_influxdb(client, influxdb_bucket, influxdb_org, "cpu_usage", {"usage": cpu_usage})

        # 内存使用率
        print("Collecting memory utilization data...")
        mem_usage = get_metric(promql_query_mem_template)
        if mem_usage is not None:
            write_to_influxdb(client, influxdb_bucket, influxdb_org, "memory_usage", {"usage": mem_usage})

        # 磁盘使用率
        print("Collecting disk utilization data...")
        disk_usage = get_metric(promql_query_disk_template)
        if disk_usage is not None:
            write_to_influxdb(client, influxdb_bucket, influxdb_org, "disk_usage", {"usage": disk_usage})

        # 网络接收速率
        print("Collecting network receive rate data...")
        net_receive_rate = get_metric(promql_query_net_receive_template)
        if net_receive_rate is not None:
            write_to_influxdb(client, influxdb_bucket, influxdb_org, "net_receive", {"rate": net_receive_rate})

        # 网络发送速率
        print("Collecting network transmit rate data...")
        net_transmit_rate = get_metric(promql_query_net_transmit_template)
        if net_transmit_rate is not None:
            write_to_influxdb(client, influxdb_bucket, influxdb_org, "net_transmit", {"rate": net_transmit_rate})

        print("Data collection completed.")
    except Exception as e:
        print(f"Error during data collection: {e}")

if __name__ == '__main__':
    get_data()
