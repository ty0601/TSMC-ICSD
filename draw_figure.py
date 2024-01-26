import matplotlib

matplotlib.use('TkAgg')  # 或 'Qt5Agg', 'WebAgg'

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


def plot_csv(file_path):
    # 讀取CSV檔案
    data = pd.read_csv(file_path)

    # 將時間列轉換為datetime對象
    data[data.columns[0]] = pd.to_datetime(data[data.columns[0]])

    # 繪製折線圖
    plt.figure(figsize=(10, 6))
    plt.plot(data[data.columns[0]], data[data.columns[1]], linestyle='-')

    # 設置標題和軸標籤
    plt.title(f"{data.columns[1]} over {data.columns[0]}")
    plt.xlabel(data.columns[0])
    plt.ylabel(data.columns[1])

    # 改進X軸的日期格式顯示
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
    plt.xticks(rotation=45)

    # 顯示圖表
    plt.tight_layout()
    # print(f"./{file_path.split('/')[1]}/figure/{file_path.split('/')[-1].split('.')[0]}.png")
    plt.savefig(f"./{file_path.split('/')[1]}/figure/{file_path.split('/')[-1].split('.')[0]}.png")
    plt.show()

