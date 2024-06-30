import requests
from datetime import datetime, timedelta

# Prometheus 服务器地址
prometheus_url = 'http://localhost:9090'

# 查询语句模板
promql_query_cpu_template = '(1-sum(rate(node_cpu_seconds_total{{mode="idle"}}[1m]))by(instance)/sum(rate(node_cpu_seconds_total[1m]))by(instance))*100'
promql_query_mem_template = '(1-(node_memory_Buffers_bytes+node_memory_Cached_bytes+node_memory_MemFree_bytes)/node_memory_MemTotal_bytes)*100'
promql_query_disk_template = '(1-(node_filesystem_avail_bytes{{fstype="ext4"}})/(node_filesystem_size_bytes{{fstype="ext4"}}))*100'
promql_query_net_receive_template = 'irate(node_network_receive_bytes_total{{instance="node-exporter:9100",job="node"}}[1m])*8/1024'
promql_query_net_transmit_template = 'irate(node_network_transmit_bytes_total{{instance="node-exporter:9100",job="node"}}[1m])*8/1024'

def query_prometheus(promql_query, time):
    response = requests.get(f'{prometheus_url}/api/v1/query', params={'query': promql_query, 'time': time})
    if response.status_code == 200:
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
    else:
        print(f"HTTP request failed with status code {response.status_code}")
        return None

def get_metrics_per_minute(promql_query_template, instance=None, job=None, interval=1):
    metrics_list = []
    for i in range(5):
        query_time = (datetime.utcnow() - timedelta(minutes=i)).isoformat() + 'Z'
        if instance and job:
            promql_query = promql_query_template.format(instance=instance, job=job)
        else:
            promql_query = promql_query_template.format(interval=interval)
        metric_value = query_prometheus(promql_query, query_time)
        if metric_value is not None:
            metrics_list.append(metric_value)
            print(f"Minute {i}: {metric_value}")
    return metrics_list

if __name__ == '__main__':
    print("CPU utilization for the last 5 minutes:")
    cpu_busy_list = get_metrics_per_minute(promql_query_cpu_template)
    print(cpu_busy_list)
    
    print("Memory utilization for the last 5 minutes:")
    mem_usage_list = get_metrics_per_minute(promql_query_mem_template)
    print(mem_usage_list)
    
    print("Disk utilization for the last 5 minutes:")
    disk_usage_list = get_metrics_per_minute(promql_query_disk_template)
    print(disk_usage_list) 
    
    instance = 'node-exporter:9100' 
    job = 'node-exporter'  
    print("Network receive for the last 5 minutes (in kB/s):")
    net_receive_list = get_metrics_per_minute(promql_query_net_receive_template, instance=instance, job=job)
    print(net_receive_list)
    
    print("Network transmit for the last 5 minutes (in kB/s):")
    net_transmit_list = get_metrics_per_minute(promql_query_net_transmit_template, instance=instance, job=job)
    print(net_transmit_list)
