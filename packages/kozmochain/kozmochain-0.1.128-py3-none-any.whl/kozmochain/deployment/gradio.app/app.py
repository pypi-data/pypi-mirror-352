import os

import gradio as gr

from kozmochain import App

os.environ["OPENAI_API_KEY"] = "sk-xxx"

app = App()


def query(message, history):
    return app.chat(message)


demo = gr.ChatInterface(query)

demo.launch()
