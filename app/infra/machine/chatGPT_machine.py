import openai
import configparser
import os

#openai.api_key = "" 

dialogs = ""
messages = []


class ChatMachine:

    def __init__(self, key="local"):
        self.openai = openai
        config = configparser.ConfigParser()
        key = None
        key = os.getenv("OPEN_AI_KEY", None)
        #환경 변수 방어 코드
        if key is None:
            print("환경 변수 방어 코드 작동")
            config.read('conf/config.ini')
            key = config['OPENAI']['key']
        self.openai.api_key = key

    def get_analysis_result(self, actual_data, predictd_data):
        print("come here")
        prompt = ("Here is the actual price data.\n" + actual_data + "\n" + "Here is the predicted price data.\n" + predictd_data + "\n\n"
        + "Compare the two tables and analyze whether the predicted price table accurately captures the trend of the actual price table. Please stop using the opening and ending comments! Just answer me.")
        res = ""

        if prompt != "":
            messages.append({"role": "user", "content": prompt})
            completion = self.openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            #print(completion)
            res = completion.choices[0].message['content']
            #res = completion.choices[0].message['content'].replace("\n", "<br/>").replace(" "," &nbsp;" )
            messages.append({"role": 'assistant', "content": res}  )
            #print(res)
        
        return res