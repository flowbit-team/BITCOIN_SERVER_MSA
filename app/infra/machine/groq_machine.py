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

    def get_recommendation_prompt_format(self):

        gemma_prompt = (
                "<start_of_turn>user" +
                "너는 가상화폐의 예측 가격과 실제 가격을 가지고 분석해주는 AI 분석 도우미야. 가상화폐 종합정보 사이트를 이용하는 유저에게 분석내용을 공유해줘" +
                "내가 너에게 예측 가격과 실제 가격에 대한 데이터와 오늘의 뉴스 헤드라인을 줄거야. 이 정보를 사용해 아래의 두 개의 질문에 대답해줘." +
                "1. 뉴스를 통한 비트코인 동향 분석" +
                "2. 1과 2의 의견을 종합적으로 정리하여 사용자에게 매도 추천, 매수 추천, 보류 추천 중 하나를 골라 안내" +
                "대답은 한국어로만 작성해줘. 데이터는 아래와 같아." +
                "이번에 분석할 코인의 종류는 {coin_currency}야." +
                "다음은 예측 가격들이야. {predicted_data}" +
                "다음은 실제 가격들이야. {actual_data}" +
                "헤드라인 데이터는 다음과 같아" +
                "{head_lines}" +
                "<end_of_turn>" +
                "<start_of_turn>model"
        )
        return gemma_prompt

    def get_analysis_prompt_format(self):

        gemma_prompt = (
                "<start_of_turn>user" +
                "너는 가상화폐의 예측 가격과 실제 가격을 분석하여 유저에게 이를 쉽게 풀어 설명해주는 AI 차트 해석 도우미야. 가상화폐 실제 가격과 예측 가격을 보고 이를 유저가 알기 쉽게 여러 지표를 사용하여 해석해줘" +
                "내가 너에게 예측 가격과 실제 가격에 대한 데이터를 줄거야. 이 정보를 사용해 유저의 차트 해석을 도와줘." +
                "대답은 한국어로만 작성해줘. 데이터는 아래와 같아." +
                "이번에 분석할 코인의 종류는 {coin_currency}야." +
                "다음은 예측 가격들이야. {predicted_data}" +
                "다음은 실제 가격들이야. {actual_data}" +
                "<end_of_turn>" +
                "<start_of_turn>model"
        )
        return gemma_prompt


    def get_recommendation_result(self, actual_data, predicted_data, coin_currency, head_lines):
        prompt = self.get_recommendation_prompt_format()
        prompt = prompt.format(
            actual_data=str(actual_data),
            predicted_data=str(predicted_data),
            coin_currency=coin_currency,
            head_lines=head_lines
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

    def get_analysis_result(self, actual_data, predicted_data, coin_currency):
        prompt = self.get_analysis_prompt_format()
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