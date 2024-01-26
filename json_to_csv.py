import json
import csv
import datetime


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
                entry.get('textPayload', 'N/A').replace('\n', ' '),  # 去除換行符
                entry.get('logName', 'N/A')
            ]
        }
    }

    # Mapping of JSON files to their corresponding CSV files and extractors
    json_csv_mappings = [
        ("./Dynamic resource/json/Request Latency.json", "./Dynamic resource/csv/Request Latency.csv",
         extractors['latency']),
        ("./Dynamic resource/json/Container CPU Utilization.json",
         "./Dynamic resource/csv/Container CPU Utilization.csv",
         extractors['utilization']),
        ("./Dynamic resource/json/Container Memory Utilization.json",
         "./Dynamic resource/csv/Container Memory Utilization.csv", extractors['utilization']),
        ("./Dynamic resource/json/Container Startup Latency.json",
         "./Dynamic resource/csv/Container Startup Latency.csv",
         extractors['latency']),
        ("./Dynamic resource/json/Instance Count.json", "./Dynamic resource/csv/Instance Count.csv",
         extractors['count']),
        ("./Dynamic resource/json/Request Count.json", "./Dynamic resource/csv/Request Count.csv", extractors['count']),
        ("./Dynamic resource/json/Cloud_Run_Logs.json", "./Dynamic resource/csv/Cloud_Run_Logs.csv", extractors['logs'])
    ]

    # Processing each JSON file into its corresponding CSV format
    for json_path, csv_path, extractor in json_csv_mappings:
        process_json_to_csv(json_path, csv_path, extractor)

    print("All JSON files have been processed into CSV format.")


if __name__ == '__main__':
    main()
