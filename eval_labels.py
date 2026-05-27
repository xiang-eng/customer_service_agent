# =====================================
# eval_labels.py
# 作用：
# 评估 IntentAgent / PlannerAgent 的标签效果
# =====================================

from sklearn.metrics import precision_recall_fscore_support

from intent import classify_intents
from planner_agentic import build_agentic_tasks


# =========================
# 1. 人工标注测试集
# =========================
# expected_intents 是标准意图标签
# expected_tasks 是标准任务标签
test_cases = [
    {
        "question": "小米智能音箱多少钱",
        "expected_intents": ["price_query"],
        "expected_tasks": ["price_task"]
    },
    {
        "question": "华为门铃还有货吗",
        "expected_intents": ["stock_query"],
        "expected_tasks": ["stock_task"]
    },
    {
        "question": "订单 O1001 到哪了",
        "expected_intents": ["order_query"],
        "expected_tasks": ["order_task"]
    },
    {
        "question": "可以退货吗",
        "expected_intents": ["policy_query"],
        "expected_tasks": ["policy_task"]
    },
    {
        "question": "可以换吗",
        "expected_intents": ["policy_query"],
        "expected_tasks": ["policy_task"]
    },
    {
        "question": "小米智能音箱多少钱？订单 O1001 到哪了？可以退货吗？",
        "expected_intents": ["price_query", "order_query", "policy_query"],
        "expected_tasks": ["price_task", "order_task", "policy_task"]
    },
    {
        "question": "订单 O1001 里的商品可以退货吗",
        "expected_intents": ["order_query", "policy_query"],
        "expected_tasks": ["order_task", "policy_task"]
    },
    {
        "question": "你好",
        "expected_intents": ["general_query"],
        "expected_tasks": ["general_task"]
    },
    {
        "question": "今天天气怎么样",
        "expected_intents": ["unknown_query"],
        "expected_tasks": ["unknown_task"]
    }
]


# =========================
# 2. 所有标签
# =========================
intent_labels = [
    "price_query",
    "stock_query",
    "order_query",
    "policy_query",
    "general_query",
    "unknown_query"
]

task_labels = [
    "price_task",
    "stock_task",
    "order_task",
    "policy_task",
    "general_task",
    "unknown_task"
]


def to_multi_hot(labels, all_labels):
    """
    把标签列表转成 0/1 向量

    例如：
    labels = ["price_query", "policy_query"]

    all_labels = [
        "price_query",
        "stock_query",
        "order_query",
        "policy_query"
    ]

    结果：
    [1, 0, 0, 1]
    """

    return [
        1 if label in labels else 0
        for label in all_labels
    ]


def evaluate(name, y_true, y_pred, labels):
    """
    计算 Precision / Recall / F1
    """

    print(f"\n========== {name} 评估结果 ==========")

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        average=None,
        zero_division=0
    )

    for i, label in enumerate(labels):
        print(
            f"{label}: "
            f"Precision={precision[i]:.2f}, "
            f"Recall={recall[i]:.2f}, "
            f"F1={f1[i]:.2f}, "
            f"Support={support[i]}"
        )

    micro = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="micro",
        zero_division=0
    )

    macro = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="macro",
        zero_division=0
    )

    print("\n总体指标：")
    print(f"Micro Precision: {micro[0]:.2f}")
    print(f"Micro Recall: {micro[1]:.2f}")
    print(f"Micro F1: {micro[2]:.2f}")
    print(f"Macro Precision: {macro[0]:.2f}")
    print(f"Macro Recall: {macro[1]:.2f}")
    print(f"Macro F1: {macro[2]:.2f}")


def main():
    """
    主评估流程
    """

    intent_true = []
    intent_pred = []

    task_true = []
    task_pred = []

    exact_intent_correct = 0
    exact_task_correct = 0

    for case in test_cases:
        question = case["question"]

        expected_intents = case["expected_intents"]
        expected_tasks = case["expected_tasks"]

        # 1. 预测意图
        predicted_intents = classify_intents(question)

        # 2. 预测任务
        predicted_tasks = build_agentic_tasks(
            question,
            predicted_intents
        )

        # 3. 打印明细
        print("\n问题：", question)
        print("标准意图：", expected_intents)
        print("预测意图：", predicted_intents)
        print("标准任务：", expected_tasks)
        print("预测任务：", predicted_tasks)

        # 4. 完全匹配统计
        if set(expected_intents) == set(predicted_intents):
            exact_intent_correct += 1

        if set(expected_tasks) == set(predicted_tasks):
            exact_task_correct += 1

        # 5. 转成 multi-hot
        intent_true.append(
            to_multi_hot(expected_intents, intent_labels)
        )

        intent_pred.append(
            to_multi_hot(predicted_intents, intent_labels)
        )

        task_true.append(
            to_multi_hot(expected_tasks, task_labels)
        )

        task_pred.append(
            to_multi_hot(predicted_tasks, task_labels)
        )

    total = len(test_cases)

    print("\n========== 完全匹配结果 ==========")
    print(f"意图完全匹配率：{exact_intent_correct / total:.2%}")
    print(f"任务完全匹配率：{exact_task_correct / total:.2%}")

    evaluate(
        "意图标签",
        intent_true,
        intent_pred,
        intent_labels
    )

    evaluate(
        "任务标签",
        task_true,
        task_pred,
        task_labels
    )


if __name__ == "__main__":
    main()