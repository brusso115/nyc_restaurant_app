#!/bin/bash

# Exit if any command fails
set -e

# Recommended to activate your virtualenv before running this script

echo "📦 Installing Apache Airflow..."

# Set the Airflow version you want
AIRFLOW_VERSION=2.8.2

# Dynamically get your Python version (e.g., 3.10)
PYTHON_VERSION=$(python --version | cut -d " " -f 2 | cut -d "." -f 1,2)

# Constraint URL for Airflow dependencies
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Upgrade pip and install Airflow
pip install --upgrade pip setuptools wheel
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

echo "✅ Airflow $AIRFLOW_VERSION installed successfully!"