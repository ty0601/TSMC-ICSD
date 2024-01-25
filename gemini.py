from vertexai.preview.generative_models import GenerativeModel, ChatSession
from Data import get_data

model = GenerativeModel("gemini-pro")
chat = model.start_chat()


def get_chat_response(chat: ChatSession, prompt: str) -> str:
    response = chat.send_message(prompt)
    return response.text


data_summary = get_data()
prompt = '''
        I have organized and preprocessed a cloud operation dataset, which includes time-series metrics for each point in time: request latency in milliseconds, container CPU utilization in percentage, container memory utilization in percentage, container startup latency in milliseconds, active instance count, and idle instance count. The time range covers the past month, with data recorded at one-minute intervals. I have cleaned the data and addressed missing and anomalous values. Based on this data, please analyze the following questions:
        Based on this data, please response each anomalies in the provided data and follow the template:
        
        <Time> : 
        <Problems> : 
        <Recommendation> :
    ''' + data_summary
# print(prompt)
print(get_chat_response(chat, prompt))
