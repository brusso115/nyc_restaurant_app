#!/bin/bash

cd "$(dirname "$0")"
export AIRFLOW_HOME=$(cd ../airflow && pwd)
export AIRFLOW__CORE__DAGS_FOLDER=$AIRFLOW_HOME/dags

# 👇 Add this to make imports like `common.db_manager` work
export PYTHONPATH=$(cd .. && pwd)

echo "🔁 Restarting Airflow..."
pkill -f airflow || true
airflow standalone
