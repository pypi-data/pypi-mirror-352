class Setting:
    """日期, 来控制系统时间

    Returns:
        object: 单例模式
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 只有第一次初始化时设置值，后续的初始化调用不会更改实例的值
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.llm = None
            self.debug = None

settings = Setting() # 在模块级别创建唯一实例
