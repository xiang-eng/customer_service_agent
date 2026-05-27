# =====================================
# react_agent.py
# 最小可运行 ReAct Agent
# =====================================


# 导入已有工具
from tools import find_product
from tools import find_order
from tools import search_policy


# ==============================
# ReAct Agent 类
# ==============================
class ReActAgent:

    def __init__(self,
                 products,
                 orders,
                 policy):
        """
        初始化 Agent
        """

        self.products = products
        self.orders = orders
        self.policy = policy


    # ==========================
    # Step1 Thought
    # ==========================
    def think(self, question):
        """
        根据问题决定要做什么
        """

        print("Thought: 分析用户问题...")

        if "价格" in question or "多少钱" in question:
            return "product_price"

        if "库存" in question or "有货" in question:
            return "product_stock"

        if "订单" in question or "物流" in question:
            return "order_query"

        if (
            "退货" in question
            or "换货" in question
            or "保修" in question
            or "坏了" in question
        ):
            return "policy_query"

        return "unknown"


    # ==========================
    # Step2 Action
    # ==========================
    def act(
        self,
        action,
        question
    ):
        """
        调工具
        """

        print(
            f"Action: 调用工具 -> {action}"
        )


        if action=="product_price":

            product= find_product(
                question,
                self.products
            )

            return product


        if action=="product_stock":

            product= find_product(
                question,
                self.products
            )

            return product


        if action=="order_query":

            order= find_order(
                question,
                self.orders
            )

            return order


        if action=="policy_query":

            policy_result= search_policy(
                question,
                self.policy
            )

            return policy_result


        return None


    # ==========================
    # Step3 Observation
    # ==========================
    def observe(
        self,
        action,
        tool_result
    ):
        """
        观察工具返回结果
        """

        print(
            "Observation: 工具返回结果"
        )

        if tool_result is None:
            return "工具未找到结果"

        if action=="product_price":

            return (
                f"{tool_result['name']}"
                f"价格为"
                f"{int(tool_result['price'])}元"
            )


        if action=="product_stock":

            return (
                f"{tool_result['name']}"
                f"库存"
                f"{tool_result['stock']}件"
            )


        if action=="order_query":

            return (
                f"订单"
                f"{tool_result['order_id']}"
                f"{tool_result['shipping_status']}"
            )


        if action=="policy_query":

            return tool_result

        return "观察完成"


    # ==========================
    # Step4 Final Answer
    # ==========================
    def final_answer(
        self,
        observation
    ):
        """
        最终回答
        """

        print(
            "Final Answer: 生成最终回复"
        )

        return (
            "客服："
            + observation
        )


    # ==========================
    # 主入口
    # ==========================
    def run(
        self,
        question
    ):
        """
        ReAct主流程
        """

        # Thought
        action = self.think(
            question
        )


        if action=="unknown":
            return "抱歉无法理解问题"


        # Action
        tool_result = self.act(
            action,
            question
        )


        # Observation
        observation = self.observe(
            action,
            tool_result
        )


        # Final Answer
        return self.final_answer(
            observation
        )