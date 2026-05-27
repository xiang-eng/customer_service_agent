'''规则版评估
LLM版评估
输出两组指标'''
import csv
import os
import time

# 规则版意图识别函数
from intent import classify_intents

# LLM 版意图识别函数
from llm_intent import classify_intents_llm


# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 测试集文件路径
TEST_FILE = os.path.join(BASE_DIR, "data", "test_intents.csv")


def parse_intents(intent_text):
    """
    把 CSV 里的字符串标签转成集合（set）

    例如：
    "price_query|stock_query"
    转成：
    {"price_query", "stock_query"}

    为什么要转成 set？
    因为后面比较预测结果和标准答案时，集合更方便比较。
    """
    return set(intent_text.strip().split("|"))


def evaluate_mode(mode_name, predict_func, is_llm=False):
    """
    评估某一种意图识别模式

    参数：
    - mode_name: 模式名称，比如 "规则版" / "LLM版"
    - predict_func: 预测函数，比如 classify_intents 或 classify_intents_llm
    - is_llm: 是否是 LLM 模式
      因为 LLM 模式可能会出现接口超时 / 调用失败，
      所以要额外统计失败次数

    返回：
    一个字典，里面保存这个模式的各种指标
    """

    # =========================
    # 一、基础计数器
    # =========================

    # 总样本数（测试集中一共有多少问题）
    total_count = 0

    # 完全匹配数量（预测意图和标准答案完全一致的样本数）
    exact_match_count = 0

    # 累计耗时（所有样本总共用了多少秒）
    total_time = 0.0

    # 成功完成识别的样本数
    # 对规则版来说，基本上总是成功
    # 对 LLM 版来说，可能会有超时失败
    success_count = 0

    # 失败调用数（主要给 LLM 用）
    fail_count = 0

    # =========================
    # 二、每类意图的 TP / FP / FN
    # =========================
    # 这些是为了后面计算 Precision / Recall / F1

    labels = [
        "price_query",
        "stock_query",
        "policy_query",
        "order_query",
        "general_query",
        "unknown_query"
    ]

    # metrics 的结构示例：
    # {
    #   "price_query": {"TP": 0, "FP": 0, "FN": 0},
    #   ...
    # }
    metrics = {label: {"TP": 0, "FP": 0, "FN": 0} for label in labels}

    print(f"\n========== {mode_name} 评估明细 ==========")

    # =========================
    # 三、逐条读取测试集并评估
    # =========================
    with open(TEST_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_count += 1

            # 当前问题
            question = row["question"]

            # 标准答案（集合）
            expected = parse_intents(row["expected_intents"])

            # 记录本条样本开始时间
            start_time = time.time()

            # 调用预测函数
            predicted_raw = predict_func(question)

            # 记录本条样本结束时间
            end_time = time.time()

            # 计算本条耗时
            elapsed = end_time - start_time

            # 不管成功失败，整体耗时都要累加
            total_time += elapsed

            # =========================
            # 四、处理 LLM 调用失败的情况
            # =========================
            # 约定：
            # 如果 LLM 调用失败，llm_intent.py 会返回 None
            # 这种情况我们不把它算成 "unknown_query"
            # 因为这不是模型“识别成 unknown”，而是“根本没成功返回”
            if predicted_raw is None:
                fail_count += 1

                print(f"\n问题：{question}")
                print(f"标准意图：{sorted(expected)}")
                print("预测意图：LLM 调用失败（本条不纳入识别能力评估）")
                print(f"耗时：{elapsed:.4f} 秒")

                # 直接跳过，不参与 TP / FP / FN 和准确率计算
                continue

            # 能走到这里，说明本条样本预测成功
            success_count += 1

            # 把预测结果转成集合
            predicted = set(predicted_raw)

            # 是否“完全匹配”
            # 例如：
            # 标准：{"price_query", "stock_query"}
            # 预测：{"price_query", "stock_query"}
            # 才算 True
            is_exact_match = expected == predicted

            if is_exact_match:
                exact_match_count += 1

            print(f"\n问题：{question}")
            print(f"标准意图：{sorted(expected)}")
            print(f"预测意图：{sorted(predicted)}")
            print(f"是否完全正确：{is_exact_match}")
            print(f"耗时：{elapsed:.4f} 秒")

            # =========================
            # 五、更新 TP / FP / FN
            # =========================
            for label in labels:
                # TP：这个标签本来就该有，预测也有
                if label in expected and label in predicted:
                    metrics[label]["TP"] += 1

                # FP：这个标签本来不该有，但预测出来了
                elif label not in expected and label in predicted:
                    metrics[label]["FP"] += 1

                # FN：这个标签本来该有，但没预测出来
                elif label in expected and label not in predicted:
                    metrics[label]["FN"] += 1

    # =========================
    # 六、输出总体结果
    # =========================

    print(f"\n========== {mode_name} 总体结果 ==========")
    print(f"测试样本总数：{total_count}")
    print(f"成功识别样本数：{success_count}")
    print(f"失败调用数：{fail_count}")

    # 对 LLM 来说，这个失败率很重要
    fail_rate = fail_count / total_count if total_count > 0 else 0
    print(f"失败率：{fail_rate:.2%}")

    # 这里分两种平均耗时：
    # 1. overall_avg_time：所有样本（包括失败）平均耗时
    # 2. success_avg_time：只有成功样本的平均耗时
    overall_avg_time = total_time / total_count if total_count > 0 else 0
    print(f"整体平均单条耗时：{overall_avg_time:.4f} 秒")

    # 如果一条都没成功，那后面没法算准确率 / F1
    if success_count == 0:
        print("没有成功识别的样本，无法计算准确率和 F1。")
        return {
            "accuracy": 0,
            "macro_f1": 0,
            "overall_avg_time": overall_avg_time,
            "success_avg_time": 0,
            "fail_rate": fail_rate,
            "success_count": success_count,
            "fail_count": fail_count
        }

    # 只基于成功样本计算“完全匹配准确率”
    exact_match_accuracy = exact_match_count / success_count

    print(f"完全匹配数量（成功样本中）：{exact_match_count}")
    print(f"完全匹配准确率（成功样本中）：{exact_match_accuracy:.2%}")

    # =========================
    # 七、计算各类意图的 Precision / Recall / F1
    # =========================
    f1_scores = []

    print(f"\n========== {mode_name} 各意图 Precision / Recall / F1 ==========")

    for label in labels:
        tp = metrics[label]["TP"]
        fp = metrics[label]["FP"]
        fn = metrics[label]["FN"]

        # Precision = TP / (TP + FP)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0

        # Recall = TP / (TP + FN)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        # F1 = 2PR / (P + R)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        f1_scores.append(f1)

        print(
            f"{label}: "
            f"Precision={precision:.2%}, "
            f"Recall={recall:.2%}, "
            f"F1={f1:.2%}"
        )

    # Macro-F1：所有类别 F1 的平均值
    macro_f1 = sum(f1_scores) / len(f1_scores)

    # 成功样本平均耗时
    # 这里为了简单，用“整体总耗时 / 成功样本数”
    # 因为失败样本也占用了时间，所以这个指标会偏大一点
    # 但能反映真实成本
    success_avg_time = total_time / success_count if success_count > 0 else 0

    print(f"\n========== {mode_name} 汇总指标 ==========")
    print(f"Macro-F1：{macro_f1:.2%}")
    print(f"成功样本平均耗时：{success_avg_time:.4f} 秒")

    return {
        "accuracy": exact_match_accuracy,
        "macro_f1": macro_f1,
        "overall_avg_time": overall_avg_time,
        "success_avg_time": success_avg_time,
        "fail_rate": fail_rate,
        "success_count": success_count,
        "fail_count": fail_count
    }


def main():
    """
    主函数：
    先评估规则版，再评估 LLM 版，最后输出对比结果
    """

    # 规则版评估
    rule_result = evaluate_mode("规则版", classify_intents, is_llm=False)

    # LLM 版评估
    llm_result = evaluate_mode("LLM版", classify_intents_llm, is_llm=True)

    # =========================
    # 八、最终对比总结
    # =========================
    print("\n================ 最终对比 ================")

    print(
        f"规则版："
        f"准确率={rule_result['accuracy']:.2%}，"
        f"Macro-F1={rule_result['macro_f1']:.2%}，"
        f"整体平均耗时={rule_result['overall_avg_time']:.4f} 秒"
    )

    print(
        f"LLM版："
        f"准确率={llm_result['accuracy']:.2%}，"
        f"Macro-F1={llm_result['macro_f1']:.2%}，"
        f"整体平均耗时={llm_result['overall_avg_time']:.4f} 秒，"
        f"失败率={llm_result['fail_rate']:.2%}"
    )

    print("\n================ 结果解读建议 ================")
    print("1. 规则版适合固定场景，速度快、稳定、不依赖网络。")
    print("2. LLM版更灵活，但在当前网络环境下容易超时，导致失败率较高。")
    print("3. 如果项目追求线上稳定性，建议采用“LLM 优先 + 规则回退”的混合方案。")


if __name__ == "__main__":
    main()