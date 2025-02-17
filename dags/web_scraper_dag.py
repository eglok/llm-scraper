from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests

def scrape_data():
    # Trigger the scraper; assuming an endpoint to start scraping exists
    response = requests.get("http://scraper:6800/schedule.json?project=default&spider=web_scraper")
    response.raise_for_status()

def process_data():
    # Retrieve scraped data and post it to the LLM service for processing
    data = requests.get("http://scraper:6800/get_data").json()
    for item in data:
        response = requests.post("http://llm-service:8000/process/", json=item)
        response.raise_for_status()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG("web_scraper_dag", default_args=default_args, schedule_interval="0 * * * *")

scrape_task = PythonOperator(
    task_id="scrape_task", python_callable=scrape_data, dag=dag
)
process_task = PythonOperator(
    task_id="process_task", python_callable=process_data, dag=dag
)

scrape_task >> process_task
