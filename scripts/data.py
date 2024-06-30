import json
import requests
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision

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

# 计数器
data_collection_counter = 0

def query_prometheus(promql_query, time):
    try:
        response = requests.get(f'{prometheus_url}/api/v1/query', params={'query': promql_query, 'time': time})
        response.raise_for_status()
        result = response.json()
        if result['status'] == 'success':
            data = result['data']['result']
            if data:
                return float(data[0]['value'][1])
            else:
                print("No data found for the query")
                return None
        else:
            print(f"Error in query: {result['error']}")
            return None
    except Exception as e:
        print(f"Failed to query Prometheus: {e}")
        return None

def get_metric(promql_query_template, instance=None, job=None):
    query_time = datetime.utcnow().isoformat() + 'Z'
    if instance and job:
        promql_query = promql_query_template
    else:
        promql_query = promql_query_template
    metric_value = query_prometheus(promql_query, query_time)
    if metric_value is not None:
        print(f"Current metric value: {metric_value}")
    return metric_value

def write_to_influxdb(client, bucket, org, measurement, fields):
    try:
        point = Point(measurement).time(datetime.utcnow(), WritePrecision.NS)
        for field, value in fields.items():
            point.field(field, value)
        write_api = client.write_api()
        write_api.write(bucket=bucket, org=org, record=point)
        print("Data written to InfluxDB successfully.")
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")

def get_data():
    global data_collection_counter
    data_collection_counter += 1
    try:
        print(f"Data collection started (count: {data_collection_counter})...")
        client = InfluxDBClient(url=influxdb_url, token=influxdb_api_key, org=influxdb_org)

        # cpu使用率
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

        # 接收速率
        instance = 'node-exporter:9100'
        job = 'node-exporter'
        print("Collecting network receive rate data...")
        net_receive_rate = get_metric(promql_query_net_receive_template)
        if net_receive_rate is not None:
            write_to_influxdb(client, influxdb_bucket, influxdb_org, "net_receive", {"rate": net_receive_rate})

        # 发送速率
        print("Collecting network transmit rate data...")
        net_transmit_rate = get_metric(promql_query_net_transmit_template)
        if net_transmit_rate is not None:
            write_to_influxdb(client, influxdb_bucket, influxdb_org, "net_transmit", {"rate": net_transmit_rate})

        print("Data collection completed.")
    except Exception as e:
        print(f"Error during data collection: {e}")

if __name__ == '__main__':
    get_data()
