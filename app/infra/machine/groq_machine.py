from groq import Groq
import configparser
import os

class GroqMachine:

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('app/conf/config.ini')
        key = os.getenv("GROQ_KEY", None)

        self.model = config['GROQ']['model']
        self.client = Groq(
            api_key=key
        )

    def get_prompt_format(self):
        formatted_prompt = """
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        너는 비트코인의 예측 가격과 실제 가격을 가지고 분석해주는 AI 분석 도우미야.
        <|eot_id|>
        
        <|start_header_id|>user<|end_header_id|>
        다음은 예측 가격들이야. {predicted_data}
        다음은 실제 가격들이야. {actual_data}
        
        예측 가격이 실제 가격의 추세를 잘 따라가고 있는지 확인해줘.
        
        모든 대답은 한글로해줘.
        <|eot_id|>
        
        <|start_header_id|>assistant<|end_header_id|>
        """

        return formatted_prompt


    def get_analysis_result(self, actual_data, predicted_data):
        prompt = self.get_prompt_format()
        prompt = prompt.format(actual_data=str(actual_data), predicted_data=str(predicted_data))

        print(prompt)

        res = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model,
        )

        return res.choices[0].message.content