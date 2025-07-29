
import os
from openai import AsyncOpenAI
from agents import set_tracing_disabled
from agents import OpenAIChatCompletionsModel,  set_tracing_disabled
from agents import set_default_openai_api

# 设置默认的 OpenAI API 类型为聊天完成
set_default_openai_api("chat_completions")

class Provider:
    def __init__(self, base_url, api_key):
        """
        初始化 Provider 类的实例。

        :param base_url: 服务的基础 URL
        :param api_key: 访问服务所需的 API 密钥
        :raises ValueError: 如果 base_url 或 api_key 为空
        """
        # 检查 base_url 和 api_key 是否为空
        if not base_url or not api_key:
            raise ValueError("base_url 和 api_key 都不能为空")
        self.base_url = base_url
        self.api_key = api_key
        # 初始化 AsyncOpenAI 客户端
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        # 禁用跟踪功能
        set_tracing_disabled(disabled=True)

    def get_client(self):
        """
        获取 AsyncOpenAI 客户端实例。

        :return: 一个元组，包含 AsyncOpenAI 客户端实例和可能的错误信息。
                 如果成功获取客户端，错误信息为 None；否则，客户端实例为 None，错误信息为异常对象。
        """
        try:
            # 这里可以添加更多的检查逻辑，如果有运行时错误可以捕获并返回
            return self.client, None
        except Exception as err:
            return None, err

class ProviderQwen(Provider):
    def __init__(self):
        """
        初始化 ProviderQwen 类的实例。

        :raises ValueError: 如果未设置 QWEN_API_KEY 环境变量
        """
        # 定义 Qwen 服务的基础 URL
        BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        # 从环境变量中获取 QWEN_API_KEY
        API_KEY = os.getenv("QWEN_API_KEY") or ""

        # 检查 BASE_URL 和 API_KEY 是否为空
        if not BASE_URL or not API_KEY:
            raise ValueError("Please set QWEN_API_KEY environment variable.")

        # 调用父类的构造函数进行初始化
        super().__init__(BASE_URL, API_KEY)

class ProviderArk(Provider):
    def __init__(self):
        """
        初始化 ProviderArk 类的实例。

        :raises ValueError: 如果未设置 ARK_API_KEY 环境变量
        """
        # 定义 Ark 服务的基础 URL
        BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
        # 从环境变量中获取 ARK_API_KEY
        API_KEY = os.getenv("ARK_API_KEY") or ""

        # 检查 BASE_URL 和 API_KEY 是否为空
        if not BASE_URL or not API_KEY:
            raise ValueError("Please set ARK_API_KEY environment variable.")

        # 调用父类的构造函数进行初始化
        super().__init__(BASE_URL, API_KEY)

class ProviderDeepSeek(Provider):
    def __init__(self):
        """
        初始化 ProviderDeepSeek 类的实例。

        :raises ValueError: 如果未设置 DEEPSEEK_API_KEY 环境变量
        """
        # 假设 DeepSeek 的基础 URL，你需要根据实际情况修改
        BASE_URL = "https://api.deepseek.com/v1"
        # 从环境变量中获取 DEEPSEEK_API_KEY
        API_KEY = os.getenv("DEEPSEEK_API_KEY") or ""

        # 检查 BASE_URL 和 API_KEY 是否为空
        if not BASE_URL or not API_KEY:
            raise ValueError("Please set DEEPSEEK_API_KEY environment variable.")

        # 调用父类的构造函数进行初始化
        super().__init__(BASE_URL, API_KEY)

class CompletionsModel:
    def __init__(self, model_name, provider):
        """
        初始化 CompletionsModel 类的实例。

        :param model_name: 模型名称
        :param provider: Provider 类的实例，用于提供 OpenAI 客户端
        """
        self.model_name = model_name
        self.provider = provider

    def get_model(self):
        """
        获取 OpenAIChatCompletionsModel 实例。

        :return: OpenAIChatCompletionsModel 实例
        """
        return OpenAIChatCompletionsModel(model=self.model_name, openai_client=self.provider.get_client()[0])

class ModelQwen(CompletionsModel):
    def __init__(self, model_name="qwen-plus"):
        """
        初始化 ModelQwen 类的实例。

        :param model_name: Qwen 模型的名称，默认为 "qwen-plus"
        """
        # 创建 ProviderQwen 实例
        provider = ProviderQwen()
        # 调用父类的构造函数进行初始化
        super().__init__(model_name, provider)

class ModelArk(CompletionsModel):
    def __init__(self, model_name="doubao-1-5-pro-32k-250115"):
        """
        初始化 ModelArk 类的实例。

        :param model_name: Ark 模型的名称，默认为 "doubao-1-5-pro-32k-250115"
        """
        # 创建 ProviderArk 实例
        provider = ProviderArk()
        # 调用父类的构造函数进行初始化
        super().__init__(model_name, provider)

class ModelDeepSeek(CompletionsModel):
    def __init__(self, model_name="deepseek-chat"):
        """
        初始化 ModelDeepSeek 类的实例。

        :param model_name: DeepSeek 模型的名称，默认为 "deepseek-chat"
        """
        # 创建 ProviderDeepSeek 实例
        provider = ProviderDeepSeek()
        # 调用父类的构造函数进行初始化
        super().__init__(model_name, provider)

if __name__ == "__main__":
    import asyncio
    from agents import Agent, Runner, RunConfig

    def get_models():
        """
        获取所有可用的模型实例。

        :return: 包含所有可用模型实例的列表
        """
        models = []
        models.append(ModelArk().get_model())
        models.append(ModelQwen("qwen-max").get_model())
        models.append(ModelDeepSeek().get_model())
        models.append(ModelDeepSeek("deepseek-reasoner").get_model())
        return models

    def new_agent(model):
        """
        创建一个新的 Agent 实例。

        :param model: 用于 Agent 的模型实例
        :return: 新创建的 Agent 实例
        """
        agent = Agent(
            name="Assistant",
            instructions="You are helpful assistant",
            model=model,
        )
        return agent

    async def main():
        """
        主异步函数，用于测试不同模型的 Agent。
        """
        # 获取所有可用的模型实例
        models = get_models()
        for model in models:
            # 创建新的 Agent 实例
            agent = new_agent(model)
            # 运行 Agent 并获取结果
            result = await Runner.run(agent, "你是谁？")
            print(result.final_output)

    # 运行主异步函数
    asyncio.run(main())