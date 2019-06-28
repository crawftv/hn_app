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
def notebook_test():
	now = datetime.datetime.now()

	pm.execute_notebook(
	    "hn_etl_back_fill.ipynb",
	    "s3://python-portfolio-notebooks/hn_updates/test"
	    + str(now.year)
	    + "-"
	    + str(now.month)
	    + "-"
	    + str(now.day)
	    + ".ipynb",
	)

	pm.execute_notebook(
	    "hn_etl_front_fill.ipynb",
	    "s3://python-portfolio-notebooks/hn_updates/test"
	    + str(now.year)
	    + "-"
	    + str(now.month)
	    + "-"
	    + str(now.day)
	    + ".ipynb",
	)


	pm.execute_notebook(
	    "hn_data_test.ipynb",
	    "s3://python-portfolio-notebooks/hn_updates/test"
	    + str(now.year)
	    + "-"
	    + str(now.month)
	    + "-"
	    + str(now.day)
	    + ".ipynb",
	)

with Flow('Test',schedule =CronSchedule('* * * * *') ) as flow:
	test = notebook_test()

flow.run()
