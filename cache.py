class SimpleCache:
    """
    简单缓存类
    用字典保存 key -> value
    """

    def __init__(self):
        self.store = {}#创建字典存储区

    def get(self, key):
        """根据 key 取缓存"""
        return self.store.get(key)#去 store 这个字典里找 key 对应的值，并返回

    def set(self, key, value):#定义一个方法，用来往缓存里写入数据
        """写入缓存"""
        self.store[key] = value

    def clear(self):
        """清空缓存"""
        self.store.clear()