"""
pip install ollama
"""
from typing import Generator, Any, Optional

from ollama import Client


def create_client(ollama_url):
    return Client(host=ollama_url)

def chat(client:Client,  model_id:str, user_prompt:str, system_prompt:str=None,
         stream:bool=False,think: Optional[bool] = None, is_json:bool=False):
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
    print('\n','*' * 20, '开始聊天', '*' * 20)
    messages= tuple(message_list)
    return client.chat(model=model_id, messages=messages, stream=stream, think=think, format='json' if is_json else '')

def get_response_content(chat_response)-> Generator[str | None, Any, str | None]:
    """
    获取响应内容
    :param chat_response:
    :return:
    """
    if isinstance(chat_response, Generator):
        for chunk in chat_response:
            yield chunk.message.content
    else:
        yield chat_response.message.content


if __name__ == '__main__':
    # o_client = create_client()
    # response = chat(o_client, '为什么天空是蓝色的？', stream=True, think=True)
    # for tmp in get_response_content(response):
    #     print(tmp, end='')
    # print(next(get_response_content(response)))
    pass