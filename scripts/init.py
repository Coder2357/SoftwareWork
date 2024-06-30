import json
import requests
import subprocess

def setup_influxdb():
    with open('../config.json', 'r') as f:
        config = json.load(f)

    grafana_api_key = config['grafana_api_key']
    influxdb_api_key = config['influxdb_api_key']
    influxdb_org = config['influxdb_org']

    # 确保 InfluxDB 容器正在运行
    print("Checking if InfluxDB container is running...")
    result = subprocess.run(['docker', 'ps', '-q', '-f', 'name=influxdb'], capture_output=True, text=True)
    if result.stdout.strip() == "":
        print("InfluxDB container is not running. Please start it manually.")
        exit(1)
    else:
        print("InfluxDB container is running.")

    # 获取 InfluxDB organization ID
    print("Getting InfluxDB organization ID...")
    influx_url = 'http://localhost:8086/api/v2'
    token = influxdb_api_key

    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(f'{influx_url}/orgs', headers=headers)
    if response.status_code == 200:
        orgs = response.json()['orgs']
        org_id = next((org['id'] for org in orgs if org['name'] == influxdb_org), None)
        if org_id:
            print(f"Organization ID: {org_id}")
        else:
            print(f"Organization '{influxdb_org}' not found.")
            exit(1)
    else:
        print(f"Failed to get organization ID: {response.text}")
        exit(1)

    # 创建 InfluxDB Bucket
    print("Creating InfluxDB bucket 'metrics'...")
    bucket = 'metrics'
    data = {
        "name": bucket,
        "orgID": org_id,
        "retentionRules": [{"everySeconds": 3600, "shardGroupDurationSeconds": 3600}]
    }

    response = requests.post(f'{influx_url}/buckets', headers=headers, json=data)
    if response.status_code == 201:
        print("Bucket 'metrics' created successfully.")
    elif response.status_code == 409:
        print("Bucket 'metrics' already exists.")
    else:
        print(f"Failed to create bucket: {response.text}")

    # 导入 Grafana 仪表盘
    # print("Importing Grafana dashboard...")
    # Uncomment and update the path if needed
    # dashboard_json_path = '../json/dashboard.json'
    # grafana_url = 'http://localhost:3000/api/dashboards/db'
    # headers = {
    #     'Authorization': f'Bearer {grafana_api_key}',
    #     'Content-Type': 'application/json'
    # }

    # with open(dashboard_json_path, 'r') as f:
    #     dashboard_json = json.load(f)

    # response = requests.post(grafana_url, headers=headers, json=dashboard_json)
    # if response.status_code == 200:
    #     print("Grafana dashboard imported successfully.")
    # else:
    #     print(f"Failed to import Grafana dashboard: {response.text}")


if __name__ == '__main__':
    setup_influxdb()
