import boto3
from decouple import config
import papermill as pm
import datetime
from prefect import Flow, task
from prefect.schedules import CronSchedule

client = boto3.client(
    "s3",
    aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
)


@task
def backfill():
    now = datetime.datetime.now()

    pm.execute_notebook(
        "etl/hn_etl_back_fill.ipynb",
        "s3://python-portfolio-notebooks/hn_updates/backfill"
        + str(now.year)
        + "-"
        + str(now.month)
        + "-"
        + str(now.day)
        + ".ipynb",
    )


@task
def frontfill():
    now = datetime.datetime.now()
    pm.execute_notebook(
        "etl/hn_etl_front_fill.ipynb",
        "s3://python-portfolio-notebooks/hn_updates/frontfill"
        + str(now.year)
        + "-"
        + str(now.month)
        + "-"
        + str(now.day)
        + ".ipynb",
    )


@task
def test_changes():

    now = datetime.datetime.now()
    pm.execute_notebook(
        "etl/hn_data_test.ipynb",
        "s3://python-portfolio-notebooks/hn_updates/test"
        + str(now.year)
        + "-"
        + str(now.month)
        + "-"
        + str(now.day)
        + ".ipynb",
    )


with Flow("ETL", schedule=CronSchedule("* * * * *")) as flow:
    test_changes = test_changes()
    frontfill = frontfill()
    backfill = backfill()
   

if __name__=="__main__":
    flow.run()
