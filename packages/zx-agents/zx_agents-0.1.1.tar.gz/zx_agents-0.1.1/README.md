# zx_agents

这是 `zx_agents` 包的简介，介绍该包的功能和使用方法。

## 安装
```bash
pip install zx_agentsfrom zx_agents import agent_stream_processor, provider_model, test_agent

使用前置条件

设置/etc/environment,设置
ARK_API_KEY       #火山引擎
QWEN_API_KEY      #阿里通义
DEEPSEEK_API_KEY  #DeepSeek 

## 使用示例

from zx_agents import agent_stream_processor, provider_model, test_agent

model_ark = provider_model.ModelArk().get_model()
