import json
import csv
import datetime
# from draw_figure import plot_csv_subplot


def process_json_to_csv(json_file_path, csv_file_path, data_extractor):
    processed_times = set()
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_extractor['headers'])

        if isinstance(json_data, list):
            for entry in json_data:
                if entry.get('timeInterval') is None:
                    continue
                formatted_time = format_time(entry['timeInterval']['endTime'])
                if formatted_time not in processed_times:
                    processed_times.add(formatted_time)
                    row = data_extractor['row_extractor'](entry)
                    writer.writerow(row)
        else:
            for series_data in json_data['timeSeriesData']:
                for point_data in series_data['pointData']:
                    formatted_time = format_time(point_data['timeInterval']['endTime'])
                    if formatted_time not in processed_times:
                        processed_times.add(formatted_time)
                        row = data_extractor['row_extractor'](point_data)
                        writer.writerow(row)


def format_time(time_str):
    time_obj = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    # Updated format to match your request
    return time_obj.strftime('%a %b %d %Y %H:%M:00')


def instance_count_extractor(json_file_path, csv_file_path, data_extractor):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_extractor['headers'])

        aggregated_data = {}
        for series_data in json_data['timeSeriesData']:
            instance_state = series_data['labelValues'][5]['stringValue']
            for point_data in series_data['pointData']:
                time = format_time(point_data['timeInterval']['endTime'])
                if time is None:
                    continue
                instance_count = int(point_data['values'][0].get('int64Value', 0))

                if time not in aggregated_data:
                    aggregated_data[time] = {'idle': 0, 'active': 0}

                if instance_state == 'idle':
                    aggregated_data[time]['idle'] += instance_count
                else:
                    aggregated_data[time]['active'] += instance_count

        for time, counts in aggregated_data.items():
            row = [time, counts['idle'], counts['active']]
            writer.writerow(row)


def request_count_extractor(json_file_path, csv_file_path, data_extractor):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_extractor['headers'])

        aggregated_data = {}
        for series_data in json_data['timeSeriesData']:
            request_state = series_data['labelValues'][6]['stringValue']
            for point_data in series_data['pointData']:
                time = format_time(point_data['timeInterval']['endTime'])
                if time is None:
                    continue
                request_count = int(point_data['values'][0].get('int64Value', 0))

                if time not in aggregated_data:
                    aggregated_data[time] = {'1xx': 0, '2xx': 0, '3xx': 0, '4xx': 0, '5xx': 0}

                aggregated_data[time][request_state] += request_count

        for time, counts in aggregated_data.items():
            row = [time, counts['1xx'], counts['2xx'], counts['3xx'], counts['4xx'], counts['5xx']]
            writer.writerow(row)

def logs_extractor(json_file_path, csv_file_path, data_extractor):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_extractor['headers'])

        for entry in json_data:
            row = data_extractor['row_extractor'](entry)
            writer.writerow(row)

def main():
    # Extractors for different JSON data types
    extractors = {
        'Request latency': {
            'headers': ["Time", "Request Latency (ms)"],
            'row_extractor': lambda point: [
                format_time(point['timeInterval']['endTime']),
                point['values'][0]['distributionValue'].get('mean', 'N/A')
            ]
        },
        'Startup latency': {
            'headers': ["Time", "Startup Latency (ms)"],
            'row_extractor': lambda point: [
                format_time(point['timeInterval']['endTime']),
                point['values'][0]['distributionValue'].get('mean', 'N/A')
            ]
        },
        'Instance count': {
            'headers': ["Time", "Instance count(idle)", "Instance count(active)"],
            'row_extractor': lambda point: [
                format_time(point['timeInterval']['endTime']),
                point['values'][0].get('int64Value', 'N/A')
            ]
        },
        'Request count': {
            'headers': ["Time", "Request count(1xx)", "Request count(2xx)", "Request count(3xx)", "Request count(4xx)",
                        "Request count(5xx)"],
            'row_extractor': lambda point: [
                format_time(point['timeInterval']['endTime']),
                point['values'][0].get('int64Value', 'N/A')
            ]
        },
        'CPU utilization': {
            'headers': ["Time", "CPU Utilization (%)"],
            'row_extractor': lambda point: [
                format_time(point['timeInterval']['endTime']),
                "{:.4f}".format(float(point['values'][0]['distributionValue'].get('mean', 0)) * 100) if
                point['values'][0][
                    'distributionValue'].get(
                    'mean') is not None else 'N/A'
            ]
        },
        'Memory utilization': {
            'headers': ["Time", "Memory Utilization (%)"],
            'row_extractor': lambda point: [
                format_time(point['timeInterval']['endTime']),
                "{:.4f}".format(float(point['values'][0]['distributionValue'].get('mean', 0)) * 100) if
                point['values'][0][
                    'distributionValue'].get(
                    'mean') is not None else 'N/A'
            ]
        },
        'logs': {
            'headers': ["Timestamp", "Severity", "TextPayload"],
            'row_extractor': lambda entry: [
                entry.get('timestamp', 'N/A').split('.')[0],
                entry.get('severity', 'N/A'),
                entry.get('textPayload', 'N/A').replace('\n', ' ').split('.')[0],
            ]
        }
    }

    # Mapping of JSON files to their corresponding CSV files and extractors
    json_csv_mappings = [
        ("./Dynamic_resource/json/Request_Latency.json", "./Dynamic_resource/csv/Request_Latency.csv",
         extractors['Request latency']),
        ("./Dynamic_resource/json/Container_CPU_Utilization.json",
         "./Dynamic_resource/csv/Container_CPU_Utilization.csv",
         extractors['CPU utilization']),
        ("./Dynamic_resource/json/Container_Memory_Utilization.json",
         "./Dynamic_resource/csv/Container_Memory_Utilization.csv", extractors['Memory utilization']),
        ("./Dynamic_resource/json/Container_Startup_Latency.json",
         "./Dynamic_resource/csv/Container_Startup_Latency.csv",
         extractors['Startup latency']),
    ]

    # Processing each JSON file into its corresponding CSV format
    for json_path, csv_path, extractor in json_csv_mappings:
        process_json_to_csv(json_path, csv_path, extractor)
    instance_count_extractor("./Dynamic_resource/json/Instance_Count.json", "./Dynamic_resource/csv/Instance_Count.csv",
                             extractors['Instance count'])
    request_count_extractor("./Dynamic_resource/json/Request_Count.json", "./Dynamic_resource/csv/Request_Count.csv",
                            extractors['Request count'])
    logs_extractor("./Dynamic_resource/json/Cloud_Run_Logs.json", "./Dynamic_resource/csv/Cloud_Run_Logs.csv",
                  extractors['logs'])

    path = './Dynamic_resource/csv'
    # path = './ICSD_Cloud_Resource'
    file_paths = [
        f"{path}/Request_Latency.csv",
        f"{path}/Container_CPU_Utilization.csv",
        f"{path}/Container_Memory_Utilization.csv",
        f"{path}/Instance_Count.csv",
        f"{path}/Request_Count.csv"
    ]

    output_path = f"{path.split('/')[1]}/figure/subplot.png"
    # plot_csv_subplot(file_paths, output_path)


if __name__ == '__main__':
    main()