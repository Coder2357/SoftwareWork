# del.py 删除所有数据，用于调试db用，慎用
import json
from influxdb_client import InfluxDBClient
from datetime import datetime

with open('../config.json', 'r') as f:
    config = json.load(f)

influxdb_api_key = config['influxdb_api_key']
influxdb_org = config['influxdb_org']
influxdb_url = 'http://localhost:8086'
influxdb_bucket = 'metrics'

def delete_all_data_from_bucket(client, bucket, org):
    try:
        now = datetime.utcnow()
        start_time = '1970-01-01T00:00:00Z' 

        delete_api = client.delete_api()

        delete_api.delete(start=start_time, stop=now.isoformat() + 'Z', predicate='_measurement != ""', bucket=bucket, org=org)
        print("All data deleted from InfluxDB bucket successfully.")
    except Exception as e:
        print(f"Error deleting data from InfluxDB: {e}")

if __name__ == '__main__':
    client = InfluxDBClient(url=influxdb_url, token=influxdb_api_key, org=influxdb_org)
    delete_all_data_from_bucket(client, influxdb_bucket, influxdb_org)
