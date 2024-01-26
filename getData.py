import os
import requests
import json
from datetime import datetime, timedelta


def get_token():
    os.system("gcloud auth application-default print-access-token > token.txt")
    with open("token.txt", "r") as file:
        token = file.read().strip()
    os.remove("token.txt")
    return token


def fetch_metrics_data(metrics, url, token, server_name, file_name):
    time = "within 1d"
    json_data = [
        f'''
        {{
            "query": "fetch cloud_run_revision | metric '{metric}' | {time} | filter resource.project_id == '586786925939' && (resource.location == 'us-central1' && resource.service_name == '{server_name}')"
        }}
        ''' for metric in metrics
    ]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    for jd, name in zip(json_data, metrics):
        response = requests.post(url, data=jd, headers=headers)
        filename = name.split("/")[-1]
        if filename == "utilizations":
            filename = name.split("/")[-2] + "_" + filename
        with open(f"./Dynamic_resource/json/{file_name[filename]}.json", "w") as file:
            file.write(response.text)


def fetch_logs(project_id, token, filename, page_size=100):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    time_filter = f"timestamp >= \"{start_time.isoformat()}Z\" AND timestamp <= \"{end_time.isoformat()}Z\""

    filter_condition = (
        'resource.type="cloud_run_revision" '
        'resource.labels.revision_name="simpleserver-00001-kgv" '
        'resource.labels.service_name="simpleserver" '
        'logName=("projects/tsmccareerhack2024-icsd-grp4/logs/run.googleapis.com%2Frequests" OR '
        '"projects/tsmccareerhack2024-icsd-grp4/logs/run.googleapis.com%2Fstderr" OR '
        '"projects/tsmccareerhack2024-icsd-grp4/logs/run.googleapis.com%2Fstdout" OR '
        '"projects/tsmccareerhack2024-icsd-grp4/logs/run.googleapis.com%2Fvarlog%2Fsystem") '
        'severity>=WARNING'
    )

    full_filter = f"{filter_condition} AND {time_filter}"

    url = "https://logging.googleapis.com/v2/entries:list"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "resourceNames": [f"projects/{project_id}"],
        "filter": full_filter,
        "pageSize": page_size
    }

    all_logs = []
    while True:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            all_logs.extend(response_data.get('entries', []))
            next_page_token = response_data.get('nextPageToken')
            if not next_page_token:
                break
            data['pageToken'] = next_page_token
        else:
            print(f"Error fetching logs: {response.text}")
            break

    with open(f"./Dynamic_resource/json/{filename}.json", "w") as file:
        json.dump(all_logs, file)


def main():
    metrics = [
        "run.googleapis.com/container/cpu/utilizations",
        "run.googleapis.com/container/memory/utilizations",
        "run.googleapis.com/container/startup_latencies",
        "run.googleapis.com/container/instance_count",
        "run.googleapis.com/request_count",
        "run.googleapis.com/request_latencies",
    ]

    url = 'https://monitoring.googleapis.com/v3/projects/586786925939/timeSeries:query'
    token = get_token()

    server_name = "simpleserver"

    file_name = {
        'cpu_utilizations': 'Container_CPU_Utilization',
        'memory_utilizations': 'Container_Memory_Utilization',
        'instance_count': 'Instance_Count',
        'startup_latencies': 'Container_Startup_Latency',
        'request_latencies': 'Request_Latency',
        'request_count': 'Request_Count'
    }

    fetch_metrics_data(metrics, url, token, server_name, file_name)

    project_id = "tsmccareerhack2024-icsd-grp4"
    filename = "cloud_run_logs"
    fetch_logs(project_id, token, filename)


if __name__ == "__main__":
    main()
