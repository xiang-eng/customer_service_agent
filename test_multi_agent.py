from multi_agent import CoordinatorAgent


class SimpleCache:
    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data


class Memory:
    def __init__(self):
        self.last_product = None
        self.last_order = None
        self.last_intents = None
        self.response_cache = SimpleCache()

    def get_last_product(self):
        return self.last_product

    def update_product(self, product):
        self.last_product = product

    def get_last_order(self):
        return self.last_order

    def update_order(self, order):
        self.last_order = order

        product_name = order.get("product_name") or order.get("product")

        if product_name:
            self.last_product = {
                "name": product_name,
                "product_name": product_name
            }

    def get_last_intents(self):
        return self.last_intents

    def update_intents(self, intents):
        self.last_intents = intents


products = [
    {
        "id": "P1001",
        "name": "华为 Mate 60",
        "product_name": "华为 Mate 60",
        "category": "手机",
        "brand": "华为",
        "aliases": ["华为 Mate 60", "Mate 60", "华为手机", "华为"],
        "price": 6999,
        "stock": 8
    },
    {
        "id": "P1002",
        "name": "小米 14",
        "product_name": "小米 14",
        "category": "手机",
        "brand": "小米",
        "aliases": ["小米 14", "小米14", "小米手机", "小米"],
        "price": 3999,
        "stock": 0
    },
    {
        "id": "P1003",
        "name": "小米智能音箱",
        "product_name": "小米智能音箱",
        "category": "智能音箱",
        "brand": "小米",
        "aliases": ["小米智能音箱", "智能音箱", "音箱"],
        "price": 199,
        "stock": 20
    }
]


orders = [
    {
        "order_id": "O1001",
        "product": "小米智能音箱",
        "product_name": "小米智能音箱",
        "status": "已发货",
        "order_status": "已发货",
        "amount": 199,
        "pay_amount": 199,
        "logistics_company": "顺丰",
        "tracking": "SF123456",
        "tracking_no": "SF123456",
        "tracking_number": "SF123456",
        "logistics_status": "运输中",
        "shipping_status": "运输中"
    },
    {
        "order_id": "O1002",
        "product": "华为 Mate 60",
        "product_name": "华为 Mate 60",
        "status": "待发货",
        "order_status": "待发货",
        "amount": 6999,
        "pay_amount": 6999,
        "logistics_company": "暂无",
        "tracking": "暂无运单",
        "tracking_no": "暂无运单",
        "tracking_number": "暂无运单",
        "logistics_status": "待发货",
        "shipping_status": "待发货"
    }
]


policy = """
售后政策：
1. 未拆封商品支持 7 天无理由退货。
2. 已拆封但无质量问题的商品，不支持无理由退货。
3. 如果商品存在质量问题，支持 15 天内换货。
4. 保修期内非人为损坏，可申请维修。
5. 退款将在退货商品入库并检测通过后 3-7 个工作日原路退回。
"""


memory = Memory()

agent = CoordinatorAgent(
    products=products,
    orders=orders,
    policy=policy,
    memory=memory
)


questions = [
    "你好",
    "华为 Mate 60 多少钱？",
    "华为 Mate 60 有货吗？",
    "小米 14 有货吗？",
    "我的订单 O1001 到哪了？",
    "我的订单 O1001 里的商品可以退货吗？",
    "那退货呢？",
    "那物流呢？"
]


for question in questions:
    print("\n==============================")
    print("用户：", question)

    answer = agent.run(question)

    print("客服：", answer)