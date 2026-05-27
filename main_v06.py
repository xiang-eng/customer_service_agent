import time

from dataloader import load_products, load_orders, load_policy
from logger import write_log
from memory import SessionMemory
from state import AgentState
from workflow import run_workflow


def main():
    products = load_products()
    orders = load_orders()
    policy = load_policy()

    memory = SessionMemory()

    print("智能客服系统已启动。")
    print("你可以问：小米智能音箱多少钱？")
    print("输入 exit 退出系统。")
    print("-" * 40)

    while True:
        question = input("用户：")

        if question.lower() in ["exit", "quit", "退出"]:
            memory.clear()
            print("客服：感谢使用，再见！")
            break

        start_time = time.time()

        # 构造状态对象
        state = AgentState(question, products, orders, policy, memory)

        # 跑工作流
        state = run_workflow(state)
        response = state.final_response

        end_time = time.time()
        response_time = round(end_time - start_time, 4)

        print("客服：" + response)
        print(f"响应耗时：{response_time} 秒")

        write_log(question, response, response_time)

        print("-" * 40)


if __name__ == "__main__":
    main()