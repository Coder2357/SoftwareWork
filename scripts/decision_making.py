import json
import requests

with open('../config.json', 'r') as f:
    config = json.load(f)

cpu_threshold = config['cpu_threshold']
memory_threshold = config['memory_threshold']

def scale_up():
    print("Scaling up resources...")
    # TODO : 分配资源

def scale_down():
    print("Scaling down resources...")
    # TODO : 分配资源

def make_decision(metric_name, predicted_value):
    if metric_name == "CPU Usage" and predicted_value > cpu_threshold:
        scale_up()
    elif metric_name == "Memory Usage" and predicted_value > memory_threshold:
        scale_up()
    elif metric_name == "Disk Usage" and predicted_value > disk_threshold:
        scale_up()
    else:
        scale_down()
