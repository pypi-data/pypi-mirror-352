"""
pip install openai
"""
from typing import Any, Generator

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk


def create_client(base_url:str, api_key:str):
    return OpenAI(base_url=base_url, api_key=api_key)

def chat(client:OpenAI, model_id:str, user_prompt:str, system_prompt:str=None,
         temperature:float=None, max_tokens:int=None, stream:bool=False)->ChatCompletion | Stream[ChatCompletionChunk]:
    """
    聊天
    :param client: 客户端
    :param user_prompt: 用户提示词
    :param system_prompt: 系统提示词
    :param model_id: 模板ID
    :param temperature: 温度/控制生成随机性（0-1，越高越随机）, 降低温度可以提升速度,
    :param max_tokens: 最大生成 token 数，限制最大生成长度可以提升速度
    :param stream: 是否流输出
    :return:
    """
    message_list = []
    if system_prompt:
        message_list.append({
            "role": "system",
            "content": system_prompt,
        })
    message_list.append({
        "role": "user",
        "content": user_prompt,
    })
    print('\n', '*'*20, '开始聊天', '*'*20)
    return client.chat.completions.create(
        model=model_id,
        messages=message_list,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
    )

def get_response_content(chat_response:ChatCompletion | Stream[ChatCompletionChunk]) \
    -> Generator[str | None, Any, str | None]:
    """
    获取响应内容
    :param chat_response:
    :return:
    """
    if isinstance(chat_response, Stream):
        for chunk in chat_response:
            yield chunk.choices[0].delta.content
    else:
        yield chat_response.choices[0].message.content


if __name__== '__main__':
    # open_client = create_client()
    # response = chat(client=open_client, user_prompt="你好,帮我生成一份关于茶杯的小红书文案", stream=False)
    # for tmp in get_response_content(response):
    #     print(tmp, end='')
    # print(next(get_response_content(response)))
    pass
