import time
from datetime import datetime, timedelta

from google.cloud import aiplatform


def submit_job():
    project = "your-project-id"
    location = "us-central1"
    display_name = "catboost-training-job"
    container_uri = "gcr.io/cloud-aiplatform/training/catboost-cpu.0-24:latest"
    command = ["python3", "your-training-script.py"]
    args = ["--arg1", "value1", "--arg2", "value2"]
    gcs_output_directory = "gs://your-bucket/output"

    worker_pool_spec = [
        {
            "replica_count": 1,
            "machine_spec": {
                "machine_type": "n1-standard-4",
            },
            "container_spec": {
                "image_uri": container_uri,
                "command": command,
                "args": args,
            },
        }
    ]

    job_spec = {
        "display_name": display_name,
        "job_spec": {
            "worker_pool_specs": worker_pool_spec,
            "base_output_directory": {
                "output_uri_prefix": gcs_output_directory,
            },
        },
    }

    options = dict(api_endpoint="us-central1-aiplatform.googleapis.com")
    client = aiplatform.gapic.JobServiceClient(client_options=options)
    parent = f"projects/{project}/locations/{location}"

    response = client.create_custom_job(parent=parent, custom_job=job_spec)
    print("Job created:", response.name)


def schedule_job():
    next_run_time = datetime.now()

    while True:
        if datetime.now() >= next_run_time:
            submit_job()
            next_run_time = datetime.now() + timedelta(days=3)
        time.sleep(60 * 60)  # check every hour


if __name__ == "__main__":
    schedule_job()
