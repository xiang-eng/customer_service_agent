import csv
import os
from datetime import datetime
'''调用 write_log
↓
先执行 init_log_file()
↓
检查 logs 文件夹有没有
↓
没有就创建 logs 文件夹
↓
检查 chat_logs.csv 有没有
↓
没有就创建 chat_logs.csv，并写入表头
↓
获取当前时间
↓
以追加模式打开 chat_logs.csv
↓
写入一行日志'''

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")#拼接日志文件夹路径。D:\customer_service_agent\logs
LOG_FILE = os.path.join(LOG_DIR, "chat_logs.csv")#日志最终会写到这个文件chat_logs.csv里。
#保存到logs/chat_logs.csv

def init_log_file():
    """初始化日志文件，如果不存在就创建"""

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)#创建 LOG_DIR 这个文件夹。

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8-sig", newline="") as f:
#注意："w" 有一个特点：如果文件不存在，会创建文件，如果文件已存在，会清空原来的内容
#它和 utf-8 很像，但更适合给 Excel 打开 CSV。因为如果 CSV 里有中文，用普通 utf-8 有时 Excel 打开会乱码。
            writer = csv.writer(f)
            writer.writerow(["time", "question", "response", "response_time_seconds"])


def write_log(question, response, response_time):#写入日志函数
    """写入一条对话日志"""

    init_log_file()#先初始化日志文件

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#获取当前时间，并格式化成字符串。
    with open(LOG_FILE, "a", encoding="utf-8-sig", newline="") as f:
        #追加写入日志文件
        writer = csv.writer(f)
        writer.writerow([current_time, question, response, response_time])


 # logger.py = 记录员，每次用户问问题，它就帮我们把问题、回答、耗时写进 CSV 文件。 

 