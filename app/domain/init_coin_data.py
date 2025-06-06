import json

from app.infra.machine.bithumb_machine import BithumbMachine
# from app.infra.machine.chatGPT_machine import ChatMachine
from app.domain.chart_machine import ChartMachine
from app.infra.db.mongodb.mongodb_handler import MongoDBHandler
from app.infra.AI.model_controller import ModelController
import datetime
from pytz import timezone
from app.infra.machine.groq_machine import GroqMachine
import requests
import re
import html

server_timezone = timezone('Asia/Seoul')

groqMachine = GroqMachine()
chartMachine = ChartMachine()
mongodbMachine = MongoDBHandler(mode="remote", db_name="BTC", collection_name="actual_data")
# groqMachine = GroqMachine()

with open('app/conf/config.json') as f:
    config = json.load(f)

def get_head_lines(coin_currency):

    currency_trans_data = config['currencyTrans']

    # API 엔드포인트 URL
    url = "https://api.flowbit.co.kr/board-service/api/v1/news"
    coin_currency_kor = next ((currency["kor"] for currency in currency_trans_data if currency["eng"] == coin_currency),
                              "No matching currency found.")

    # `pageable` 파라미터 설정
    params = {
        "page": 0,  # 페이지 번호 (0부터 시작)
        "size": 10,  # 한 페이지에 포함할 항목 개수
        "sort": ["ASC"],  # 정렬 기준 (날짜 내림차순)
        "searchword": "",
        "tag": coin_currency_kor
    }
    # params["tag"] = None

    # GET 요청 보내기
    response = requests.get(url, params=params)
    titles_string = [html.unescape(re.sub(r"<.*?>", "", item["title"])) for item in response.json()["data"]["content"]]

    titles = "\n".join(f"헤드라인{i + 1}) {title}" for i, title in enumerate(titles_string))
    return titles


def pre_data(data):
    result = []
    for entry in data:
        values = [entry[key] for key in entry.keys() if key != 'timestamp' and key != "_id"]
        result.append(values)
    return result

def init_code():
    print("start initializing")
    print("start prev data")
    chart_machine = ChartMachine()
    # chat_machine = ChatMachine()
    bithumbMachine = BithumbMachine()
    modelController = ModelController()


    #init agent data
    agent_data = config["agentData"]

    mongodbMachine.delete_items(condition="ALL", db="AI", collection="define_chart")
    mongodbMachine.delete_items(condition="ALL", db="AI", collection="define_r2_score")
    mongodbMachine.delete_items(condition="ALL", db="AI", collection="define_news_room")

    # print(agent_data)
    mongodbMachine.insert_item(
        data=agent_data,
        database_name="AI",
        collection_name="help"
    )

    # mongodbMachine.insert_items(
    #     datas=agent_data["defineR2Score"],
    #     database_name="AI",
    #     collection_name="help"
    # )
    #
    # mongodbMachine.insert_items(
    #     datas=agent_data["defineNewsRoom"],
    #     database_name="AI",
    #     collection_name="help"
    # )

    for model_data in modelController.get_model_list():

        if model_data.get("model_type") != "prev":
            continue

        print(model_data.get("model_type"))
        print(model_data.get("coin_currency"))

        flowbitMachine = model_data.get("model_class")
        database_name = model_data.get("coin_currency")
        # mongodbMachine = MongoDBHandler(mode="remote", db_name=database_name, collection_name="actual_data")

        print("start reset database")
        mongodbMachine.delete_items(condition="ALL", db=database_name, collection="actual_data")
        mongodbMachine.delete_items(condition="ALL", db=database_name, collection="predicted_data")
        mongodbMachine.delete_items(condition="ALL", db=database_name, collection="analysis_data")
        print("end reset database")

        print("insert all actual data to database")
        datas = bithumbMachine.get_all_data(coin_currency=database_name)[0:-1]
        mongodbMachine.insert_items(datas=datas, database_name=database_name, collection_name="actual_data")
    
        print("start price prediction")
        results = []
        for i in range(0, len(datas) - 14):
            chunk = datas[i:i+15]
            results.insert(0, chunk)
        results.reverse()
    
        for i in results:
            data = pre_data(i)
            data = flowbitMachine.data_processing(data)
            result = flowbitMachine.get_predict_value(data)
            one_day_data = {}
            date_string = i[-1]["timestamp"]
            date_format = "%Y-%m-%d"

            server_date = server_timezone.localize(datetime.datetime.strptime(date_string, date_format))
            one_day_later = (server_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

            one_day_data["timestamp"] = one_day_later
            one_day_data["predicted_price"] = result + 0.0
            mongodbMachine.insert_item(data=one_day_data, database_name=database_name, collection_name="predicted_data")
        
        print("end price prediction")

        actual_data_str, predicted_data_str = chartMachine.get_analysis_chart()
        print(actual_data_str, predicted_data_str)
        # res = chat_machine.get_analysis_result(actual_data_str, predicted_data_str)
        print("start get LLM analysis")
        recommendation_res = groqMachine.get_recommendation_result(
            actual_data_str,
            predicted_data_str,
            database_name,
            get_head_lines(database_name))
        # print(res)
        print("end get LLM analysis")
        print("end price analysis")
        #
        recommendation_data = {"response": recommendation_res, "timestamp": datetime.date.today().strftime("%Y-%m-%d"), "current_price": database_name}
        #
        # print("insert analysis data to database")
        mongodbMachine.insert_item(data=recommendation_data, database_name="AI", collection_name="recommendation_data")
        # mongodbMachine.insert_item(data=recommendation_data, database_name="AI", collection_name="recommendation_data")

        analysis_res = groqMachine.get_analysis_result(actual_data_str, predicted_data_str, database_name)
        analysis_data = {"response": analysis_res, "timestamp": datetime.date.today().strftime("%Y-%m-%d"),"current_price": database_name}
        mongodbMachine.insert_item(data=analysis_data, database_name="AI",collection_name="analysis_data")


    
    for model_data in modelController.get_model_list():

        if model_data.get("model_type") != "pridict":
            continue

        print(model_data.get("model_type"))
        print(model_data.get("coin_currency"))

        flowbitMachine = model_data.get("model_class")
        database_name = model_data.get("coin_currency")
        # mongodbMachine = MongoDBHandler(mode="remote", db_name=database_name, collection_name="actual_data")

        datas = bithumbMachine.get_all_data(coin_currency=database_name)
        time_step = 60

        data = datas[-time_step:]
        
        print("start price prediction")

        
        date_string = data[-2]["timestamp"]
        data = pre_data(data)
        data = flowbitMachine.data_processing(data)
        result = flowbitMachine.get_predict_value_for_list(data)
        result_data_size = len(result)
        
        date_format = "%Y-%m-%d"

        server_date = server_timezone.localize(datetime.datetime.strptime(date_string, date_format))
        print(server_date)
        result_data = []

        for index in range(result_data_size):

            if index == 0:
                continue

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