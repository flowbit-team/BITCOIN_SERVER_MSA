from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import sys
import os
import numpy as np
import json

class FlowbitMachine:
    def __init__(self, model_path):
        """
        가장 먼저 호출되는 메서드
        config.ini에서 정보를 읽어옴
        """

        self.model = load_model(model_path, compile=False)

        self.scalerOne = MinMaxScaler(feature_range=(0, 1))
        self.scalerMul = MinMaxScaler(feature_range=(0, 1))

    def get_model(self):
        return self.model

    def get_predict_value(self, current_data):
        """
        모델을 불러와서 학습을 진행하고 결과값을 return
        """
        predicted_value = self.model.predict(current_data)
        predicted_value = self.scalerOne.inverse_transform(predicted_value)

        return predicted_value[0][0]
    
    def get_predict_value_for_list(self, current_data):
        """
        모델을 불러와서 학습을 진행하고 결과값을 return
        """
        predicted_value = self.model.predict(current_data)
        predicted_value = self.scalerOne.inverse_transform(predicted_value)

        print(predicted_value)

        return predicted_value[0]

    def data_processing(self, raw_data):
        """
        학습을 위한 전처리 진행
        """

        final_data = [raw_data]
        final_close_data =  [entry[1] for entry in raw_data]

        final_data = self.scalerMul.fit_transform(
            raw_data
        )
        final_close_data = self.scalerOne.fit_transform(
            np.array(final_close_data).reshape(-1, 1)
        )
        final_data = [final_data.tolist()]

        return final_data