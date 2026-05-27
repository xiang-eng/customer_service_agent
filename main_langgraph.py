# ==========================================
# main_langgraph.py
# 作用：
# 用 LangGraph 版本工作流启动智能客服系统
#
# 和 main_v06.py 类似，
# 只是底层调用换成了 langgraph_workflow
# ==========================================


# -----------------------------
# 导入时间模块
# 用来统计响应耗时
# -----------------------------
import time


# -----------------------------
# 导入基础数据加载函数
# -----------------------------
from dataloader import (
    load_products,
    load_orders,
    load_policy
)


# -----------------------------
# 导入会话记忆对象
# 用于多轮对话上下文
# -----------------------------
from memory import SessionMemory


# -----------------------------
# 导入 LangGraph 工作流
# -----------------------------
from langgraph_workflow import run_langgraph_workflow


def main():
    """
    主程序入口
    """

    # -----------------------------
    # 加载商品数据
    # -----------------------------
    products = load_products()

    # -----------------------------
    # 加载订单数据
    # -----------------------------
    orders = load_orders()

    # -----------------------------
    # 加载售后政策
    # -----------------------------
    policy = load_policy()


    # -----------------------------
    # 初始化会话记忆
    # 多轮对话靠它保存上下文
    # -----------------------------
    memory = SessionMemory()


    # -----------------------------
    # 欢迎信息
    # -----------------------------
    print("智能客服 LangGraph 版本已启动。")
    print("你可以问：小米智能音箱多少钱？")
    print("输入 exit 退出系统。")
    print("-" * 40)


    # =============================
    # 主循环
    # =============================
    while True:

        # 用户输入
        question = input("用户：").strip()


        # 输入 exit 退出
        if question.lower() == "exit":
            print("客服：感谢使用，再见！")
            break


        # 记录开始时间
        start_time = time.time()


        # =========================
        # 构造 LangGraph 输入状态
        # =========================
        state = {
            "question": question,

            "products": products,
            "orders": orders,
            "policy": policy,

            "memory": memory,

            # trace用于记录节点轨迹
            "trace": [],

            # 初始化空字段
            "responses": [],
            "tasks": [],
            "intents": [],
        }


        # =========================
        # 调用 LangGraph 工作流
        # =========================
        result_state = run_langgraph_workflow(
            state
        )


        # -------------------------
        # 拿最终回答
        # -------------------------
        response = result_state["final_response"]


        # 输出客服回复
        print(f"客服：{response}")


        # 记录耗时
        end_time = time.time()

        print(
            f"响应耗时："
            f"{round(end_time-start_time,4)} 秒"
        )

        print("-" * 40)


# -----------------------------
# 程序入口
# -----------------------------
if __name__ == "__main__":
    main()