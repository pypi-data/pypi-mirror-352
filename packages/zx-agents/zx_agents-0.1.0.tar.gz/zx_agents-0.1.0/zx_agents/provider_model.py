
import os
from openai import AsyncOpenAI
from agents import set_tracing_disabled
from agents import OpenAIChatCompletionsModel,  set_tracing_disabled


from agents import set_default_openai_api

set_default_openai_api("chat_completions")

class Provider:
    def __init__(self, base_url, api_key):
        """
        初始化 Provider 类的实例。

        :param base_url: 服务的基础 URL
        :param api_key: 访问服务所需的 API 密钥
        """
        if not base_url or not api_key:
            raise ValueError("base_url 和 api_key 都不能为空")
        self.base_url = base_url
        self.api_key = api_key
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        set_tracing_disabled(disabled=True)

    def get_client(self):
        """获取 AsyncOpenAI 客户端实例"""
        try:
            # 这里可以添加更多的检查逻辑，如果有运行时错误可以捕获并返回
            return self.client, None
        except Exception as err:
            return None, err

class ProviderQwen(Provider):
    def __init__(self):
        BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        API_KEY = os.getenv("QWEN_API_KEY") or ""

        if not BASE_URL or not API_KEY:
            raise ValueError("Please set QWEN_API_KEY environment variable.")

        super().__init__(BASE_URL, API_KEY)

class ProviderArk(Provider):
    def __init__(self):
        BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
        API_KEY = os.getenv("ARK_API_KEY") or ""

        if not BASE_URL or not API_KEY:
            raise ValueError("Please set ARK_API_KEY environment variable.")

        super().__init__(BASE_URL, API_KEY)

class ProviderDeepSeek(Provider):
    def __init__(self):
        # 假设 DeepSeek 的基础 URL 和环境变量名，你需要根据实际情况修改
        BASE_URL = "https://api.deepseek.com/v1"
        API_KEY = os.getenv("DEEPSEEK_API_KEY") or ""

        if not BASE_URL or not API_KEY:
            raise ValueError("Please set DEEPSEEK_API_KEY environment variable.")

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
        return OpenAIChatCompletionsModel(model=self.model_name, openai_client=self.provider.get_client()[0])


class ModelQwen(CompletionsModel):
    def __init__(self, model_name="qwen-plus"):
        provider = ProviderQwen()
        super().__init__(model_name, provider)


class ModelArk(CompletionsModel):
    def __init__(self, model_name="doubao-1-5-pro-32k-250115"):
        provider = ProviderArk()
        super().__init__(model_name, provider)

class ModelDeepSeek(CompletionsModel):
    def __init__(self, model_name="deepseek-chat"):
        provider = ProviderDeepSeek()
        super().__init__(model_name, provider)

if __name__ == "__main__":
    import asyncio
    from agents import Agent, Runner,RunConfig
   

    def get_models():
        models = []
        models.append(ModelArk().get_model())
        models.append(ModelQwen("qwen-max").get_model())
        models.append(ModelDeepSeek().get_model())
        models.append(ModelDeepSeek("deepseek-reasoner").get_model())
        return models

    def new_agent(model):
        agent = Agent(
            name="Assistant",
            instructions="You are helpful assistant",
            model=model,
        )
        return agent
    async def main():
        models = get_models()
        for model in models:
            agent = new_agent(model)
            result = await Runner.run(agent, "你是谁？")
            print(result.final_output)
    asyncio.run(main())
    