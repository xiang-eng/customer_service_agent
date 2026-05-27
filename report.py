# ================================
# report.py
# 作用：
# 自动输出一份“项目总结报告”
# 把系统模块、实验结果、结论整理成可展示的文本
# ================================


# 从 compare_intent_modes.py 中导入评估函数
# evaluate_mode 可以对“规则版”或“LLM版”做评估，返回指标结果
from compare_intent_modes import evaluate_mode

# 从规则版意图识别模块中导入函数
from intent import classify_intents

# 从 LLM 版意图识别模块中导入函数
from llm_intent import classify_intents_llm


def print_system_modules():#列出你这个项目有哪些模块
    """
    打印系统模块说明

    这个函数不做计算，只负责把你项目里已经实现的模块列出来
    作用类似“系统介绍”
    """

    print("一、系统模块")
    print("- 安全护栏：过滤隐私、违法和超出经营范围的问题")
    print("- 意图识别：支持规则版与 LLM 版两套方案")
    print("- Planner：把识别出的意图转换成任务列表")
    print("- 执行器：分别执行价格、库存、订单、售后任务")
    print("- LLM回答生成：把工具结果整理成自然语言客服回复")
    print("- 回答校验与回退：校验 LLM 输出，不通过则回退模板")
    print("- 缓存：重复问题直接复用历史回答，减少大模型调用")
    print("- 多轮记忆：记录最近商品、订单、意图，支持追问")
    print("- 状态对象与节点式工作流：各节点围绕统一 state 运行")
    print()


def print_experiment_results():#真实调用 compare_intent_modes 里的评估函数
    """                       #拿到规则版和 LLM版的指标
    打印实验结果                  再用报告格式输出

    这里会真实调用 evaluate_mode：
    - 一次评估规则版
    - 一次评估 LLM版

    然后把返回的结果打印成“报告风格”
    """

    print("二、实验结果")

    # =========================
    # 1. 评估规则版
    # =========================
    # mode_name = "规则版"
    # predict_func = classify_intents
    # is_llm = False，表示这不是大模型模式
    rule_result = evaluate_mode("规则版", classify_intents, is_llm=False)

    # =========================
    # 2. 评估 LLM版
    # =========================
    # mode_name = "LLM版"
    # predict_func = classify_intents_llm
    # is_llm = True，表示这是大模型模式，可能有调用失败
    llm_result = evaluate_mode("LLM版", classify_intents_llm, is_llm=True)

    # =========================
    # 3. 把结果整理成简洁报告
    # =========================
    print("\n三、关键指标摘要")
    print(f"- 规则版准确率：{rule_result['accuracy']:.2%}")
    print(f"- 规则版 Macro-F1：{rule_result['macro_f1']:.2%}")
    print(f"- 规则版整体平均耗时：{rule_result['overall_avg_time']:.4f} 秒")

    print(f"- LLM版准确率（成功样本中）：{llm_result['accuracy']:.2%}")
    print(f"- LLM版 Macro-F1（成功样本中）：{llm_result['macro_f1']:.2%}")
    print(f"- LLM版整体平均耗时：{llm_result['overall_avg_time']:.4f} 秒")
    print(f"- LLM版失败率：{llm_result['fail_rate']:.2%}")
    print()

    # 把结果返回出去，后面总结结论要用
    return rule_result, llm_result


def print_conclusion(rule_result, llm_result):#根据实验结果，自动给出项目结论
    """
    根据评估结果，输出项目结论

    参数：
    - rule_result：规则版评估结果字典
    - llm_result：LLM版评估结果字典
    """

    print("四、结论")

    # 结论1：规则版稳定性强
    print("- 规则版在当前封闭测试集上表现稳定，识别速度快，适合固定场景。")

    # 结论2：LLM 版更灵活，但代价更高
    print("- LLM版在成功返回的样本中也能达到较好效果，但更依赖网络和接口稳定性。")

    # 结论3：根据失败率和耗时给出工程结论
    if llm_result["fail_rate"] > 0:
        print("- 当前实验环境下，LLM版存在明显失败率，因此不能单独依赖大模型。")

    # 结论4：推荐架构
    print("- 最适合的工程方案是“LLM 优先 + 规则回退 + 缓存 + 校验”的混合架构。")

    # 结论5：项目价值
    print("- 该项目验证了从规则系统向 Agent 工作流演进的完整过程，具备较强的展示和讲述价值。")
    print()


def print_interview_summary():#输出一段可以直接拿去讲的项目总结
    """
    输出一段可直接在面试中讲述的项目总结

    这样你以后可以直接把这段当作口头表达模板
    """

    print("五、面试讲述摘要")
    print(
        "我做的是一个电商智能客服 Agent 原型系统，"
        "核心流程包括安全护栏、意图识别、任务规划、工具执行、"
        "大模型回答生成、结果校验、缓存和多轮记忆。"
        "我同时实现了规则版和 LLM 版意图识别，并通过测试集做了离线评估。"
        "结果表明，规则版在固定场景下速度和稳定性更好，"
        "LLM 版更灵活，但存在时延和失败率问题。"
        "因此我最终采用了“LLM 优先、失败回退规则版”的混合方案，"
        "在保证系统稳定性的同时，提升了语义理解和回答自然度。"
    )
    print()


def main():#把上面几个模块串起来，按顺序输出一整份报告
    """
    主函数：按顺序打印完整项目报告
    """

    print("========== 智能客服 Agent 项目报告 ==========\n")

    # 1. 打印系统模块
    print_system_modules()

    # 2. 打印实验结果，并拿到返回值
    rule_result, llm_result = print_experiment_results()

    # 3. 根据结果输出结论
    print_conclusion(rule_result, llm_result)

    # 4. 输出面试讲述摘要
    print_interview_summary()

    print("========== 报告结束 ==========")


# Python 程序入口
# 只有直接运行 report.py 时，才会执行 main()
if __name__ == "__main__":
    main()