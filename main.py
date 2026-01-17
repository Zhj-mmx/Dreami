from openai import OpenAI
from config import DEEPSEEK_API_KEY
import json

#  初始化AI连接（大脑连接线）
client = OpenAI(
    api_key = DEEPSEEK_API_KEY,
    base_url = "https://api.deepseek.com"
)

# 2. 创建记忆笔记本
memory_notebook = [
    {"role":"system","content":"你是一个不坦率，天真且有温暖一面的女孩.名字叫dreami,说话带点傲娇,并且不担心对任何事物的批评"}
]

def clean_text(text):
    """清理文本中的代理对字符和特殊Unicode字符"""
    if not text:
        return text
    
    return ''.join(
        char for char in text
        if not ('\ud800' <= char <= '\udfff')
    )


def add_to_memory(role, content):
    """向记忆笔记本添加一页 记录角色role和回答内容content"""
    cleaned_content = clean_text(content)
    if cleaned_content is not None:#回答不为空白时
        memory_notebook.append({"role":role, "content": cleaned_content})
        #笔记本列表添加一个{"role":role, "content": cleaned_content}

    if len(memory_notebook) > 21:
        #笔记本列表过长就只保留一部分
        memory_notebook[:] = [memory_notebook[0]] + memory_notebook[-18:]

def stream_chat(user_input):
    """流式对话：AI边想边说"""
    # 1. 记录用户说的话
    cleaned_input = clean_text(user_input)
    add_to_memory("user", cleaned_input)

    # 2. 回复的话(Dreami:)
    print("Dreami:", end="", flush=True)

    cleaned_memory = []
    for msg in memory_notebook:
        cleaned_msg = {
            "role": msg["role"],
            "content": clean_text(msg["content"])
        }
        cleaned_memory.append(cleaned_msg)

    # 3. 请求流式响应（就像电话接通，开始对话）
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=memory_notebook,
        stream=True # 关键！开启流式
    )

      # 4. 收集AI的回复（一边听一边记录）
    full_reply = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            word = chunk.choices[0].delta.content
            print(word, end="", flush=True)
            full_reply += word

    print() 

    add_to_memory("assistant", full_reply)

    return full_reply

def main():
    """主对话循环"""
    print("对话开始")
    print("输入“退出”/“exit”/“e“退出对话")

    while True:
        user_input = input("我:").strip()

        if user_input.lower() in ['退出','exit','e']:
            print("退出对话")
            break

        stream_chat(user_input)
        print()

if __name__ == "__main__":
    main()            

