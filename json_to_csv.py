import json
import csv
import datetime


def process_json_to_csv(json_file_path, csv_file_path, data_extractor):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write headers
        writer.writerow(data_extractor['headers'])

        for series_data in json_data['timeSeriesData']:
            for point_data in series_data['pointData']:
                row = data_extractor['row_extractor'](point_data)
                writer.writerow(row)


def format_time(time_str):
    # 解析 ISO 8601 格式的時間
    time_obj = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    # 格式化為 'YYYY-MM-DD hh:mm:ss' 形式
    return time_obj.strftime('%Y-%m-%d %H:%M:%S')


# Extractors for different JSON data types
extractors = {
    'latency': {
        'headers': ["Time", "Latency (ms)"],
        'row_extractor': lambda point: [
            format_time(point['timeInterval']['endTime']),
            point['values'][0]['distributionValue'].get('mean', 'N/A')
        ]
    },
    'count': {
        'headers': ["Time", "Count"],
        'row_extractor': lambda point: [
            format_time(point['timeInterval']['endTime']),
            point['values'][0].get('int64Value', 'N/A')
        ]
    },
    'utilization': {
        'headers': ["Time", "Utilization (%)"],
        'row_extractor': lambda point: [
            format_time(point['timeInterval']['endTime']),
            "{:.4f}".format(float(point['values'][0]['distributionValue'].get('mean', 0)) * 100) if point['values'][0][
                                                                                                        'distributionValue'].get(
                'mean') is not None else 'N/A'
        ]
    }
}

# Mapping of JSON files to their corresponding CSV files and extractors
json_csv_mappings = [
    ("./Dynamic resource/json/Request Latency.json", "./Dynamic resource/csv/Request Latency.csv",
     extractors['latency']),
    ("./Dynamic resource/json/Container CPU Utilization.json", "./Dynamic resource/csv/Container CPU Utilization.csv",
     extractors['utilization']),
    ("./Dynamic resource/json/Container Memory Utilization.json",
     "./Dynamic resource/csv/Container Memory Utilization.csv", extractors['utilization']),
    ("./Dynamic resource/json/Container Startup Latency.json", "./Dynamic resource/csv/Container Startup Latency.csv",
     extractors['latency']),
    ("./Dynamic resource/json/Instance Count.json", "./Dynamic resource/csv/Instance Count.csv", extractors['count']),
    ("./Dynamic resource/json/Request Count.json", "./Dynamic resource/csv/Request Count.csv", extractors['count'])
]

# Processing each JSON file into its corresponding CSV format
for json_path, csv_path, extractor in json_csv_mappings:
    process_json_to_csv(json_path, csv_path, extractor)

print("All JSON files have been processed into CSV format.")
