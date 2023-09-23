from dotenv import load_dotenv
import openai
import json
import time
import os

load_dotenv()

question_text = """
You are my English teacher.
Now I want to learn the word "{}".
So I am trying to make a sentence with it.

Check my sentence and give me a score out of 10 like this 8/10

If I have grammar issues or any English issues in my sentence fix it and explain it to me.

My sentence is :

{}
"""

example_text = """
You are my English teacher
I have the '{}' word and I want the following information about it.
I need this information for the root of the word so explain the root of the word and after explain the following things.
1. explain the word's meaning in easy English words.
2. list the word different types of the root (verb, adj, adv and etc) and explain the meaning there.
3. for each type make 5 example in a sentence.
3. for each type give me a score out of 10 on how often use in normal life.
3. if it is a verb give me the 3 different times of the verb
"""


openai.api_key = os.getenv("CHAT_GPT_TOKEN")
chats = {}


class Chat(object):

    def __init__(self):
        self.messages = []

    def ask(self, text):
        self._add_message(text)
        self._call_chat_gpt()
        return self.messages[-1]['content']

    def _call_chat_gpt(self):
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=self.messages
        )
        self._add_message(response.choices[0].message.content, 'assistant')
        return response

    def _add_message(self, text, role='user'):
        self.messages.append({
            'role': role,
            'content': text
        })

    def save(self, name):
        # save messages in json file
        with open(f"./chats/{name}_{time.time()}.json", 'w') as f:
            json.dump(self.messages, f)
