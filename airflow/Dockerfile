FROM apache/airflow:2.9.1-python3.10

USER airflow
WORKDIR /opt/airflow

COPY airflow/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir playwright

USER root
ENV HOME=/home/airflow
RUN playwright install --with-deps

USER airflow

COPY airflow/dags/ /opt/airflow/dags/
COPY common/ /opt/airflow/common
COPY scraper/ /opt/airflow/scraper
