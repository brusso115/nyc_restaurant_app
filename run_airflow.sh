#!/bin/bash

export AIRFLOW_HOME=$(pwd)/airflow_home
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags

echo "🔁 Restarting Airflow..."
pkill -f airflow || true
airflow standalone