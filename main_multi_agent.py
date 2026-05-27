# =====================================
# main_multi_agent.py
# 作用：
# 启动 Multi-Agent 版本客服系统
# =====================================

import time

from dataloader import load_products, load_orders, load_policy
from memory import SessionMemory
from multi_agent import CoordinatorAgent


def main():
    """
    主程序入口
    """

    # 加载商品数据
    products = load_products()

    # 加载订单数据
    orders = load_orders()

    # 加载售后政策
    policy = load_policy()

    # 初始化会话记忆
    memory = SessionMemory()

    # 初始化总协调 Agent
    agent = CoordinatorAgent(
        products=products,
        orders=orders,
        policy=policy,
        memory=memory
    )

    print("智能客服 Multi-Agent 版本已启动。")
    print("你可以问：小米智能音箱多少钱？")
    print("输入 exit 退出系统。")
    print("-" * 40)

    while True:
        question = input("用户：").strip()

        if question.lower() in ["exit", "quit", "退出"]:
            print("客服：感谢使用，再见！")
            break

        start_time = time.time()

        response = agent.run(question)

        end_time = time.time()

        print("客服：" + response)
        print(f"响应耗时：{round(end_time - start_time, 4)} 秒")
        print("-" * 40)


if __name__ == "__main__":
    main()