import matplotlib

matplotlib.use('TkAgg')  # 或 'Qt5Agg', 'WebAgg'

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

y_mapping = {
    'Request Latency': 'Request Latency (ms)',
    'Container CPU Utilization': 'CPU Utilization (%)',
    'Container Memory Utilization': 'Memory Utilization (%)',
    'Instance Count': 'Instance count',
    'Request Count': 'Request count'
}


def plot_csv_subplot(file_paths, output_path):
    # 設置圖表的總大小
    plt.figure(figsize=(15, 10))

    # 對於每個CSV檔案，創建一個子圖
    for i, file_path in enumerate(file_paths, 1):
        data = pd.read_csv(file_path)
        data[data.columns[0]] = pd.to_datetime(data[data.columns[0]])

        # 創建子圖
        ax = plt.subplot(len(file_paths), 1, i)
        for column in data.columns[1:]:
            ax.plot(data[data.columns[0]], data[column], linestyle='-', label=column)

        # 設置標題和軸標籤
        ax.set_title(f"{file_path.split('/')[-1].split('.')[0]}")
        ax.set_xlabel(data.columns[0])
        ax.set_ylabel("Value")

        # 改進X軸的日期格式顯示
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
        plt.xticks(rotation=45)

        # 添加圖例
        ax.legend()

    # 自動調整子圖間距
    plt.tight_layout()

    # 保存圖表
    plt.savefig(output_path)
    plt.close()


# path = './ICSD Cloud Resource/'
# path = './Dynamic resource/csv/'
# file_paths = [
#     f"{path}Request Latency.csv",
#     f"{path}Container CPU Utilization.csv",
#     f"{path}Container Memory Utilization.csv",
#     f"{path}Instance Count.csv",
#     f"{path}Request Count.csv"
# ]
#
# output_path = f"./{path.split('/')[1]}/figure/subplot.png"
# plot_csv_subplot(file_paths, output_path)

