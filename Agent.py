from vertexai.preview.generative_models import GenerativeModel
import pandas as pd
import csv


class DataLoadAgent:
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.merged_data = None

    def load_and_merge_data(self):
        # Reading the files into dataframes
        dataframes = {path.split('/')[-1].split('.')[0]: pd.read_csv(path) for path in self.file_paths}
        print(dataframes)
        # Standardizing the time format and setting it as index for each dataframe
        for df in dataframes.values():
            df['Time'] = pd.to_datetime(df['Time'])
            df.set_index('Time', inplace=True)

        # Merging all dataframes on the 'Time' index
        self.merged_data = pd.concat(dataframes.values(), axis=1)

        # Preprocess the data right after merging
        self.preprocess_data()

        # Saving the merged and preprocessed data as a new CSV file
        self.merged_data.to_csv('./Dynamic_resource/merged_cloud_data.csv')

    def get_merged_data(self):
        if self.merged_data is not None:
            return self.merged_data.to_csv(index=False)
        else:
            raise ValueError("Data not loaded. Please run load_and_merge_data() first.")

    def preprocess_data(self):
        # Assuming the self.merged_data is a DataFrame
        if self.merged_data is not None:
            with open(f'.//merged_cloud_data.csv', 'r') as f:
                reader = list(csv.reader(f))
                title = reader[0]
                data = reader[1:]
                for idx, row in enumerate(data):
                    row[0] = row[0].split(' ')[1][:5]
                    row[1] = row[1].split('.')[0]
                    row[2] = row[2].split('.')[0]
                    row[3] = row[3].split('.')[0]
                    data[idx] = [row[i] for i in list(range(0, 4)) + list(range(5, 7)) + [8]]
                title = [title[i] for i in list(range(0, 4)) + list(range(5, 7)) + [8]]
                return [title] + data
        else:
            raise ValueError("Data not loaded. Please run load_and_merge_data() first.")

    def get_merged_data_batches(self, batch_size=30):
        if self.merged_data is not None:
            # Resetting index to make 'Time' a column
            data_with_time = self.merged_data.reset_index()
            return [data_with_time.iloc[i:i + batch_size].to_csv(index=False) for i in
                    range(0, len(data_with_time), batch_size)]
        else:
            raise ValueError("Data not loaded. Please run load_and_merge_data() first.")


class DataAnalysisAgent:
    def __init__(self, model_name):
        self.model = GenerativeModel(model_name)
        self.chat = self.model.start_chat()
        self.user_decision_log = './Dynamic_resource/user_decision_log'

    def get_chat_response(self, data_summary):
        user_log_prompt = ""
        if isinstance(self.user_decision_log):
            with open(self.user_decision_log, 'r') as f:
                user_log_prompt = f.read().strip('\n')

        prompt = '''
            I have organized and preprocessed a cloud operation dataset, which includes metrics :
            Time(YYYY-MM-DD hh:mm:ss),Request_Latency (ms),Container_CPU_Utilization (%),Container_Memory_Utilization (%),Container_Startup_Latency (ms),Instance_Count (active),Instance_Count (idle),Request_Count (1xx),Request_Count (2xx),Request_Count (3xx),Request_Count (4xx)
            The title of each column, columns are separated by comma.
            Use the following step-by-step instructions to respond:
                step 1. Read the data carefully
                step 2. Analyze the correlation between data metrics and consider the case :
                    Many times, we do not wish to simply increase the number of instances, but rather to specifically increase CPU or RAM. In situations where only the CPU is insufficient, merely adding instances would instead result in additional costs for increasing RAM.
                step 3. Based on this data and correlation between the data metrics, please response each anomalies in the provided data and follow the template:
                     <Time> : {YYYY-MM-DD hh:mm:ss ~ hh:mm:ss}
                     <Problems> :
                     <Recommendation> : (scale up or scale down instance's CPU/instance 's memory/Instance_Count)
        ''' + data_summary + '\n' + user_log_prompt + '\n'

        response = self.chat.send_message(prompt)
        return response.text


def main():
    file_path = "./Dynamic_resource/csv"
    file_paths = [
        f"{file_path}/Request_Latency.csv",
        f"{file_path}/Container_CPU_Utilization.csv",
        f"{file_path}/Container_Memory_Utilization.csv",
        f"{file_path}/Container_Startup_Latency.csv",
        f"{file_path}/Instance_Count.csv",
        f"{file_path}/Request_Count.csv"
    ]

    data_agent = DataLoadAgent(file_paths)
    data_agent.load_and_merge_data()
    merged_data_batches = data_agent.get_merged_data_batches(batch_size=50)

    analysis_agent = DataAnalysisAgent("gemini-pro")

    for i, batch_csv in enumerate(merged_data_batches):
        analyzed_data = analysis_agent.get_chat_response(batch_csv)
        print(analyzed_data)

        break


if __name__ == '__main__':
    main()
