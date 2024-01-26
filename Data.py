import pandas as pd

def get_data():
    # Load the provided CSV files
    file_paths = [
        "./ICSD_Cloud_Resource/Request_Latency.csv",
        "./ICSD_Cloud_Resource/Container_CPU_Utilization.csv",
        "./ICSD_Cloud_Resource/Container_Memory_Utilization.csv",
        "./ICSD_Cloud_Resource/Container_Startup_Latency.csv",
        "./ICSD_Cloud_Resource/Instance_Count.csv",
        "./ICSD_Cloud_Resource/Request_Count.csv"
    ]

    # Reading the files into dataframes
    dataframes = {path.split('/')[-1].split('.')[0]: pd.read_csv(path) for path in file_paths}

    # Standardizing the time format and setting it as index for each dataframe
    for df in dataframes.values():
        df['Time'] = pd.to_datetime(df['Time'])
        df.set_index('Time', inplace=True)

    # Merging all dataframes on the 'Time' index
    merged_data = pd.concat(dataframes.values(), axis=1)

    # Saving the merged data as a new CSV file
    merged_data.to_csv('merged_cloud_data.csv')

    data_with_time = merged_data.reset_index()
    return [data_with_time.iloc[i:i + 20].to_csv(index=False) for i in
            range(0, len(data_with_time), 20)]

# Call the function and print the return value
# print(get_data())
