#做日志分析，因为 PDF 里的项目很强调量化指标，比如响应延迟、幻觉率、自动解决率、意图识别 F1 等。真实项目里，这些指标不是凭空写出来的，而是从日志和评估数据里统计出来的
import csv
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs", "chat_logs.csv")


def infer_query_type(question):
    """根据问题内容，简单推断问题类型"""

    types = []

    if any(word in question for word in ["多少钱", "价格", "售价", "贵不贵"]):
        types.append("价格查询")

    if any(word in question for word in ["库存", "有货", "还有货", "缺货"]):
        types.append("库存查询")

    if any(word in question for word in ["订单", "物流", "快递", "发货", "签收", "到哪了"]):
        types.append("订单查询")

    if any(word in question for word in ["退货", "换货", "售后", "保修", "质量问题", "无理由"]):
        types.append("售后查询")

    if not types:
        types.append("其他问题")

    return types


def analyze_logs():#这是主分析函数，读取日志文件，统计各种数据，然后打印分析报告
    """分析客服系统日志"""

    if not os.path.exists(LOG_FILE):
        print("还没有找到日志文件，请先运行 main_v06.py 产生一些对话日志。")
        return

    total_count = 0#总对话数，初始为 0
    response_times = []
    reject_count = 0#拒答次数，初始为 0，

    type_count = {
        "价格查询": 0,
        "库存查询": 0,
        "订单查询": 0,
        "售后查询": 0,
        "其他问题": 0
    }
#这是一个字典，用来统计每种问题类型出现了多少次。
    with open(LOG_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_count += 1

            question = row["question"]
            response = row["response"]
            response_time = float(row["response_time_seconds"])

            response_times.append(response_time)

            # 简单判断是否拒答
            if response.startswith("抱歉"):
                reject_count += 1

            query_types = infer_query_type(question)

            for query_type in query_types:
                type_count[query_type] += 1
           #把这条问题所属的每个类型，对应计数都加 1
    if total_count == 0:
        print("日志文件为空，暂无可分析数据。")
        return

    avg_response_time = sum(response_times) / len(response_times)
    #avg_response_time，所有响应时间加起来 / 响应时间个数 = 平均响应时间
    max_response_time = max(response_times)
    #最大响应时间
    min_response_time = min(response_times)
    #最小响应时间
    reject_rate = reject_count / total_count
    #拒答次数 / 总对话数 = 拒答率
    print("========== 智能客服日志分析报告 ==========")
    print(f"总对话数：{total_count}")
    print(f"平均响应时间：{avg_response_time:.4f} 秒")
    #保留 4 位小数
    print(f"最大响应时间：{max_response_time:.4f} 秒")
    print(f"最小响应时间：{min_response_time:.4f} 秒")
    print(f"拒答次数：{reject_count}")
    print(f"拒答率：{reject_rate:.2%}")
    #按百分比显示，并保留 2 位小数

    print("\n========== 问题类型分布 ==========")
    for query_type, count in type_count.items():
        print(f"{query_type}：{count} 次")


if __name__ == "__main__":
    analyze_logs()