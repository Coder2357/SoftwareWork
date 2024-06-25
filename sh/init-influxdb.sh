#!/bin/bash
# sh/init-influxdb.sh

set -e

echo "Starting InfluxDB..."
influxd &

echo "Waiting for InfluxDB to start..."
sleep 10

echo "Creating database 'metrics'..."
influx -execute "CREATE DATABASE metrics"

wait
