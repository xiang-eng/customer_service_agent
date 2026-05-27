from cache import SimpleCache


class SessionMemory:
    """
    会话记忆类
    用来记录当前会话中最近提到的商品、订单、意图，以及回答缓存
    """

    def __init__(self):
        # 最近一次提到的商品
        self.last_product = None

        # 最近一次提到的订单
        self.last_order = None

        # 最近一次识别出的意图列表
        self.last_intents = None

        # 回答缓存
        self.response_cache = SimpleCache()

    def update_product(self, product):
        """更新最近商品"""
        if product is not None:
            self.last_product = product

    def update_order(self, order):
        """更新最近订单"""
        if order is not None:
            self.last_order = order

    def update_intents(self, intents):
        """更新最近意图"""
        if intents:
            self.last_intents = intents

    def get_last_product(self):
        """获取最近商品"""
        return self.last_product

    def get_last_order(self):
        """获取最近订单"""
        return self.last_order

    def get_last_intents(self):
        """获取最近意图"""
        return self.last_intents

    def clear(self):
        """清空记忆和缓存"""
        self.last_product = None
        self.last_order = None
        self.last_intents = None
        self.response_cache.clear()