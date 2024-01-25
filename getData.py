import os
import requests

metrics = [
    "run.googleapis.com/container/cpu/utilizations",
    "run.googleapis.com/container/memory/utilizations",
    "run.googleapis.com/container/startup_latencies",
    "run.googleapis.com/container/instance_count",
    "run.googleapis.com/request_count",
    "run.googleapis.com/request_latencies",
]

url = 'https://monitoring.googleapis.com/v3/projects/586786925939/timeSeries:query'
token = "ya29.a0AfB_byC0G8ZeMTkcTyHkH307nrGXQnRTVQJOeMXqvsy93Ujf0RARFrB_K2e3Nw8rztCmqufuDNblcYiY9GzEztdJqmwY2qFQuP04N9mzOoduI3yE3kluMD0YKTA0LtavK8v5lRIc_RWP3tPey7eqO8o5VuOOUQuTfyMeM0yUwQMbHIsJHwudQLq0pZQNtOxDjdzxYPNJTnA5k9a6RK911GKR_ebPm6ZUwsFqa2ifPIXgPhAK_3pnpktM_z2A6qS4YFIpk6C87OSxWHp8uxdf71EIshSdJ826_HHPv0NzxjBmW7P9RPzMCW1uH-ePjjSCORT79HDZFLDBwXkkUqptzGBSQrPNF_2YGxq1uAjKqTqj_rrg-eXRbXqHZ8rNCMiuiZYJRo9EBm48QH53yK0ZzeS4PtM6VBrAaCgYKATYSARASFQHGX2Mi5_MaG41AUHBZ3rAO42LcaA0423"

time = "within 1d"
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

for jd, name in zip(json_data, metrics):
    response = requests.post(url, data=jd, headers=headers)
    filename = name.split("/")[-1]
    if filename == "utilizations":
        filename = name.split("/")[-2] + "_" + filename
    file = open(f"./Dynamic resource/json/{file_name[filename]}.json", "w")
    file.write(response.text)
