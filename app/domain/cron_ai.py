import sys
import os

from app.infra.AI.model_controller import ModelController

sys.path.append(os.path.realpath(__file__)[0:-18]+"..")
from app.infra.machine.bithumb_machine import BithumbMachine
from app.domain.chart_machine import ChartMachine
from app.infra.db.mongodb.mongodb_handler import MongoDBHandler
from app.infra.machine.chatGPT_machine import ChatMachine
import datetime
from pytz import timezone

server_timezone = timezone('Asia/Seoul')

def data_processing(data):
    ret = []
    for i in data:
        ret.append(list(i.values())[2:])
    return ret

def pre_data(data):
    result = []
    for entry in data:
        values = [entry[key] for key in entry.keys() if key != 'timestamp' and key != "_id"]
        result.append(values)
    return result

def save_one_day_data():
    print("start cron method")

    bithumbMachine = BithumbMachine()
    modelController = ModelController()
    for model_data in modelController.get_model_list():
        if model_data.get("model_type") != "prev":
            continue

        flowbitMachine = model_data.get("model_class")
        database_name = model_data.get("coin_currency")
        mongodbMachine = MongoDBHandler(mode="remote", db_name=database_name, collection_name="actual_data")

        print("insert last actual data to database")
        data = bithumbMachine.get_last_data(coin_currency=database_name)
        mongodbMachine.insert_item(data=data, database_name=database_name, collection_name="actual_data")
    
        print("start price prediction")
        past_data = mongodbMachine.find_items_for_db(db_name=database_name, collection_name="actual_data")
        data = data_processing(past_data)
        data.reverse()

        data = flowbitMachine.data_processing(data)
        result = flowbitMachine.get_predict_value(data)

        one_day_data = {}
        one_day_data["timestamp"] = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        one_day_data["predicted_price"] = result + 0.0
        print("end price prediction")

        print("insert predicted data to database")
        mongodbMachine.insert_item(data=one_day_data, database_name=database_name, collection_name="predicted_data")

        # print("start price analysis")
        # chart_machine = ChartMachine()
        # chat_machine = ChatMachine()
        #
        # actual_data_str, predicted_data_str = chart_machine.get_analysis_chart()
        # # print(actual_data_str, predicted_data_str)
        # res = chat_machine.get_analysis_result(actual_data_str, predicted_data_str)
        # print("end price analysis")
        #
        # analysis_data = {"gpt_response":res, "timestamp":datetime.date.today().strftime("%Y-%m-%d")}
        #
        # print("insert analysis data to database")
        # mongodbMachine.insert_item(data = analysis_data, database_name=database_name, collection_name="analysis_data")

    #todo: one day ai 부분 객체로 바꾸기
    for model_data in modelController.get_model_list():

        #flowbitMachine = FlowbitMachine()
        if model_data.get("model_type") != "pridict":
            continue

        print(model_data.get("model_type"))
        print(model_data.get("coin_currency"))

        flowbitMachine = model_data.get("model_class")
        database_name = model_data.get("coin_currency")
        mongodbMachine = MongoDBHandler(mode="remote", db_name=database_name, collection_name="actual_data")

        #print("start reset database")
        #mongodbMachine.delete_items(condition="ALL", db=database_name, collection="actual_data")
        #mongodbMachine.delete_items(condition="ALL", db=database_name, collection="predicted_data")
        #mongodbMachine.delete_items(condition="ALL", db=database_name, collection="analysis_data")
        #print("end reset database")

        #print("insert all actual data to database")
        #datas = bithumbMachine.get_all_data(coin_currency=database_name)[:-1]
        #mongodbMachine.insert_items(datas=datas, database_name=database_name, collection_name="actual_data")

        datas = bithumbMachine.get_all_data(coin_currency=database_name)[:-1]
        time_step = 60

        data = datas[-time_step:]
        
        print("start price prediction")

        
        date_string = data[-1]["timestamp"]
        data = pre_data(data)
        data = flowbitMachine.data_processing(data)
        result = flowbitMachine.get_predict_value_for_list(data)
        result_data_size = len(result)
        
        date_format = "%Y-%m-%d"

        server_date = server_timezone.localize(datetime.datetime.strptime(date_string, date_format))
        print(server_date)
        one_day_later = (server_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        result_data = []
        predicted_price_list =[int(x) for x in  result.tolist()]

        for index in range(result_data_size):
            one_day_data = {}

            price = result[index]
            date = (server_date + datetime.timedelta(days=(index + 1))).strftime("%Y-%m-%d")
            
            one_day_data["timestamp"] = date
            one_day_data["predicted_price"] = int(price)

            result_data.append(one_day_data)
        
        print(result_data)
        db_data = {}
        db_data["predicted_data"] = result_data

        mongodbMachine.insert_item(data=db_data, database_name=database_name, collection_name="multiple_predicted_data")