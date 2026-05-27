import csv
import os

from intent import classify_intents



BASE_DIR = os.path.dirname(os.path.abspath(__file__))#获取当前 Python 文件所在目录
#结果是D:\customer_service_agent
TEST_FILE = os.path.join(BASE_DIR, "data", "test_intents.csv")
#拼接出测试文件 test_intents.csv 的完整路径
#结果是D:\customer_service_agent\data\test_intents.csv
def parse_intents(intent_text):
    """把 price_query|stock_query 转成集合"""
#把由 | 分隔的字符串，转换成集合
    return set(intent_text.strip().split("|"))#set是把列表转换为集合
#strip() 的作用是去掉字符串两边的空格、换行   .split("|") 按 | 把字符串切开
#因为这里不关心顺序，只关心“包含哪些意图”。所以用集合

def evaluate_intent():#这是主函数，负责真正做评估。
    """评估意图识别效果"""

    total_count = 0#总测试样本数
    exact_match_count = 0#完全匹配的数量

    # 用来统计每一种意图的 TP / FP / FN
    labels = [
        "price_query",
        "stock_query",
        "policy_query",
        "order_query",
        "general_query",
        "unknown_query"
    ]

    metrics = {}#用来保存每个标签的统计数据

    for label in labels:
        metrics[label] = {
            "TP": 0,#以 price_query 为例：该预测成price_query，也确实预测成价格查询了
            "FP": 0,#标准答案里没有 price_query，但预测里有。
            "FN": 0#标准答案里有 price_query，但预测里没有。
        }
#给每一个意图标签准备一个小字典，
#里面记录 TP、FP、FN，初始都为 0
    print("========== 意图识别评估明细 ==========")

    with open(TEST_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_count += 1

            question = row["question"]
            expected = parse_intents(row["expected_intents"])
            predicted = set(classify_intents(question))

            is_exact_match = expected == predicted
            #判断标准答案集合 和 预测集合 是否完全相同
            if is_exact_match:
                exact_match_count += 1

            print(f"\n问题：{question}")
            print(f"标准意图：{sorted(expected)}")
            print(f"预测意图：{sorted(predicted)}")
            print(f"是否完全正确：{is_exact_match}")

            for label in labels:
                if label in expected and label in predicted:
                    metrics[label]["TP"] += 1
                elif label not in expected and label in predicted:
                    metrics[label]["FP"] += 1
                elif label in expected and label not in predicted:
                    metrics[label]["FN"] += 1

    exact_match_accuracy = exact_match_count / total_count

    print("\n========== 总体结果 ==========")
    print(f"测试样本数：{total_count}")
    print(f"完全匹配数量：{exact_match_count}")
    print(f"完全匹配准确率：{exact_match_accuracy:.2%}")

    print("\n========== 各意图 Precision / Recall / F1 ==========")

    f1_scores = []

    for label in labels:
        tp = metrics[label]["TP"]
        fp = metrics[label]["FP"]
        fn = metrics[label]["FN"]
    #取出当前标签对应的 TP、FP、FN
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        #Precision = TP / (TP + FP)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        #Recall = TP / (TP + FN)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        #F1 = Precision 和 Recall 的综合指标 =2PR / (P + R)
        f1_scores.append(f1)

        print(
            f"{label}: "
            f"Precision={precision:.2%}, "
            f"Recall={recall:.2%}, "
            f"F1={f1:.2%}"
        )

    macro_f1 = sum(f1_scores) / len(f1_scores)
    #把所有标签的 F1 求平均,不管每个类别样本多少，都平等看待，算一个整体平均表现


    print("\n========== 汇总指标 ==========")
    print(f"Macro-F1：{macro_f1:.2%}")


if __name__ == "__main__":
    evaluate_intent()

#Precision:你报出来的结果里，有多少是真的。
#Recall:本来该找出来的，你找出来多少。
#F1:Precision 和 Recall 的综合分数。
#Macro-F1:所有标签 F1 的平均值。
