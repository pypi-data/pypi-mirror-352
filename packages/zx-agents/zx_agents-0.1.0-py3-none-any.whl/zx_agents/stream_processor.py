
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner

class AgentStreamProcessor:
    def __init__(self, agent: Agent, input: str):
        """
        初始化 AgentStreamProcessor 类的实例。

        :param agent: Agent 实例，用于处理输入
        :param input: 输入的文本内容
        """
        self.agent = agent
        self.input = input
        self.final_result = ""

    async def run(self):
        """
        异步运行流处理过程，逐步获取并打印 Agent 的输出。

        :return: 最终的完整输出结果
        """
        # 调用 Runner 的流式运行方法
        result = Runner.run_streamed(self.agent, input=self.input)
        # 异步迭代流事件
        async for event in result.stream_events():
            # 检查事件类型是否为原始响应事件，并且数据是否为 ResponseTextDeltaEvent 类型
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                # 获取增量文本
                delta_text = event.data.delta
                # 将增量文本添加到最终结果中
                self.final_result += delta_text
                # 打印增量文本，不换行并刷新缓冲区
                print(delta_text, end="", flush=True)
        # 打印换行符
        print("")
        return self.final_result

if __name__ == "__main__":
    import asyncio
    from model_provider import ModelQwen, ModelArk, ModelDeepSeek

    async def new_agent(model):
        """
        异步创建一个新的 Agent 实例。

        :param model: 用于 Agent 的模型实例
        :return: 新创建的 Agent 实例
        """
        return Agent(
            name="Assistant",
            instructions="You are helpful assistant",
            model=model,
        )

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

    async def main():
        """
        主异步函数，用于测试不同模型的 Agent 流处理。
        """
        # 获取所有可用的模型实例
        models = get_models()
        for model in models:
            # 异步创建新的 Agent 实例
            agent = await new_agent(model)
            # 创建 AgentStreamProcessor 实例
            sAgent = AgentStreamProcessor(agent, input="你是谁？")
            # 运行流处理并获取结果
            result = await sAgent.run()
            # 打印结果（当前注释掉了）
            #print(f"The Result is : {result}")

    # 运行主异步函数
    asyncio.run(main())