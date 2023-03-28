import gradio as gr
import json
import asyncio
import os
from EdgeGPT import Chatbot, ConversationStyle
import re

#read cookie from local file
# with open('./cookies.json', 'r') as f:
#     cookies = json.load(f)
#如果你是选择读取仓库内的cookie.json文件，那么不需要再向函数内传递cookies参数
# 也可以删去gr.Tab("Cookies"):这一界面对应的代码
async def get_model_reply(prompt,style,cookies,context=[]):
    # combines the new question with a previous context
    context += [prompt]
    cookies = json.loads(cookies)
    # given the most recent context (4096 characters)
    # continue the text up to 2048 tokens ~ 8192 charaters
    bot = Chatbot(cookies=cookies)
    prompt2='\n\n'.join(context)[:4096]
    raw_data = await bot.ask(prompt2, conversation_style=style)
    await bot.close()
    #print(raw_data)
    try:
        try:
            response = raw_data["item"]["messages"][1]["text"]
        except:
            response = raw_data["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
        response = re.sub(r'\^', '', response)
        response = response.rstrip()
        context += [response]

    # list of (user, bot) responses. We will use this format later
        responses = [(u, b) for u, b in zip(context[::2], context[1::2])]
        return responses, context
    except:
        try:
            if raw_data["item"]["throttling"]["numUserMessagesInConversation"] > raw_data["item"]["throttling"]["maxNumUserMessagesInConversation"]:
                response="> **Oops, I think we've reached the end of this conversation. Please reset the bot!**"
                context += [response]

                # list of (user, bot) responses. We will use this format later
                responses = [(u, b) for u, b in zip(context[::2], context[1::2])]
                return responses, context
                
        except:    
            if raw_data["item"]["result"]["value"] == "Throttled":
                response="> **Error: We're sorry, but you've reached the maximum number of messages you can send to Bing in a 24-hour period. Check back later!**"
                context += [response]

                # list of (user, bot) responses. We will use this format later
                responses = [(u, b) for u, b in zip(context[::2], context[1::2])]
                return responses, context
# query = 'Which is the largest country by area in the world?'
# style="precise"
# responses, context =asyncio.run(get_model_reply(query,style,context=[]))
#
# print(' ' + responses[-1][0])
# print(' ' + responses[-1][1])
with gr.Blocks() as dialog_app:
    with gr.Tab("Cookies"):
        cookies = gr.Textbox(lines=2, label="输入bing.com中的cookies")
    with gr.Tab("New Bing Chat"):
        gr.Markdown("# A Simple Web to use New Bing Without Magic")
        chatbot = gr.Chatbot()
        state = gr.State([])
        markdown = gr.Markdown(label="Output")

        with gr.Row():
            inputs = gr.Textbox(
                label="输入问题",
                placeholder="Enter text and press enter"
            )
            style = gr.Dropdown(label="回答倾向", choices=["creative", "balanced", "precise"], multiselect=False,
                                value="balanced", type="value")

        inputs.submit(get_model_reply, [inputs, style, cookies, state], [chatbot, state])
        send = gr.Button("Send")
        send.click(get_model_reply, [inputs, style, cookies, state], [chatbot, state])

# launches the app in a new local port
dialog_app.launch()
# 为网站设置密码防止滥用
# dialog_app.launch(auth=("admin", "pass1234"))
