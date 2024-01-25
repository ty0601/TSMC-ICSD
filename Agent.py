from vertexai.preview.generative_models import GenerativeModel
import pandas as pd


class DataLoadAgent:
    def __init__(self, file_paths):
        # Initialize with a list of file paths
        self.file_paths = file_paths
        self.merged_data = None

    def load_and_merge_data(self):
        # Reading the files into dataframes
        dataframes = {path.split('/')[-1].split('.')[0]: pd.read_csv(path) for path in self.file_paths}

        # Standardizing the time format and setting it as index for each dataframe
        for df in dataframes.values():
            df['Time'] = pd.to_datetime(df['Time'])
            df.set_index('Time', inplace=True)

        # Merging all dataframes on the 'Time' index
        self.merged_data = pd.concat(dataframes.values(), axis=1)

        # Saving the merged data as a new CSV file
        self.merged_data.to_csv('merged_cloud_data.csv')

    def get_merged_data(self):
        # Return the merged data as CSV string without index
        if self.merged_data is not None:
            return self.merged_data.to_csv(index=False)
        else:
            raise ValueError("Data not loaded. Please run load_and_merge_data() first.")

    def get_merged_data_batches(self, batch_size=10):
        # Ensure 'Time' column is included in the CSV
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

    def get_chat_response(self, data_summary):
        prompt = '''
            I have organized and preprocessed a cloud operation dataset, which includes metrics :
            Time(YYYY-MM-DD hh:mm:ss),Request Latency (ms),Container CPU Utilization (%),Container Memory Utilization (%),Container Startup Latency (ms),Instance Count (active),Instance Count (idle),Request Count (1xx),Request Count (2xx),Request Count (3xx),Request Count (4xx)
            The title of each column, columns are separated by comma.
            Use the following step-by-step instructions to respond:
                step 1. Read the data carefully
                step 2. Analyze the correlation between data metrics and consider the case :
                    Many times, we do not wish to simply increase the number of instances, but rather to specifically increase CPU or RAM. In situations where only the CPU is insufficient, merely adding instances would instead result in additional costs for increasing RAM.
                step 3. Based on this data and correlation between the data metrics, please response each anomalies in the provided data and follow the template:
                     <Time> : {YYYY-MM-DD hh:mm:ss ~ hh:mm:ss}
                     <Problems> :
                     <Recommendation> : (scale up or scale down instance's CPU/instance 's memory/instance count)
        ''' + data_summary

        response = self.chat.send_message(prompt)
        return response.text


class SuspendAnalysisAgent:
    def __init__(self, model_name):
        self.model = GenerativeModel(model_name)
        self.chat = self.model.start_chat()

    def get_chat_response(self, data_summary, analyzed_data):
        prompt = '''
            I have organized and preprocessed a cloud operation dataset, which includes metrics :
            Time(YYYY-MM-DD hh:mm:ss),Request Latency (ms),Container CPU Utilization (%),Container Memory Utilization (%),Container Startup Latency (ms),Instance Count (active),Instance Count (idle),Request Count (1xx),Request Count (2xx),Request Count (3xx),Request Count (4xx)
            And this is the analysis that I made, please check if the problem is really a problem and the recommendation is really helpful.
            Use the following step-by-step instructions to respond:
                step 1. Read the data and the analyzed data carefully.
                step 2. Analyze the correlation between data metrics.
                step 3. Check the analyzed data.
                step 4. Response your opinion about the analyzed data.
        ''' + data_summary + analyzed_data

        response = self.chat.send_message(prompt)
        return response.text


class FinalAnalysisAgent:
    def __init__(self, model_name):
        self.model = GenerativeModel(model_name)
        self.chat = self.model.start_chat()

    def get_chat_response(self, data_summary, analyzed_data, opinion):
        prompt = '''
            I have organized and preprocessed a cloud operation dataset, which includes metrics :
            Time(YYYY-MM-DD hh:mm:ss),Request Latency (ms),Container CPU Utilization (%),Container Memory Utilization (%),Container Startup Latency (ms),Instance Count (active),Instance Count (idle),Request Count (1xx),Request Count (2xx),Request Count (3xx),Request Count (4xx)
            I have made some recommendation about the analyzed data, please redo the report
            Use the following step-by-step instructions to respond:
                step 1. Read the data, the analyzed data and opinion carefully.
                step 2. Analyze the correlation between data metrics.
                step 3. Response the new analyzed data according to the opinion and follow the template:
                    <Problem Time> : {YYYY-MM-DD hh:mm:ss ~ hh:mm:ss}
                    <Problems> :
                    <Recommendation> : (scale up or scale down instance's CPU/instance 's memory/instance count)
        ''' + data_summary + analyzed_data + opinion

        response = self.chat.send_message(prompt)
        return response.text

# class DataAnalysisAgent:
#     def __init__(self, model_name):
#         self.model = GenerativeModel(model_name)
#         self.chat = self.model.start_chat()
#
#     def get_chat_response(self, data_summary):
#         prompt = '''
#             please consider mean, std, min, max and response the threshold of scaling CPU, memory and instance.
#         ''' + data_summary
#
#         response = self.chat.send_message(prompt)
#         return response.text


def main():
    file_paths = [
        "./ICSD Cloud Resource/Request Latency.csv",
        "./ICSD Cloud Resource/Container CPU Utilization.csv",
        "./ICSD Cloud Resource/Container Memory Utilization.csv",
        "./ICSD Cloud Resource/Container Startup Latency.csv",
        "./ICSD Cloud Resource/Instance Count.csv",
        "./ICSD Cloud Resource/Request Count.csv"
    ]

    data_agent = DataLoadAgent(file_paths)
    data_agent.load_and_merge_data()
    merged_data_batches = data_agent.get_merged_data_batches()

    analysis_agent = DataAnalysisAgent("gemini-pro")
    suspend_agent = SuspendAnalysisAgent("gemini-pro")
    final_agent = FinalAnalysisAgent("gemini-pro")

    for i, batch_csv in enumerate(merged_data_batches):
        analyzed_data = analysis_agent.get_chat_response(batch_csv)
        print(analyzed_data)
        print('------------------------------------------------------------------------------------------------------')
        opinion = suspend_agent.get_chat_response(batch_csv, analyzed_data)
        print(opinion)
        print('------------------------------------------------------------------------------------------------------')
        final_analyzed_data = final_agent.get_chat_response(batch_csv, analyzed_data, opinion)
        print(final_analyzed_data)
        print()

        break
    # analyzed_data = analysis_agent.get_chat_response(data_agent.get_merged_data())
    # print(analyzed_data)


if __name__ == '__main__':
    main()
