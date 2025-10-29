安装 Google GenAI SDK
Python
JavaScript
Go
Java
Apps 脚本
使用 Python 3.9 及更高版本，通过以下 pip 命令安装 google-genai 软件包：


pip install -q -U google-genai
提交第一个请求
以下示例使用 generateContent 方法，通过 Gemini 2.5 Flash 模型向 Gemini API 发送请求。

如果您将 API 密钥设置为环境变量 GEMINI_API_KEY，那么在使用 Gemini API 库时，客户端会自动获取该密钥。否则，您需要在初始化客户端时将 API 密钥作为实参传递。

请注意，Gemini API 文档中的所有代码示例都假定您已设置环境变量 GEMINI_API_KEY。

Python

from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)
