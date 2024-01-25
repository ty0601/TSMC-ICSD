import vertexai
from vertexai.preview.language_models import TextGenerationModel
import os
import pandas as pd
from Data import get_data

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
                     <Recommendation> : (scale up or scale down CPU/memory/instance)
        '''


def predict_large_language_model(
        model_name: str,
        temperature: float,
        max_output_tokens: int,
        top_p: float,
        top_k: int,
        content: str,
        tuned_model_name: str = "",
):
    model = TextGenerationModel.from_pretrained(model_name)
    if tuned_model_name:
        model = model.get_tuned_model(tuned_model_name)
    response = model.predict(
        content,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_k=top_k,
        top_p=top_p, )
    return response.text


review = "Please analysis the data and response the Time, problems and recommendations. "
batch_data = get_data()

for i, data in enumerate(batch_data):
    content = prompt + data

    response_text = predict_large_language_model(
        "text-bison@001",
        temperature=0.2,
        max_output_tokens=1024,
        top_p=0.8,
        top_k=1,
        content=content)

    print(response_text)
    if i > 2:
        break
