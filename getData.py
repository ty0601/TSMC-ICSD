import os
import requests
import json
from datetime import datetime, timedelta


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
        with open(f"./Dynamic resource/json/{file_name[filename]}.json", "w") as file:
            file.write(response.text)


def fetch_logs(project_id, token, filename, page_size=100):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)  # 過去 3 天
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

    with open(f"./Dynamic resource/json/{filename}.json", "w") as file:
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
    token = "ya29.a0AfB_byDQRv8cjjHUksFNI1Q68-dOii2MekCB_JFIP8nBfdrWMcptiCHJtvBOoOj1EwljYWFOEHrO85fSGdYYQTCVNrs2VnVnJoe1pynITUkomUs7l4VPssJpv6w_Wnwnd0ogp-Jg8McogRWt_OE0P_Dj_pE7ZISqBaVZHqygs_uivzycBym_0m-T3mqSnwkt5FVobkiYTbDwsmCIxc_OudwUXOiKdbUNHwegO0vzxmxSsvwBjs3hNlJzx9T9kEE1AI3C5Va5t8ss7mxLSfOyLVarU39OrbhY2d0ByUs5VyeIahwrxjQ-kvEXRRA_1P7SEmuK5zT9c_tVhx_Gr271CTuL4fAcVcRYduxYcV8QfBXyX5cfTG6h44pcRvUWQvmzpokxcJDhSVAnrYO79Mx2k9MMSK13aCgYKAaQSARASFQHGX2Mi93JsYDrMDpQBp2ALxRv4yA0419"  # Replace with your actual token
    server_name = "simpleserver"

    file_name = {
        'cpu_utilizations': 'Container CPU Utilization',
        'memory_utilizations': 'Container Memory Utilization',
        'instance_count': 'Instance Count',
        'startup_latencies': 'Container Startup Latency',
        'request_latencies': 'Request Latency',
        'request_count': 'Request Count'
    }

    fetch_metrics_data(metrics, url, token, server_name, file_name)

    project_id = "tsmccareerhack2024-icsd-grp4"
    filename = "cloud_run_logs"
    fetch_logs(project_id, token, filename)


if __name__ == "__main__":
    main()
