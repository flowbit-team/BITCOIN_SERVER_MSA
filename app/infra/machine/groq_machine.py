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
        너는 가상화폐의 예측 가격과 실제 가격을 가지고 분석해주는 AI 분석 도우미야.
        <|eot_id|>
        
        <|start_header_id|>user<|end_header_id|>
        이번에 분석할 코인의 종류는 {coin_currency}야.
        다음은 예측 가격들이야. {predicted_data}
        다음은 실제 가격들이야. {actual_data}
        
        예측 가격이 실제 가격의 추세를 잘 파악하고 있는지를 분석해줘.

        답변형식은 다음과 같이 해줘

        (인사말)

        (MAE 분석 내용)

        (Correlation Coefficient 분석 내용)

        (종합 의견)

        대답은 한국어로만 작성해줘.

        모든 대답은 한글로해줘.
        <|eot_id|>
        
        <|start_header_id|>assistant<|end_header_id|>
        """

        gemma_prompt = """
        <start_of_turn>user
        너는 가상화폐의 예측 가격과 실제 가격을 가지고 분석해주는 AI 분석 도우미야. 가상화폐 종합정보 사이트를 이용하는 유저에게 분석내용을 공유해줘
        이번에 분석할 코인의 종류는 {coin_currency}야.
        다음은 예측 가격들이야. {predicted_data}
        다음은 실제 가격들이야. {actual_data}

        예측 가격이 실제 가격의 추세를 잘 파악하고 있는지를 분석해줘.

        대답은 한국어로만 작성해줘.<end_of_turn>
        <start_of_turn>model
        """

        return gemma_prompt


    def get_analysis_result(self, actual_data, predicted_data, coin_currency):
        prompt = self.get_prompt_format()
        prompt = prompt.format(
            actual_data=str(actual_data),
            predicted_data=str(predicted_data),
            coin_currency=coin_currency
        )

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