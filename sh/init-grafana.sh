#!/bin/bash
# sh/init-grafana.sh

set -e

GRAFANA_URL="http://admin:admin@grafana:3000"

echo "Starting Grafana..."
/run.sh &

echo "Waiting for Grafana to start..."
sleep 20

# 检查数据源
check_datasource() {
  local datasource_name="$1"
  local response=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$GRAFANA_URL/api/datasources/name/$datasource_name")
  echo "$response"
}

echo "Adding InfluxDB data source..."
datasource_name="InfluxDB"
existing=$(check_datasource "$datasource_name")

if [ "$existing" -eq 200 ]; then
  echo "InfluxDB data source '$datasource_name' already exists. Skipping."
else
  response=$(curl -s -w "%{http_code}" -o /dev/null -X POST -H "Content-Type: application/json" -d '{
    "name": "InfluxDB",
    "type": "influxdb",
    "access": "proxy",
    "url": "http://influxdb:8086",
    "database": "metrics",
    "user": "admin",
    "password": "admin"
  }' "$GRAFANA_URL/api/datasources")

  if [ "$response" -eq 200 ]; then
    echo "InfluxDB data source added successfully."
  else
    echo "Failed to add InfluxDB data source. HTTP response code: $response"
  fi
fi

# 添加仪表
echo "Adding dashboard..."
response=$(curl -s -w "%{http_code}" -o /dev/null -X POST -H "Content-Type: application/json" -d @/etc/grafana/provisioning/dashboards/dashboard.json "$GRAFANA_URL/api/dashboards/db")

if [ "$response" -eq 200 ]; then
  echo "CPU Usage dashboard added successfully."
else
  echo "Failed to add CPU Usage dashboard. HTTP response code: $response"
fi

wait
