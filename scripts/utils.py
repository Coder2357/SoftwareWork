# utils.py 存放通用函数

import requests

def query_prometheus(prometheus_url, promql_query, time):
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

def write_to_influxdb(client, bucket, org, measurement, fields):
    from datetime import datetime
    from influxdb_client import Point, WritePrecision
    try:
        point = Point(measurement).time(datetime.utcnow(), WritePrecision.NS)
        for field, value in fields.items():
            point.field(field, value)
        write_api = client.write_api()
        write_api.write(bucket=bucket, org=org, record=point)
        print("Data written to InfluxDB successfully.")
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")
