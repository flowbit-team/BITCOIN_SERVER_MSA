import sys
sys.path.append("C:\AGAPE\FLOW-BIT\projects\BITCOIN_SERVER_MSA")
import os
import json
from app.infra.AI.flowbit_machine import FlowbitMachine

class ModelController:
    def __init__(self):
        """
        가장 먼저 호출되는 메서드
        config.ini에서 정보를 읽어옴
        """
        with open('conf/config.json') as f:
            config = json.load(f)

        model_data = config['modelData']

        self.model_size = model_data["modelSize"]
        self.coin_name = model_data["coinName"]
        self.coin_currency = model_data["coinCurrency"]
        self.model_version = model_data["modelVersion"]
        self.file_name_extension = model_data["fileNameExtension"]
        self.model_type = model_data["modelType"]

        self.model_data_list = []
        
        for index in range(self.model_size):
            model_define_data = {
            "model_type" : None,
            "model_class" : None,
            "model_path" : None,
            "coin_currency" : None
            }
            model_name = self.coin_currency[index] + "_MODEL_" + self.model_version[index]+ "." + self.file_name_extension[index]

            real_path = os.path.abspath(__file__)[0:-20]+"/../models/" + model_name
            #print(os.path.abspath(__file__)[0:-20])
            if os.path.isfile(real_path):
                #print(real_path)
                model = FlowbitMachine(model_path=real_path)
            else:
                print("File does not exist:", real_path)
            
            model_define_data["model_path"] = real_path
            model_define_data["model_type"] = self.model_type[index]
            model_define_data["model_class"] = model
            model_define_data["coin_currency"] = self.coin_currency[index]

            self.model_data_list.append(model_define_data)
            #print(self.model_data_list)



    def get_model(self, model_index=0):
        return self.model_data_list[model_index]

    def get_model_list(self):
        return self.model_data_list