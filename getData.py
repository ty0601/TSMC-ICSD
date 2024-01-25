import os
import requests
import json
from datetime import datetime, timedelta

metrics = [
    "run.googleapis.com/container/cpu/utilizations",
    "run.googleapis.com/container/memory/utilizations",
    "run.googleapis.com/container/startup_latencies",
    "run.googleapis.com/container/instance_count",
    "run.googleapis.com/request_count",
    "run.googleapis.com/request_latencies",
]

url = 'https://monitoring.googleapis.com/v3/projects/586786925939/timeSeries:query'
token = "ya29.a0AfB_byBpKX6-xOX8uHKBTSHpgjh25HdYAuL433JHjRVm5JI9gllId6ufe8b0UtiCMA0sUXvnHsVTZ3J_Kp-kz3i3Mrors0rKe-IwhPA-LPQrOVnSqFnzH9GN8AZihLQPamCrDSJeFIrMnHiP43IY0AFm_E1-eK3WczLZN2Y0IVZm91jHgvemOxK04zYyzToOKNGUdbAAceVC8T0880fPvsFrUOgRBRcR1nBQYO-RX6hVvnZYVspcf36e5x5I2kq5wZQc2KcYf8F0N1l-qbTFOqAapUl-8F276wVLFl8K3T4XrkUDrUsJYMtT9KShSJbYoFnxPEAciTezYpM9anOqRSDD34YpxVEZ-vQ9vTv5fl6bPZ3XnnqE2se906bCzrDgkNa4ZEXumG2YMNoJ6CJfqQDt77KqbilhaCgYKAaoSARASFQHGX2MisbA-Nj7TUM_9Az9gJ1SqHw0423"

time = "within 3d"
server_name = "simpleserver"

json_data = [f'''
{{
    "query": "fetch cloud_run_revision | metric '{metric}' | {time} | filter resource.project_id == '586786925939' && (resource.location == 'us-central1' && resource.service_name == '{server_name}')"
}}
''' for metric in metrics]

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

file_name = {
    'cpu_utilizations': 'Container CPU Utilization',
    'memory_utilizations': 'Container Memory Utilization',
    'instance_count': 'Instance Count',
    'startup_latencies': 'Container Startup Latency',
    'request_latencies': 'Request Latency',
    'request_count': 'Request Count'
}


def fetch_logs(project_id, token, filename, page_size=100):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=3)  # 過去 3 天
    time_filter = f"timestamp >= \"{start_time.isoformat()}Z\" AND timestamp <= \"{end_time.isoformat()}Z\""

    # 定義過濾條件
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

    # 將時間篩選條件加入到 filter_condition 中
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

    with open(f"./Dynamic resource/json/{filename}.json", "w") as file:
        json.dump(all_logs, file)


for jd, name in zip(json_data, metrics):
    response = requests.post(url, data=jd, headers=headers)
    filename = name.split("/")[-1]
    if filename == "utilizations":
        filename = name.split("/")[-2] + "_" + filename
    with open(f"./Dynamic resource/json/{file_name[filename]}.json", "w") as file:
        file.write(response.text)

project_id = "tsmccareerhack2024-icsd-grp4"
filename = "cloud_run_logs"

fetch_logs(project_id, token, filename)
