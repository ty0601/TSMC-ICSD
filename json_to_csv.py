import json
import csv
import datetime
from draw_figure import plot_csv


def process_json_to_csv(json_file_path, csv_file_path, data_extractor):
    processed_times = set()

    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_extractor['headers'])

        if isinstance(json_data, list):
            for entry in json_data:
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
            'headers': ["Time", "Instance count"],
            'row_extractor': lambda point: [
                format_time(point['timeInterval']['endTime']),
                point['values'][0].get('int64Value', 'N/A')
            ]
        },
        'Request count': {
            'headers': ["Time", "Request count"],
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
            'headers': ["Timestamp", "Severity", "TextPayload", "LogName"],
            'row_extractor': lambda entry: [
                entry.get('timestamp', 'N/A'),
                entry.get('severity', 'N/A'),
                entry.get('textPayload', 'N/A').replace('\n', ' '),
                entry.get('logName', 'N/A')
            ]
        }
    }

    # Mapping of JSON files to their corresponding CSV files and extractors
    json_csv_mappings = [
        ("./Dynamic resource/json/Request Latency.json", "./Dynamic resource/csv/Request Latency.csv",
         extractors['Request latency']),
        ("./Dynamic resource/json/Container CPU Utilization.json",
         "./Dynamic resource/csv/Container CPU Utilization.csv",
         extractors['CPU utilization']),
        ("./Dynamic resource/json/Container Memory Utilization.json",
         "./Dynamic resource/csv/Container Memory Utilization.csv", extractors['Memory utilization']),
        ("./Dynamic resource/json/Container Startup Latency.json",
         "./Dynamic resource/csv/Container Startup Latency.csv",
         extractors['Startup latency']),
        ("./Dynamic resource/json/Instance Count.json", "./Dynamic resource/csv/Instance Count.csv",
         extractors['Instance count']),
        ("./Dynamic resource/json/Request Count.json", "./Dynamic resource/csv/Request Count.csv",
         extractors['Request count']),
        ("./Dynamic resource/json/Cloud_Run_Logs.json", "./Dynamic resource/csv/Cloud_Run_Logs.csv", extractors['logs'])
    ]

    # Processing each JSON file into its corresponding CSV format
    for json_path, csv_path, extractor in json_csv_mappings:
        process_json_to_csv(json_path, csv_path, extractor)

    path = './Dynamic resource/csv'
    file_paths = [
        f"{path}/Request Latency.csv",
        f"{path}/Container CPU Utilization.csv",
        f"{path}/Container Memory Utilization.csv",
        f"{path}/Instance Count.csv",
    ]

    for path in file_paths:
        plot_csv(path)


if __name__ == '__main__':
    main()
