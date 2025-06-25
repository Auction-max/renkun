import json
from functools import lru_cache


@lru_cache(maxsize=64)
def get_llm_response(client, *, system_prompt='', few_shot_prompt='',
                     user_prompt='', model='deepseek-chat', temperature=0.2,
                     top_p=0.1, frequency_penalty=0, presence_penalty=0,
                     max_tokens=1024, stream=False):

    messages = []

    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    if few_shot_prompt:
        messages += json.loads(few_shot_prompt)
    if user_prompt:
        messages.append({'role': 'user', 'content': user_prompt})

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=max_tokens,
        messages=messages,
        stream=stream,
    )
    if not stream:
        return resp.choices[0].message.content
    return resp



import streamlit as st
#运行：streamlit run example17.py

from openai import OpenAI
from common import get_llm_response




def get_answer(question:str)->str:
    try:
        client = OpenAI(api_key=api_key,base_url=base_url)
        stream = get_llm_response(client,model=model_name,user_prompt=question,stream=True)
        for chunk in stream:
            yield chunk.choices[0].delta.content or ''
    except:
        return "抱歉，请检查你的api_key哦。"

with st.sidebar:
    api_vendor = st.radio(label ="请选择API供应商",options =["OpenAI","DeepSeek"])
    if api_vendor == "OpenAI":
        base_url = 'https://twapi.openai-hk.com/v1'
        model_options = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
        ]
    elif api_vendor == "DeepSeek":
        base_url = 'https://api.deepseek.com'
        model_options = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
            'deepseek-chat',
        ]
    model_name = st.selectbox(label ="请选择模型",options = model_options)
    api_key = st.text_input(label ="请输入API Key",type ="password")

if 'messages' not in st.session_state:
    st.session_state['messages'] = [('ai','你好，我是你的聊天机器人，我叫小七😀')]

st.write("### 小雨的聊天机器人")

if not api_key:
    st.error("请输入API Key")
    st.stop ()

for role, content in st.session_state['messages']:
    st.chat_message(role).write(content)

user_input = st.chat_input(placeholder ="请输入")
if user_input:
    _, history = st.session_state['messages'][-1]
    st.session_state['messages'].append(('human',user_input))
    st.chat_message("human").write(user_input)
    with st.spinner("小七正在思考中哦~，请耐心等待..."):
        answer = get_answer(f'{history}, {user_input}')
        result = st.chat_message("ai").write_stream(answer)
        st.session_state['messages'].append(('ai',result))
