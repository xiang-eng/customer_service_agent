class AgentState:
    """
    Agent 状态对象
    用来保存一次问题处理过程中的所有关键信息
    """

    def __init__(self, question, products, orders, policy, memory):
        # 用户当前问题
        self.question = question

        # 数据源
        self.products = products
        self.orders = orders
        self.policy = policy

        # 会话记忆
        self.memory = memory

        # 中间状态
        self.intents = []
        self.tasks = []
        self.responses = []

        # 控制状态
        self.should_stop = False
        self.final_response = None
        self.is_safe = True
        self.guard_message = None

        # 调试轨迹
        self.trace = []

    def add_trace(self, message):
        """记录调试轨迹"""
        self.trace.append(message)
        print(message)

    def add_response(self, text):
        """添加一段回答"""
        self.responses.append(text)

    def get_final_response(self):
        """把多个回答片段拼接成最终回答"""
        return "\n".join(self.responses)